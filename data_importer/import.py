import csv
import sqlite3
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import spacy
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
from typing import List, Dict
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RequirementProcessor:
    def __init__(self, db_path, overwrite=True):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = self.dict_factory
        self.cursor = self.conn.cursor()
        self._configure_database(overwrite)
        self.nlp = spacy.load('de_core_news_md')
        nltk.download('stopwords')
        nltk.download('wordnet')

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _configure_database(self, overwrite):
        if overwrite:
            self.cursor.execute('DROP TABLE IF EXISTS requirements')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirements (
                context TEXT,
                source TEXT,
                requirement_number TEXT,
                title TEXT,
                description TEXT,
                processed_title TEXT,
                processed_description TEXT,
                obligation TEXT,
                test_procedure TEXT,
                theme TEXT,
                focus TEXT
            )
        ''')
        self.conn.commit()

    @staticmethod
    def preprocess_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        text = text.strip()
        stop_words = set(stopwords.words('german'))
        words = text.split()
        words = [word for word in words if word not in stop_words]
        stemmer = SnowballStemmer('german')
        words = [stemmer.stem(word) for word in words]
        return ' '.join(words)

    def import_csv_to_db(self, csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            total_entries = 0
            for row in reader:
                processed_title = self.preprocess_text(row.get('Titel', ''))
                processed_description = self.preprocess_text(row.get('Beschreibung', ''))
                try:
                    self.cursor.execute('''
                        INSERT INTO requirements (
                            context, source, requirement_number, title, description,
                            processed_title, processed_description, obligation, test_procedure, theme, focus
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Kontext', ''),
                        row.get('Quelle', ''),
                        row.get('Anforderungs Nr.', ''),
                        row.get('Titel', ''),
                        row.get('Beschreibung', ''),
                        processed_title,
                        processed_description,
                        row.get('Verbindlichkeit', ''),
                        row.get('Pruefverfahren', ''),
                        row.get('Thema', ''),
                        row.get('Schwerpunkt', '')
                    ))
                    total_entries += 1
                except sqlite3.Error as e:
                    logging.error(f"Error inserting data into database: {e}")
                    continue

            self.conn.commit()
            logging.info(f"Total number of entries added from {csv_file_path}: {total_entries}")

    def close(self):
        self.conn.close()


class RequirementComparer(ABC):
    def __init__(self, db_connection, overwrite: bool = False):
        self.db_connection = db_connection
        self._setup(overwrite)

    def _setup(self, overwrite: bool):
        cursor = self.db_connection.cursor()
        if overwrite:
            cursor.execute('DROP TABLE IF EXISTS requirement_similarities')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirement_similarities (
                combined_identifier TEXT PRIMARY KEY,
                comparison_method TEXT,
                epa_requirement_number TEXT,
                erp_requirement_number TEXT,
                epa_title TEXT,
                erp_title TEXT,
                epa_description TEXT,
                erp_description TEXT,
                title_similarity_score REAL,
                description_similarity_score REAL
            )
        ''')
        self.db_connection.commit()

    def fetch_requirements(self, context: str) -> List[Dict]:
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM requirements WHERE context=?", (context,))
        return cursor.fetchall()

    def store_similarity(self, epa: Dict, erp: Dict, title_similarity: float, description_similarity: float):
        combined_identifier = f"{epa['requirement_number']}_{erp['requirement_number']}"
        cursor = self.db_connection.cursor()
        method = self.get_comparison_method()
        
        try:
            cursor.execute('''
                INSERT INTO requirement_similarities (
                    combined_identifier, comparison_method, epa_requirement_number, erp_requirement_number,
                    epa_title, erp_title, epa_description, erp_description, title_similarity_score, description_similarity_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                combined_identifier, method, epa['requirement_number'], erp['requirement_number'],
                epa['title'], erp['title'], epa['description'], erp['description'], title_similarity, description_similarity
            ))
        except sqlite3.IntegrityError:
            print(f"Entry with combined_identifier {combined_identifier} already exists.")
        self.db_connection.commit()

    def compare_requirements(self):
        epa_requirements = self.fetch_requirements('ePA')
        erp_requirements = self.fetch_requirements('eRp')
        for i, epa_req in enumerate(epa_requirements):
            for erp_req in erp_requirements:

                title_similarity = self.calculate_similarity(epa_req['processed_title'], erp_req['processed_title'])
                description_similarity = self.calculate_similarity(epa_req['processed_description'], erp_req['processed_description'])
                
                if self.is_above_threshold(title_similarity, description_similarity):
                    self.store_similarity(epa_req, erp_req, title_similarity, description_similarity)
            if (i + 1) % 10 == 0:
                logging.info(f"Progress: Compared {i + 1} ePA requirements.")

        self.db_connection.commit()

    @abstractmethod
    def calculate_similarity(self, text1: str, text2: str) -> float:
        pass

    @abstractmethod
    def get_comparison_method(self) -> str:
        pass

    @abstractmethod
    def is_above_threshold(self, title_similarity: float, description_similarity: float) -> bool:
        pass


class JaccardRequirementComparer(RequirementComparer):
    def calculate_similarity(self, text1: str, text2: str) -> float:
        set1 = set(text1.split())
        set2 = set(text2.split())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union) if union else 0

    def get_comparison_method(self) -> str:
        return 'jaccard_similarity'

    def is_above_threshold(self, title_similarity: float, description_similarity: float) -> bool:
        return title_similarity > 0.6 or description_similarity > 0.6


class CosineRequirementComparer(RequirementComparer):
    def calculate_similarity(self, text1: str, text2: str) -> float:
        # Assume TfidfVectorizer and cosine_similarity are imported
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]

    def get_comparison_method(self) -> str:
        return 'cosine_similarity'

    def is_above_threshold(self, title_similarity: float, description_similarity: float) -> bool:
        return title_similarity > 0.75 or description_similarity > 0.75


if __name__ == '__main__':
    try:
        processor = RequirementProcessor('../public/db/requirements2.db', True)
        processor.import_csv_to_db('data/epa_afos.csv')
        processor.import_csv_to_db('data/erp_afos.csv')
        cosine_comparer = CosineRequirementComparer(processor.conn, True)
        cosine_comparer.compare_requirements()
        jaccard_comparer = JaccardRequirementComparer(processor.conn, False)
        jaccard_comparer.compare_requirements()

       # comparer.fetch_sample_data('requirement_similarities', 100)
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
    finally:
        # This ensures that processor.close() is called only if processor is defined
        if 'processor' in locals():
            processor.close()
