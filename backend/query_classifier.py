from transformers import pipeline
import os

class QueryClassifier:
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.categories = [
            "informational",  # General information
            "comparison",     # Comparing options
            "temporal",       # Time-related questions
            "admission",      # Admission requirements
            "curriculum",     # Course content, skills
            "fees"           # Cost-related
        ]

    def classify(self, query: str) -> str:
        """
        Classify the query into one of the categories.
        """
        result = self.classifier(query, self.categories)
        return result['labels'][0]  # Highest score

    def get_filters(self, query_type: str) -> dict:
        """
        Return metadata filters based on query type.
        """
        filters = {}
        if query_type == "admission":
            filters["document_type"] = "admission"
        elif query_type == "curriculum":
            filters["document_type"] = "curriculum"
        elif query_type == "fees":
            filters["document_type"] = "fees"
        # Add more as needed
        return filters

if __name__ == "__main__":
    classifier = QueryClassifier()
    query = "What skills will I learn?"
    query_type = classifier.classify(query)
    filters = classifier.get_filters(query_type)
    print(f"Query: {query}")
    print(f"Type: {query_type}")
    print(f"Filters: {filters}")