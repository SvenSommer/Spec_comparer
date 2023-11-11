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

def format_similarity_counts(similarity_data):
    # Prepare table headers
    headers = [
        "Spec1 ID", "Spec1 Name", "Spec1 Version",
        "Spec2 ID", "Spec2 Name", "Spec2 Version",
        "Similarity Count"
    ]

    # Determine the maximum width for each column
    column_widths = [len(header) for header in headers]
    for item in similarity_data:
        for idx, key in enumerate(item):
            column_widths[idx] = max(column_widths[idx], len(str(item[key])))

    # Create a format string for each row of the table
    row_format = " | ".join(["{:<" + str(width) + "}" for width in column_widths])

    # Print the table header
    print(row_format.format(*headers))
    print("-" * (sum(column_widths) + len(headers) * 3 - 1))

    # Print each row of data
    for item in similarity_data:
        print(row_format.format(
            item['spec1_id'],
            item['spec1_name'],
            item['spec1_version'],
            item['spec2_id'],
            item['spec2_name'],
            item['spec2_version'],
            item['similarity_count']
        ))




if __name__ == "__main__":
    try:
        do_import = True

        conn = sqlite3.connect("../public/db/requirements.db")
        document_helper = DocumentHelper("data/")
        db_writer = DataWriter(conn, do_import)
        processor = RequirementProcessor(db_writer)
        db_reader = DataReader(conn)

        if do_import:
            for parsed_file in document_helper.list_and_parse_xlsx_files():
                if parsed_file.error:
                    print(f"Filename: {parsed_file.filename}, Error: {parsed_file.error}")
                else:
                    specification = db_writer.get_or_create_specification(parsed_file)

                    processor.import_requirements_to_db(specification)


            custom_comparer = CustomRequirementComparer(conn, db_reader, db_writer, 0.2)

            # Retrieve all specifications from the database.
            specifications = db_reader.get_all_specifications()

            # Iterate over all specifications to compare every specification with the next one.
            for i in range(len(specifications) - 1):
                for j in range(i + 1, len(specifications)):
                    spec1 = specifications[i]
                    spec2 = specifications[j]
                    print(f"Comparing {spec1['name']} v{spec1['version']} with {spec2['name']} v{spec2['version']}")
                    custom_comparer.compare_requirements(spec1, spec2)

        # Call get_similarity_counts() on db_reader to get the data
        similarity_data = db_reader.get_similarity_counts()

        # Now pass this data to the format function
        format_similarity_counts(similarity_data)
        specifications =db_reader.get_all_specifications()

        for spec in specifications:
            print(f"Name: {spec['name']}, Type: {spec['type']}, Category: {spec['category']}")
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
