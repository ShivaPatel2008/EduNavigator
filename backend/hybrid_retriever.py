from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.vector_stores.faiss import FaissVectorStore
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List

class HybridRetriever(BaseRetriever):
    def __init__(self, vector_store: FaissVectorStore, documents: List[str], nodes: List, alpha: float = 0.5):
        """
        Hybrid retriever combining BM25 and vector search.
        alpha: weight for vector search (1-alpha for BM25)
        """
        super().__init__()
        self.vector_store = vector_store
        self.documents = documents
        self.nodes = nodes
        self.alpha = alpha

        # Prepare BM25
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def _retrieve_bm25(self, query: str, top_k: int) -> List[NodeWithScore]:
        """Retrieve using BM25"""
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Get top_k indices
        top_indices = np.argsort(bm25_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if bm25_scores[idx] > 0:
                node = self.nodes[idx]
                score = bm25_scores[idx]
                results.append(NodeWithScore(node=node, score=score))

        return results

    def _retrieve_vector(self, query: str, top_k: int) -> List[NodeWithScore]:
        """Retrieve using vector search"""
        query_bundle = QueryBundle(query_str=query)
        query = VectorStoreQuery(
            query_embedding=None,  # Will be computed
            similarity_top_k=top_k,
            query_str=query_bundle.query_str
        )
        result = self.vector_store.query(query)
        return result.nodes

    def _reciprocal_rank_fusion(self, bm25_results: List[NodeWithScore], vector_results: List[NodeWithScore], k: int = 60) -> List[NodeWithScore]:
        """Combine results using Reciprocal Rank Fusion"""
        scores = {}

        # BM25 scores
        for i, result in enumerate(bm25_results):
            node_id = id(result.node)
            scores[node_id] = scores.get(node_id, 0) + (1 - self.alpha) / (k + i + 1)

        # Vector scores
        for i, result in enumerate(vector_results):
            node_id = id(result.node)
            scores[node_id] = scores.get(node_id, 0) + self.alpha / (k + i + 1)

        # Sort by combined score
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Return top results with nodes
        results = []
        node_map = {id(node): node for node in self.nodes}
        for node_id, score in sorted_nodes[:10]:  # Top 10
            node = node_map.get(node_id)
            if node:
                results.append(NodeWithScore(node=node, score=score))

        return results

    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Async retrieve"""
        bm25_results = self._retrieve_bm25(query_bundle.query_str, top_k=10)
        vector_results = self._retrieve_vector(query_bundle.query_str, top_k=10)
        return self._reciprocal_rank_fusion(bm25_results, vector_results)

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Sync retrieve"""
        bm25_results = self._retrieve_bm25(query_bundle.query_str, top_k=10)
        vector_results = self._retrieve_vector(query_bundle.query_str, top_k=10)
        return self._reciprocal_rank_fusion(bm25_results, vector_results)