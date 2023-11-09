from data_importer.controller.RequirementComparer import RequirementComparer


class JaccardRequirementComparer(RequirementComparer):
    def calculate_similarity(self, text1: str, text2: str) -> float:
        set1 = set(text1.split())
        set2 = set(text2.split())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union) if union else 0

    def get_comparison_method(self) -> str:
        return 'jaccard_similarity'

    def is_above_threshold(self, title_similarity: float, description_similarity: float) -> bool:
        return title_similarity > 0.6 or description_similarity > 0.5