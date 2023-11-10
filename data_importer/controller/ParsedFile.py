from dataclasses import dataclass, field

@dataclass
class ParsedFile:
    file_path: str    
    filename: str
    spec_name: str
    spec_version: str
    spec_type: str = field(default="Unbekannt")
    category_type: str = field(default="Unbekannt")
    error: str = '' 
