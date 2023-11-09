import os
import re
from dataclasses import dataclass

@dataclass
class ParsedFile:
    file_path: str    
    filename: str
    spec_name: str
    spec_version: str
    error: str = '' 

class DocumentHelper:
    def __init__(self, directory) -> None:
        self.directory = directory

    def parse_filename(self, filename):
        """
        Parses the filename to extract spec_name and spec_version.
        The 'spec_name' is everything after "gem" and before the last "_V".
        The 'spec_version' is everything after the last "_V" and before ".xlsx".
        """
        match = re.match(r"^(gem.*?)_V(.*?)\.xlsx$", filename)
        if match:
            spec_name, version = match.groups()
            return spec_name, version
        else:
            raise ValueError(f"Filename '{filename}' does not match expected pattern")

    def list_and_parse_xlsx_files(self):
            parsed_files = []
            for filename in os.listdir(self.directory):
                full_path = os.path.join(self.directory, filename)
                if filename.endswith('.xlsx'):
                    try:
                        spec_name, spec_version = self.parse_filename(filename)
                        parsed_file = ParsedFile(
                            file_path=full_path,
                            filename=filename,
                            spec_name=spec_name,
                            spec_version=spec_version
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