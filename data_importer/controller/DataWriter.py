from typing import Dict, List
import sqlite3
from Specification import Specification


class DataWriter:
    def __init__(self, conn, overwrite) -> None:
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.conn.row_factory = self.dict_factory
        self.configure_database(overwrite)
        self.populate_static_data()

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def configure_database(self, overwrite):
        if overwrite:
            self.cursor.execute("DROP TABLE IF EXISTS requirements")
            self.cursor.execute("DROP TABLE IF EXISTS specifications")
            self.cursor.execute("DROP TABLE IF EXISTS categories")
            self.cursor.execute("DROP TABLE IF EXISTS types")
            self.cursor.execute("DROP TABLE IF EXISTS requirement_similarities")

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS types (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY,
                specification_id INTEGER,
                source TEXT,
                requirement_number TEXT,
                title TEXT,
                description TEXT,
                processed_title TEXT,
                processed_description TEXT,
                obligation TEXT,
                test_procedure TEXT,
                FOREIGN KEY(specification_id) REFERENCES specifications(id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS specifications (
                id INTEGER PRIMARY KEY,
                name TEXT,
                version TEXT,
                fullname TEXT,
                file_path TEXT,
                category_id INTEGER,
                type_id INTEGER,
                UNIQUE(name, version),
                FOREIGN KEY(category_id) REFERENCES categories(id),
                FOREIGN KEY(type_id) REFERENCES types(id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS requirement_similarities (
                combined_identifier TEXT PRIMARY KEY,
                spec1_id INTEGER,
                spec2_id INTEGER,
                spec1_requirement_number TEXT,
                spec2_requirement_number TEXT,
                spec1_title TEXT,
                spec2_title TEXT,
                spec1_description TEXT,
                spec2_description TEXT,
                spec1_source TEXT,
                spec2_source TEXT,
                spec1_obligation TEXT,
                spec2_obligation TEXT,
                spec1_test_procedure TEXT,
                spec2_test_procedure TEXT,
                title_similarity_score REAL,
                description_similarity_score REAL,
                comparison_method TEXT,
                FOREIGN KEY(spec1_id) REFERENCES specifications(id),
                FOREIGN KEY(spec2_id) REFERENCES specifications(id)
            )
        """
        )
        self.conn.commit()

    def populate_static_data(self):
        static_data = [
            ('Konzepte', 'Spezifikationsdokumente'),
            ('Systemlösung', 'Spezifikationsdokumente'),
            ('Spezifikationen', 'Spezifikationsdokumente'),
            ('Feature-Spezifikationen', 'Spezifikationsdokumente'),
            ('Richtlinien', 'Spezifikationsdokumente'),
            ('Produkttyp Steckbriefe', 'Steckbriefe'),
            ('Anbietertyp Steckbriefe', 'Steckbriefe'),
            ('Anwendungssteckbrief', 'Steckbriefe'),
            ('Verzeichnis', 'Steckbriefe'),
            ('Unbekannt', 'Unbekannt')
        ]

        for type_name, category_name in static_data:
            self.insert_category(category_name)
            self.insert_type(type_name)

    def insert_category(self, name):
        self.cursor.execute(
            """
            INSERT INTO categories (name)
            VALUES (?)
            ON CONFLICT(name) DO NOTHING
            """, (name,)
        )
        self.conn.commit()

    def insert_type(self, name):
        self.cursor.execute(
            """
            INSERT INTO types (name)
            VALUES (?)
            ON CONFLICT(name) DO NOTHING
            """, (name,)
        )
        self.conn.commit()

    def get_or_create_specification(self, parsed_file):
        # Get or create the category_id from the database
        category_id = self.get_or_create_category_id(parsed_file.category_type)
        # Get or create the type_id from the database
        type_id = self.get_or_create_type_id(parsed_file.spec_type)

        # Insert the specification if it does not exist, using the IDs for category and type
        self.cursor.execute(
            """
            INSERT INTO specifications (name, version, fullname, file_path, category_id, type_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                parsed_file.spec_name,
                parsed_file.spec_version,
                parsed_file.filename,
                parsed_file.file_path,
                category_id,
                type_id
            ),
        )
        self.conn.commit()

        # Retrieve the specification ID
        self.cursor.execute(
            """
            SELECT id FROM specifications
            WHERE name = ? AND version = ?
            """,
            (parsed_file.spec_name, parsed_file.spec_version),
        )
        spec_id = self.cursor.fetchone()
        if spec_id:
            spec_id = spec_id[0]
        else:
            raise Exception(
                f"Specification {parsed_file.spec_name} v{parsed_file.spec_version} could not be retrieved or added to the database."
            )

        spec = Specification(
            spec_id,
            parsed_file.spec_name,
            parsed_file.spec_version,
            parsed_file.filename,
            parsed_file.file_path,
            [],
        )

        return spec
    
    def get_or_create_category_id(self, category_name):
        # First, try to get the category ID from the database
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            # If the category does not exist, insert it and then return the new ID
            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            self.conn.commit()
            return self.cursor.lastrowid

    # This function should be within the DataWriter class
    def get_or_create_type_id(self, type_name):
        # First, try to get the type ID from the database
        self.cursor.execute("SELECT id FROM types WHERE name = ?", (type_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            # If the type does not exist, insert it and then return the new ID
            self.cursor.execute("INSERT INTO types (name) VALUES (?)", (type_name,))
            self.conn.commit()
            return self.cursor.lastrowid

    def add_requirement(self, requirement):
        self.cursor.execute(
            """
                    INSERT INTO requirements (
                        specification_id, source, requirement_number, title, description,
                        processed_title, processed_description, obligation, test_procedure
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                requirement.specification_id,
                requirement.source,
                requirement.requirement_number,
                requirement.title,
                requirement.description,
                requirement.processed_title,
                requirement.processed_description,
                requirement.obligation,
                requirement.test_procedure,
            ),
        )


    def add_requirement_similarities(
        self,
        spec1: Dict,
        spec2: Dict,
        method,
        title_similarity: float,
        description_similarity: float,
    ):
        combined_identifier = f"{spec1['name']}_{spec1['version']}_{spec1['requirement_number']}_{spec1['name']}_{spec1['version']}_{spec2['requirement_number']}"

        try:
            self.cursor.execute(
                """
                INSERT INTO requirement_similarities (
                    combined_identifier, 
                    spec1_id, 
                    spec2_id,
                    spec1_requirement_number, spec2_requirement_number,
                    spec1_title, spec2_title, 
                    spec1_description, spec2_description, 
                    spec1_source, spec2_source, 
                    spec1_obligation, spec2_obligation, 
                    spec1_test_procedure, spec2_test_procedure,
                    title_similarity_score, description_similarity_score, 
                    comparison_method
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    combined_identifier,
                    spec1["specification_id"],  
                    spec2["specification_id"],
                    spec1["requirement_number"],
                    spec2["requirement_number"],
                    spec1["title"],
                    spec2["title"],
                    spec1["description"],
                    spec2["description"],
                    spec1.get("source", "unknown"),
                    spec2.get("source", "unknown"),
                    spec1.get("obligation", "unknown"),
                    spec2.get("obligation", "unknown"),
                    spec1.get("test_procedure", "unknown"),
                    spec2.get("test_procedure", "unknown"),
                    title_similarity,
                    description_similarity,
                    method,
                ),
            )
        except sqlite3.IntegrityError as e:
            print(
                f"Entry with combined_identifier {combined_identifier} already exists. Error: {e}"
            )
        self.conn.commit()

    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()
