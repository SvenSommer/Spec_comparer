import logging

from abc import ABC, abstractmethod
from typing import Dict, List


class RequirementComparer(ABC):
    def __init__(self, db_connection, data_reader, data_writer, treshold):
        self.db_connection = db_connection
        self.data_reader = data_reader
        self.data_writer = data_writer
        self.treshold = treshold


    def compare_requirements(self, specifkation1, specifkation2):
        spec1_requirements = self.data_reader.get_requirements_by_specification(specifkation1)
        spec2_requirements = self.data_reader.get_requirements_by_specification(specifkation2)
        for i, spec1_req in enumerate(spec1_requirements):
            for spec2_req in spec2_requirements:
                if spec1_req["requirement_number"] == spec2_req["requirement_number"]:
                    continue

                title_similarity = self.calculate_similarity(
                    spec1_req["processed_title"], spec2_req["processed_title"]
                )
                description_similarity = self.calculate_similarity(
                    spec1_req["processed_description"],
                    spec2_req["processed_description"],
                )

                if self.is_above_threshold(title_similarity, description_similarity, self.treshold):
                    method = self.get_comparison_method()
                    self.data_writer.add_requirement_similarities(
                        spec1_req,
                        spec2_req,
                        method,
                        title_similarity,
                        description_similarity,
                    )
            if (i + 1) % 10 == 0:
                logging.info(
                    f"Progress: Compared {i + 1} requirements of {specifkation1['fullname']} with {specifkation2['fullname']} by using {self.get_comparison_method()}"
                )

        self.db_connection.commit()

    @abstractmethod
    def calculate_similarity(self, text1: str, text2: str) -> float:
        pass

    @abstractmethod
    def get_comparison_method(self) -> str:
        pass

    @abstractmethod
    def is_above_threshold(
        self, title_similarity: float, description_similarity: float, treshold: float
    ) -> bool:
        pass
