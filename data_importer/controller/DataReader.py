from typing import Dict, List


class DataReader:
    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = self.dict_factory
        self.cursor = self.conn.cursor()

    def dict_factory(self, cursor, row):
        """
        Create a dictionary from rows in a cursor result.
        The keys will correspond to the column names.
        """
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def get_all_requirements(self):
        """
        Retrieve all requirements from the database.
        """
        self.cursor.execute('SELECT * FROM requirements')
        return self.cursor.fetchall()
    
    def get_requirements_by_specification(self, specification) -> List[Dict]:
        """
        Fetch requirements for a given spec_name and spec_version.
        """
        self.cursor.execute(
            '''
            SELECT r.*, s.name, s.version, s.fullname, s.file_path 
            FROM requirements r 
            JOIN specifications s ON r.specification_id = s.id 
            WHERE s.id=? 
            ''', 
            (specification['id'],)
        )
        return self.cursor.fetchall()

    def get_requirement_by_number(self, requirement_number):
        """
        Retrieve a specific requirement by its number.
        """
        self.cursor.execute(
            '''
            SELECT r.*, s.name, s.version, s.fullname, s.file_path 
            FROM requirements r 
            JOIN specifications s ON r.specification_id = s.id 
            WHERE r.requirement_number = ? 
            ''', 
            (requirement_number,)
        )
        return self.cursor.fetchone()

    def search_requirements(self, search_query):
        """
        Search for requirements that match a search query in their title or description.
        """
        search_query = f'%{search_query}%'
        self.cursor.execute('SELECT * FROM requirements WHERE title LIKE ? OR description LIKE ?', (search_query, search_query))
        return self.cursor.fetchall()
    
    def get_all_specifications(self):
        """
        Retrieve all specifications from the database along with the count of associated requirements,
        including the type, category, and their respective IDs.
        """
        self.cursor.execute(
            '''
            SELECT s.*, t.name AS type, c.name AS category, t.id AS type_id, c.id AS category_id, COUNT(r.specification_id) as requirement_count
            FROM specifications s
            LEFT JOIN requirements r ON s.id = r.specification_id
            LEFT JOIN spec_types t ON s.type_id = t.id
            LEFT JOIN spec_categories c ON s.category_id = c.id
            GROUP BY s.id
            '''
        )
        return self.cursor.fetchall()

    
    def get_similarity_counts(self):
        """
        Retrieve the count of similar requirements between each pair of specifications.
        """
        self.cursor.execute(
            '''
           SELECT 
                r1.specification_id AS spec1_id, 
                r2.specification_id AS spec2_id, 
                s1.name AS spec1_name, 
                s1.version AS spec1_version, 
                s2.name AS spec2_name, 
                s2.version AS spec2_version, 
                COUNT(*) AS similarity_count
            FROM 
                requirement_similarities rs
            JOIN 
                requirements r1 ON rs.requirement1_id = r1.id
            JOIN 
                requirements r2 ON rs.requirement2_id = r2.id
            JOIN 
                specifications s1 ON r1.specification_id = s1.id
            JOIN 
                specifications s2 ON r2.specification_id = s2.id
            GROUP BY 
                r1.specification_id, r2.specification_id;

            '''
        )
        return self.cursor.fetchall()


    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()