class RequirementComparer:
    def __init__(self, db_connection, overwrite):
        self.db_connection = db_connection
        self._setup(overwrite)

    def _setup(self, overwrite):
        cursor = self.db_connection.cursor()
        if overwrite:
            self.cursor.execute('DROP TABLE IF EXISTS requirement_similarities')
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
    
    def compare_requirements_jaccard(self):
        try:
            epa_requirements = self._fetch_requirements('ePA')
            erp_requirements = self._fetch_requirements('eRP')
            
            for epa_req in epa_requirements:
                for erp_req in erp_requirements:
                    title_similarity = self._calculate_jaccard_similarity(epa_req['processed_title'], erp_req['processed_title'])
                    description_similarity = self._calculate_jaccard_similarity(epa_req['processed_description'], erp_req['processed_description'])
                    
                    if title_similarity > 0.6 or description_similarity > 0.6:
                        self._store_jaccard_similarity(epa_req, erp_req, title_similarity, description_similarity)
        
        except sqlite3.DatabaseError as e:
            print(f"An error occurred during database operations: {e}")
        finally:
            self.db_connection.commit()

    def _calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard Similarity between two strings."""
        set1 = set(text1.split())
        set2 = set(text2.split())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union) if union else 0

    def _store_jaccard_similarity(self, epa: Dict, erp: Dict, title_similarity: float, description_similarity: float):
        """Store the similarity results in the requirement_similarities table."""
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
                combined_identifier, 'jaccard_similarity', epa['requirement_number'], erp['requirement_number'],
                epa['title'], erp['title'], epa['description'], erp['description'], title_similarity, description_similarity
            ))
        except sqlite3.IntegrityError:
            print(f"Entry with combined_identifier {combined_identifier} already exists.")

    # Other methods like _setup, compare_requirements, _fetch_requirements, etc.


class CosineRequirementComparer:
    def __init__(self, db_connection, overwrite):
        self.db_connection = db_connection
        self._setup(overwrite)

    def _setup(self, overwrite):
        cursor = self.db_connection.cursor()
        if overwrite:
            self.cursor.execute('DROP TABLE IF EXISTS requirement_similarities')
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

    def compare_requirements(self):
        epa_requirements = self._fetch_requirements('ePA')
        erp_requirements = self._fetch_requirements('eRp')

        for i, epa in enumerate(epa_requirements):
            for erp in erp_requirements:
                # Calculate similarities separately
                title_similarity = self._calculate_similarity(epa['processed_title'], erp['processed_title'])
                description_similarity = self._calculate_similarity(epa['processed_description'], erp['processed_description'])
                
                # Check if either similarity is above the threshold
                if title_similarity > 0.75 or description_similarity > 0.75:
                    self._store_similarity(epa, erp, title_similarity, description_similarity)
            if (i + 1) % 10 == 0:
                logging.info(f"Progress: Compared {i + 1} ePA requirements.")

        self.db_connection.commit()
    
    def _fetch_requirements(self, context):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM requirements WHERE context=?", (context,))
        return cursor.fetchall()

    def _store_similarity(self, epa, erp, title_similarity, description_similarity):
        combined_identifier = f"{epa['requirement_number']}_{erp['requirement_number']}"
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO requirement_similarities (
                combined_identifier, comparison_method, epa_requirement_number, erp_requirement_number,
                epa_title, erp_title, epa_description, erp_description, title_similarity_score, description_similarity_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            combined_identifier, 'cosine_similarity', epa['requirement_number'], erp['requirement_number'],
            epa['title'], erp['title'], epa['description'], erp['description'], title_similarity, description_similarity
        ))

    @staticmethod
    def _calculate_similarity(text1, text2):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]
    def fetch_sample_data(self, table_name, sample_size=5):
        cursor = self.db_connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (sample_size,))
        return cursor.fetchall()