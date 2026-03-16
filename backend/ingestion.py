from llama_index import SimpleDirectoryReader
from llama_index.llms import OpenAI
from pathlib import Path
import os

def tag_document(content: str, llm) -> list:
    """
    Use LLM to assign semantic tags to document content.
    """
    prompt = f"""
    Analyze the following document content and assign relevant tags from this list:
    admissions, curriculum, scholarships, internships, placements, fees, requirements, courses, technologies, careers

    Return only the tags as a comma-separated list.

    Content: {content[:1000]}...  # First 1000 chars
    """
    response = llm.complete(prompt).text.strip()
    tags = [tag.strip() for tag in response.split(',') if tag.strip()]
    return tags

def load_documents(data_dir: str = "data"):
    """
    Load documents from the data directory with semantic tagging.
    Supports text and PDF files.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        raise ValueError(f"Data directory {data_dir} does not exist")

    reader = SimpleDirectoryReader(
        input_dir=data_path,
        required_exts=[".txt", ".pdf"],
        recursive=True
    )
    documents = reader.load_data()

    # Add semantic tags
    llm = OpenAI(model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"), temperature=0.1)
    for doc in documents:
        tags = tag_document(doc.text, llm)
        doc.metadata['tags'] = tags

    return documents

if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")