import sqlite3
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
    

    def get_requirement_by_specification(self, specification) -> List[Dict]:
        """
        Fetch requirements for a given spec_name and spec_version.
        """
        self.cursor.execute(
            'SELECT * FROM requirements WHERE spec_name=? AND spec_version=?', 
            (specification['name'], specification['version'])
        )
        return self.cursor.fetchall()

    def get_requirement_by_number(self, requirement_number):
        """
        Retrieve a specific requirement by its number.
        """
        self.cursor.execute('SELECT * FROM requirements WHERE requirement_number = ?', (requirement_number,))
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
        Retrieve all specifications from the database.
        """
        self.cursor.execute('SELECT * FROM specifications')
        return self.cursor.fetchall()

    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()