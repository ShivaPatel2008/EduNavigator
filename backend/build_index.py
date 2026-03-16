from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from ingestion import load_documents_from_jsonl
import faiss
import os
import shutil

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
def build_and_persist_index(jsonl_file: str = "final_rag_input.jsonl", storage_dir: str = "storage"):
    """
    Build FAISS vector index from documents in JSONL file and persist to disk.
    """
    # Load documents from JSONL
    documents = load_documents_from_jsonl(jsonl_file)
    print(f"Loaded {len(documents)} documents")

    # Text splitter
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    # Embedding model - simplified
    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # FAISS vector store - let LlamaIndex handle the dimension
    vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatIP(384))

    # Storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Build index with fewer documents for testing
    test_documents = documents  # Start with just 5 documents
    print(f"Building index with {len(test_documents)} test documents")

    index = VectorStoreIndex.from_documents(
        test_documents,
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=[text_splitter],
    )

    # Persist index
    index.storage_context.persist(persist_dir=storage_dir)
    print(f"Index built and persisted to {storage_dir}")

    # Check what files were created
    import os
    if os.path.exists(storage_dir):
        files = os.listdir(storage_dir)
        print(f"Files created in {storage_dir}: {files}")

def load_persisted_index(storage_dir: str = "storage"):
    """
    Load persisted index from disk with error handling and auto-rebuild.
    """
    try:
        # Load FAISS vector store from persist directory
        vector_store = FaissVectorStore.from_persist_dir(persist_dir=storage_dir)

        # Create storage context with the loaded vector store
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=storage_dir
        )

        # Load the index from storage
        index = load_index_from_storage(storage_context)
        print(f"Index loaded successfully from {storage_dir}")
        return index

    except Exception as e:
        print(f"Error loading persisted index: {e}")
        print("Attempting to rebuild index...")

        # Check if source data exists
        jsonl_file = "final_rag_input.jsonl"
        if os.path.exists(jsonl_file):
            # Remove corrupted storage
            if os.path.exists(storage_dir):
                shutil.rmtree(storage_dir)
                print(f"Removed corrupted storage directory: {storage_dir}")

            # Rebuild index
            build_and_persist_index(jsonl_file, storage_dir)

            # Try loading again
            try:
                vector_store = FaissVectorStore.from_persist_dir(persist_dir=storage_dir)
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store,
                    persist_dir=storage_dir
                )
                index = load_index_from_storage(storage_context)
                print("Index rebuilt and loaded successfully")
                return index
            except Exception as rebuild_error:
                raise Exception(f"Failed to rebuild index: {rebuild_error}")
        else:
            raise Exception(f"Cannot rebuild index: source file {jsonl_file} not found")
    return index

if __name__ == "__main__":
    if not os.path.exists("storage"):
        os.makedirs("storage")
    build_and_persist_index()