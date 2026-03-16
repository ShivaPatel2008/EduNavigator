from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from ingestion import load_documents

import faiss
import os
def build_and_persist_index(data_dir: str = "data", storage_dir: str = "storage"):
    """
    Build FAISS vector index from documents and persist to disk.
    """
    # Load documents
    documents = load_documents(data_dir)

    # Text splitter
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    # Embedding model with caching
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
        cache_folder="./cache/embeddings"  # Cache embeddings
    )

    # FAISS vector store
    d = 384  # dimension for bge-small-en-v1.5
    faiss_index = faiss.IndexFlatIP(d)
    vector_store = FaissVectorStore(faiss_index=faiss_index)

    # Storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Build index
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=[text_splitter],
    )

    # Persist index
    index.storage_context.persist(persist_dir=storage_dir)
    print(f"Index built and persisted to {storage_dir}")

def load_persisted_index(storage_dir: str = "storage"):
    """
    Load persisted index from disk.
    """
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index_from_storage(storage_context)
    return index

if __name__ == "__main__":
    if not os.path.exists("storage"):
        os.makedirs("storage")
    build_and_persist_index()