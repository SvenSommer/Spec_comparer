from dataclasses import dataclass

@dataclass
class Requirement:
    spec_name: str
    spec_version: str
    source: str
    requirement_number: str
    title: str
    description: str
    processed_title: str
    processed_description: str
    obligation: str
    test_procedure: str = "unknown"  # Default value for test_procedure
