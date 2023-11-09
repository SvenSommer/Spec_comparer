from dataclasses import dataclass


class Specification:
    def __init__(self, spec_id, name, version, fullname, file_path, words_to_remove):
        self.id = spec_id
        self.name = name
        self.version = version
        self.fullname = fullname
        self.file_path = file_path
        self.words_to_remove = words_to_remove