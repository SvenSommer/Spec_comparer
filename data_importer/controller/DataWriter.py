from typing import Dict, List
import sqlite3
from Specification import Specification

class DataWriter:
    def __init__(self, conn, overwrite) -> None:
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.conn.row_factory = self.dict_factory
        self.configure_database(overwrite)

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def configure_database(self, overwrite):
        if overwrite:
            self.cursor.execute("DROP TABLE IF EXISTS requirements")
            self.cursor.execute("DROP TABLE IF EXISTS specifications")
            self.cursor.execute("DROP TABLE IF EXISTS requirement_similarities")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS requirements (
                spec_name TEXT,
                spec_version TEXT,            
                source TEXT,
                requirement_number TEXT,
                title TEXT,
                description TEXT,
                processed_title TEXT,
                processed_description TEXT,
                obligation TEXT,
                test_procedure TEXT
               
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE specifications (
                id INTEGER PRIMARY KEY,
                name TEXT,
                version TEXT,
                fullname TEXT,
                file_path TEXT,
                UNIQUE(name, version)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS requirement_similarities (
                combined_identifier TEXT PRIMARY KEY,
                spec_name TEXT,
                spec1_version TEXT,       
                spec2 TEXT,
                spec2_version TEXT,       
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
                comparison_method TEXT
            )
        """
        )
        self.conn.commit()

    def get_or_create_specification(self, parsed_file):
        # Einfügen der Spezifikation, falls sie noch nicht existiert
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO specifications (name, version, fullname, file_path)
            VALUES (?, ?, ?,?)
            """,
            (parsed_file.spec_name, parsed_file.spec_version, parsed_file.filename, parsed_file.file_path),
        )
        self.conn.commit()

        # Abrufen der Spezifikations-ID
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
            raise Exception(f"Specification {parsed_file.spec_name} v{parsed_file.spec_version} could not be retrieved or added to the database.")

        spec = Specification(spec_id, parsed_file.spec_name, parsed_file.spec_version, parsed_file.filename,parsed_file.file_path, [])

        return spec

    def add_requirement(self, requirement):
        self.cursor.execute(
            """
                    INSERT INTO requirements (
                        spec_name, spec_version, source, requirement_number, title, description,
                        processed_title, processed_description, obligation, test_procedure
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
            (
                requirement.spec_name,
                requirement.spec_version,
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
        combined_identifier = f"{spec1['spec_name']}_{spec1['spec_version']}_{spec2['spec_name']}_{spec2['spec_version']}_{spec1['requirement_number']}_{spec2['requirement_number']}"


        try:
            self.cursor.execute(
                """
                INSERT INTO requirement_similarities (
                    combined_identifier, 
                    spec_name, spec1_version, spec2, spec2_version,
                    spec1_requirement_number, spec2_requirement_number,
                    spec1_title, spec2_title, 
                    spec1_description, spec2_description, 
                    spec1_source, spec2_source, 
                    spec1_obligation, spec2_obligation, 
                    spec1_test_procedure, spec2_test_procedure,
                    title_similarity_score, description_similarity_score, 
                    comparison_method
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    combined_identifier,
                    spec1["spec_name"],
                    spec1["spec_version"],
                    spec2["spec_name"],
                    spec2["spec_version"],
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
