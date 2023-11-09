import logging
import sqlite3

import sys



sys.path.append("./controller")
from Specification import Specification
from RequirementProcessor import RequirementProcessor
from DataReader import DataReader
from DataWriter import DataWriter
from DocumentHelper import DocumentHelper
from CustomRequirementComparer import CustomRequirementComparer


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
if __name__ == "__main__":
    try:
        print("Hello world")
        conn = sqlite3.connect("../public/db/requirements.db")
        print("conn established")
        document_helper = DocumentHelper("data/")
        print("document_helper")
        db_writer = DataWriter(conn, True)
        print("db_writer")
        processor = RequirementProcessor(db_writer)
        print("processor")
        db_reader = DataReader(conn)
        print("db_reader")


        for parsed_file in document_helper.list_and_parse_xlsx_files():
            if parsed_file.error:
                print(f"Filename: {parsed_file.filename}, Error: {parsed_file.error}")
            else:
                specification = db_writer.get_or_create_specification(parsed_file)

                processor.import_requirements_to_db(specification)


        custom_comparer = CustomRequirementComparer(conn, db_reader, db_writer)

        # Retrieve all specifications from the database.
        specifications = db_reader.get_all_specifications()

        # Iterate over all specifications to compare every specification with the next one.
        for i in range(len(specifications) - 1):
            for j in range(i + 1, len(specifications)):
                spec1 = specifications[i]
                spec2 = specifications[j]
                print(f"Comparing {spec1['name']} v{spec1['version']} with {spec2['name']} v{spec2['version']}")
                custom_comparer.compare_requirements(spec1, spec2)



        # cosine_comparer.compare_requirements()
        # jaccard_comparer = JaccardRequirementComparer(processor.conn, False)
        # jaccard_comparer.compare_requirements()
        # custom_comparer = CustomRequirementComparer(processor.conn, False)
        # custom_comparer.compare_requirements()

    # comparer.fetch_sample_data('requirement_similarities', 100)
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
    finally:
        # This ensures that processor.close() is called only if processor is defined
        if "processor" in locals():
            conn.close()
