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
import pandas as pd


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Load a medium German model
nlp = spacy.load('de_core_news_md')

# Define the database connection
conn = sqlite3.connect('requirements.db')
cursor = conn.cursor()

# Drop the existing table to reset our database for this example
cursor.execute('DROP TABLE IF EXISTS requirements')

# Create the table with two new columns for processed text
cursor.execute('''
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



# Make sure to download the stopwords and wordnet datasets if you haven't already
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove whitespaces
    text = text.strip()
    
    # Remove stop words
    stop_words = set(stopwords.words('german'))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    
    # Stemming or Lemmatization (optional, depending on the use case)
    # For German, you would use the SnowballStemmer
    stemmer = SnowballStemmer('german')
    words = [stemmer.stem(word) for word in words]
    
    # Rejoin words
    text = ' '.join(words)
    
    return text

# Function to parse CSV and insert data into the database
def import_csv_to_db(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        total_entries = 0

        for row in reader:
            # Preprocess 'title' and 'description'
            processed_title = preprocess_text(row.get('Titel', ''))
            processed_description = preprocess_text(row.get('Beschreibung', ''))
            
            # Insert data into the database, including processed texts
            try:
                cursor.execute('''
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

        conn.commit()
        logging.info(f"Total number of entries added from {csv_file_path}: {total_entries}")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def fetch_requirements_by_context(connection, context):
    # Set the row factory to the dict_factory function for dictionary-like cursor
    connection.row_factory = dict_factory
    # Now, create a new cursor object using the new row_factory setting
    cursor.execute("SELECT * FROM requirements WHERE context=?", (context,))
    return cursor.fetchall()


def create_comparison_table():
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
        similarity_score REAL
    )
    ''')
    conn.commit()

# Add the comparison function
def compare_requirements(cursor):
    # Ensure the comparison table exists
    create_comparison_table()

    # Fetch the requirements for ePA and eRp
    epa_requirements = fetch_requirements_by_context(cursor, 'ePA')
    erp_requirements = fetch_requirements_by_context(cursor, 'eRp')

    # Loop through each ePA requirement and compare with each eRp requirement
    for i, epa in enumerate(epa_requirements):
        for erp in erp_requirements:
            # Compare the processed titles
            title_similarity = calculate_similarity(epa['processed_title'], erp['processed_title'])
            # Compare the processed descriptions
            description_similarity = calculate_similarity(epa['processed_description'], erp['processed_description'])

            # Store the higher of the two similarity scores
            similarity_score = max(title_similarity, description_similarity)

            # Only store requirements with a high degree of similarity
            if similarity_score > 0.75:  # This threshold can be adjusted
                combined_identifier = f"{epa['requirement_number']}_{erp['requirement_number']}"
                cursor.execute('''
                INSERT INTO requirement_similarities (
                    combined_identifier, comparison_method, epa_requirement_number, erp_requirement_number,
                    epa_title, erp_title, epa_description, erp_description, similarity_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    combined_identifier, 'cosine_similarity', epa['requirement_number'], erp['requirement_number'],
                    epa['title'], erp['title'], epa['description'], erp['description'], similarity_score
                ))

        # Log progress every 10 comparisons
        if (i+1) % 10 == 0:
            logging.info(f"Progress: Compared {i+1} ePA requirements.")

    conn.commit()

# Function to calculate similarity
def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]
    

def fetch_sample_data(cursor, table_name, sample_size=5):
    # Execute the SELECT query
    cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (sample_size,))
    
    # Fetch the results
    rows = cursor.fetchall()
    
    # Print out the sample data
    for row in rows:
        print(row)

try:
    import_csv_to_db('data/epa_afos.csv')
    import_csv_to_db('data/erp_afos.csv')

    compare_requirements(cursor)
    fetch_sample_data(cursor, 'requirement_similarities', 100)
except Exception as e:
    logging.error("An error occurred:", exc_info=True)
finally:
    conn.close()