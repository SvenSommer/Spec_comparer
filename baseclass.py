class BaseRequirementComparer:
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

    def store_similarity(self, epa: Dict, erp: Dict, title_similarity: float, description_similarity: float, method: str):
        combined_identifier = f"{epa['requirement_number']}_{erp['requirement_number']}"
        cursor = self.db_connection.cursor()
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
            logging.warning(f"Entry with combined_identifier {combined_identifier} already exists.")
        self.db_connection.commit()

    def calculate_similarity(self, text1: str, text2: str, method: str) -> float:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def compare_requirements(self, similarity_threshold: float, method: str):
        epa_requirements = self.fetch_requirements('ePA')
        erp_requirements = self.fetch_requirements('eRP')

        for i, epa_req in enumerate(epa_requirements):
            for erp_req in erp_requirements:
                title_similarity = self.calculate_similarity(epa_req['processed_title'], erp_req['processed_title'], method)
                description_similarity = self.calculate_similarity(epa_req['processed_description'], erp_req['processed_description'], method)

                if title_similarity > similarity_threshold or description_similarity > similarity_threshold:
                    self.store_similarity(epa_req, erp_req, title_similarity, description_similarity, method)

            if (i + 1) % 10 == 0:
                logging.info(f"Progress: Compared {i + 1} ePA requirements with {method}")


class JaccardRequirementComparer(BaseRequirementComparer):
    def calculate_similarity(self, text1: str, text2: str, method: str) -> float:
        set1 = set(text1.split())
        set2 = set(text2.split())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union) if union else 0


class CosineRequirementComparer(BaseRequirementComparer):
    @staticmethod
    def _calculate_cosine_similarity(text1: str, text2: str) -> float:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]

    def calculate_similarity(self, text1: str, text2: str, method: str) -> float:
        return self._calculate_cosine_similarity(text1, text2)


