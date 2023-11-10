import os
import re

from SpecificationType import SpecificationType
from ParsedFile import ParsedFile

class DocumentHelper:
    def __init__(self, directory) -> None:
        self.directory = directory
        self.spec_type = SpecificationType()

    def parse_filename(self, filename):
        match = re.match(r"^(gem.*?)_V(.*?)\.xlsx$", filename)
        if match:
            spec_name, version = match.groups()
            subtype, cattype = self.spec_type.get_spec_type(spec_name)
            return spec_name, version, subtype, cattype
        else:
            raise ValueError(f"Filename '{filename}' does not match expected pattern")

    def list_and_parse_xlsx_files(self):
        parsed_files = []
        for filename in os.listdir(self.directory):
            full_path = os.path.join(self.directory, filename)
            if filename.endswith('.xlsx'):
                try:
                    spec_name, spec_version, spec_type, category_type = self.parse_filename(filename)
                    parsed_file = ParsedFile(
                        file_path=full_path,
                        filename=filename,
                        spec_name=spec_name,
                        spec_version=spec_version,
                        spec_type=spec_type,
                        category_type=category_type
                    )
                except ValueError as e:
                    parsed_file = ParsedFile(
                        file_path=full_path,
                        filename=filename,
                        spec_name="Parsing error",
                        spec_version=str(e),
                        error=str(e)
                    )
                parsed_files.append(parsed_file)
        return parsed_files
    
