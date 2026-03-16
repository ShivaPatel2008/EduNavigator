import networkx as nx
import spacy
from llama_index.llms import OpenAI
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.nlp = spacy.load("en_core_web_sm")
        self.llm = OpenAI(model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"), temperature=0.1)

    def extract_entities(self, text: str) -> List[str]:
        """
        Extract entities using spaCy.
        """
        doc = self.nlp(text)
        entities = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'SKILL', 'COURSE']]
        return entities

    def extract_relations(self, text: str) -> List[Dict]:
        """
        Use LLM to extract relations from text.
        """
        prompt = f"""
        Extract relationships from the following text. Format as:
        entity1 - relation - entity2

        Text: {text[:500]}...

        Return only the relationships, one per line.
        """
        response = self.llm.complete(prompt).text.strip()
        relations = []
        for line in response.split('\n'):
            if ' - ' in line:
                parts = line.split(' - ')
                if len(parts) == 3:
                    relations.append({
                        'entity1': parts[0].strip(),
                        'relation': parts[1].strip(),
                        'entity2': parts[2].strip()
                    })
        return relations

    def build_graph(self, documents: List) -> None:
        """
        Build knowledge graph from documents.
        """
        for doc in documents:
            text = doc.text
            entities = self.extract_entities(text)
            relations = self.extract_relations(text)

            # Add entities as nodes
            for entity in entities:
                self.graph.add_node(entity, type='entity')

            # Add relations as edges
            for rel in relations:
                self.graph.add_edge(rel['entity1'], rel['entity2'], relation=rel['relation'])

    def query_graph(self, query: str) -> str:
        """
        Query the knowledge graph for relational information.
        """
        # Simple query: find related entities
        entities = self.extract_entities(query)
        if not entities:
            return "No entities found in query."

        related = set()
        for entity in entities:
            if entity in self.graph:
                neighbors = list(self.graph.neighbors(entity))
                related.update(neighbors)

        if related:
            return f"Related entities: {', '.join(related)}"
        else:
            return "No related information found."

    def get_graph_stats(self) -> Dict:
        """
        Get graph statistics.
        """
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph)
        }