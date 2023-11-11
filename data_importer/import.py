import logging
import sqlite3
import os
import sys

sys.path.append("./controller")
from RequirementProcessor import RequirementProcessor
from DataReader import DataReader
from DataWriter import DataWriter
from DocumentHelper import DocumentHelper
from CustomRequirementComparer import CustomRequirementComparer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def format_similarity_counts(similarity_data):
    headers = ["Spec1 ID", "Spec1 Name", "Spec1 Version", "Spec2 ID", "Spec2 Name", "Spec2 Version", "Similarity Count"]
    column_widths = [len(header) for header in headers]
    for item in similarity_data:
        for idx, key in enumerate(item):
            column_widths[idx] = max(column_widths[idx], len(str(item[key])))
    row_format = " | ".join(["{:<" + str(width) + "}" for width in column_widths])
    print(row_format.format(*headers))
    print("-" * (sum(column_widths) + len(headers) * 3 - 1))
    for item in similarity_data:
        print(row_format.format(item["spec1_id"], item["spec1_name"], item["spec1_version"], item["spec2_id"], item["spec2_name"], item["spec2_version"], item["similarity_count"]))

if __name__ == "__main__":
    try:
        do_import = True
        db_directory = "../public/db"
        db_file = "requirements.db"
        db_path = os.path.join(db_directory, db_file)
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)
        if do_import and os.path.exists(db_path):
             os.remove(db_path)

        conn = sqlite3.connect(db_path)
        document_helper = DocumentHelper("data/")
        db_writer = DataWriter(conn, do_import)
        words_to_replace = ["ePA-Frontend", "ePA Frontend",  "E-Rezept-FdV","TI-ITSM-Teilnehmer", "Hersteller", "Produkttyp"]
        processor = RequirementProcessor(db_writer, words_to_replace)
        db_reader = DataReader(conn)

        if do_import:
            for parsed_file in document_helper.list_and_parse_xlsx_files():
                if parsed_file.error:
                    print(f"Filename: {parsed_file.filename}, Error: {parsed_file.error}")
                else:
                    specification = db_writer.get_or_create_specification(parsed_file)
                    processor.import_requirements_to_db(specification)

            custom_comparer = CustomRequirementComparer(db_reader, db_writer, 0.2)
            specifications = db_reader.get_all_specifications()
            for i in range(len(specifications) - 1):
                for j in range(i + 1, len(specifications)):
                    spec1 = specifications[i]
                    spec2 = specifications[j]
                    print(f"Comparing {spec1['name']} v{spec1['version']} with {spec2['name']} v{spec2['version']}")
                    custom_comparer.compare_requirements(spec1, spec2)

        similarity_data = db_reader.get_similarity_counts()
        format_similarity_counts(similarity_data)

    except Exception as e:
        logging.error("An error occurred", exc_info=True)
    finally:
        if 'processor' in locals():
            conn.close()
