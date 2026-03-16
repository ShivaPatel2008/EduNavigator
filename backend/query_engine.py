from llama_index.core.schema import QueryBundle
from llama_index.core.retrievers import VectorIndexRetriever, QueryFusionRetriever
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts import PromptTemplate
from build_index import load_persisted_index
from query_classifier import QueryClassifier
from answer_validator import AnswerValidator
from hybrid_retriever import HybridRetriever
from knowledge_graph import KnowledgeGraph
from self_reflection import reflect_on_answer
from gpt4all_llm import LocalLLM
import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
# Load environment variables
load_dotenv()

# Load size control variables
MAX_ANSWER_LENGTH = int(os.getenv("MAX_ANSWER_LENGTH", "150"))
MAX_SOURCES = int(os.getenv("MAX_SOURCES", "3"))
MAX_HIGHLIGHTED_CHUNKS = int(os.getenv("MAX_HIGHLIGHTED_CHUNKS", "2"))

# Custom prompt
CUSTOM_PROMPT = PromptTemplate(
    "You are an AI assistant for an educational program. Answer the question based only on the provided context. "
    "If the information is not in the context, respond with: 'I could not find that information in the program documents.'\n\n"
    "Context:\n{context_str}\n\n"
    "Question: {query_str}\n\n"
    "Answer:"
)

# Conversation memory
conversation_memory: Dict[str, List[Dict]] = {}

def expand_query(question: str, llm) -> List[str]:
    """
    Expand the query using LLM to generate related queries.
    """
    prompt = f"""
    Given the question: "{question}"
    Generate 3 related questions that would help retrieve more comprehensive information.
    Return only the questions, one per line.
    """
    response = llm.complete(prompt).text.strip()
    expanded = [q.strip() for q in response.split('\n') if q.strip()]
    return expanded[:3]  # Limit to 3

def get_answer_with_retrieval(question: str, query_engine, llm):
    """
    Perform retrieval and generate combined answer.
    """
    # Expand query
    expanded_queries = expand_query(question, llm)
    
    # Combine queries
    all_queries = [question] + expanded_queries
    
    # Query
    responses = []
    all_sources = []
    highlighted_chunks = []
    for q in all_queries:
        response = query_engine.query(q)
        responses.append(response)
        all_sources.extend([node.metadata.get('file_name', 'Unknown') for node in response.source_nodes])
        highlighted_chunks.extend([node.text for node in response.source_nodes])
    
    # Combine answers
    combined_answer = " ".join([r.response for r in responses])
    unique_sources = list(set(all_sources))
    unique_chunks = list(set(highlighted_chunks))
    retrieved_context = " ".join(unique_chunks)
    
    return combined_answer, unique_sources, unique_chunks, retrieved_context, expanded_queries

def log_query(log_data: dict):
    """
    Log query data to JSON file.
    """
    log_file = "logs/query_logs.json"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    try:
        with open(log_file, 'a') as f:
            json.dump(log_data, f)
            f.write('\n')
    except Exception as e:
        print(f"Logging error: {e}")

def create_query_engine(storage_dir: str = "storage", llm_model: str = None, top_k: int = 5):
    """
    Create a query engine with hybrid retrieval, MMR, and reranking.
    """
    if llm_model is None:
        llm_model = os.getenv("LLM_MODEL", "llama3-8b-8192")

    # Load index
    index = load_persisted_index(storage_dir)

    # LLM - Use GPT4All for local inference
    llm = LocalLLM(model_name=llm_model, temperature=0.1)

    # Use VectorIndexRetriever directly
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=top_k,
    )

    # Reranker
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n=5
    )

    # Query engine
    # Response synthesizer
    response_synthesizer = get_response_synthesizer(
        llm=llm,
        text_qa_template=CUSTOM_PROMPT
    )

    # Query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[reranker],
    )
    # Set custom prompt
    query_engine.update_prompts({"response_synthesizer:text_qa_template": CUSTOM_PROMPT})

    return query_engine, llm

def query_with_sources(question: str, query_engine, llm, filters: dict = None, conversation_id: str = None):
    """
    Query the engine with self-reflection loop, return concise answer with sources and short highlighted chunks.
    Includes expansion, validation, logging, and self-reflection.
    """
    start_time = time.time()

    # Classify query
    classifier = QueryClassifier()
    query_type = classifier.classify(question)
    if not filters:
        filters = classifier.get_filters(query_type)

    # Conversation memory
    history = ""
    if conversation_id and conversation_id in conversation_memory:
        history = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in conversation_memory[conversation_id][-5:]])  # Last 5 exchanges

    # Self-reflection loop
    iteration_count = 0
    max_iterations = 2
    top_k = 5
    reflection_results = []
    improved_answer = False
    final_answer = None
    final_sources = None
    final_chunks = None
    expanded_queries = None

    while iteration_count < max_iterations:
        # Create engine with current top_k
        current_engine, current_llm = create_query_engine(top_k=top_k)

        # Get answer with retrieval
        answer, sources, chunks, retrieved_context, expanded_queries = get_answer_with_retrieval(question, current_engine, current_llm)

        # Self-reflection
        reflection = reflect_on_answer(question, answer, retrieved_context, current_llm)
        reflection_results.append(reflection)

        if reflection['is_sufficient']:
            final_answer = answer
            final_sources = sources
            final_chunks = chunks
            break
        elif reflection['needs_more_retrieval']:
            top_k += 5
            iteration_count += 1
            improved_answer = True
        else:
            final_answer = answer
            final_sources = sources
            final_chunks = chunks
            break
    else:
        # Max iterations reached
        final_answer = answer
        final_sources = sources
        final_chunks = chunks

    # Validate answer
    validator = AnswerValidator()
    final_answer = validator.get_final_answer(question, final_answer, retrieved_context)

    # Make answer concise (1-3 sentences)
    concise_prompt = f"""
    Summarize the following answer in 1-3 simple sentences using plain English only. Remove any unnecessary details, symbols, or formatting. Keep the answer under {MAX_ANSWER_LENGTH} characters:

    Original answer: {final_answer}

    Concise summary:
    """
    concise_answer = llm.complete(concise_prompt).text.strip()

    # Limit sources to max configured value
    limited_sources = final_sources[:MAX_SOURCES] if len(final_sources) > MAX_SOURCES else final_sources

    # Create short highlighted chunks (max configured, each < 100 chars)
    short_chunks = []
    for chunk in final_chunks[:MAX_HIGHLIGHTED_CHUNKS]:  # Max configured chunks
        # Take first 100 characters and clean up
        short_chunk = chunk[:100].strip()
        if len(short_chunk) > 50:  # Only include if meaningful length
            short_chunks.append(short_chunk)

    # Update conversation memory
    if conversation_id:
        if conversation_id not in conversation_memory:
            conversation_memory[conversation_id] = []
        conversation_memory[conversation_id].append({
            "question": question,
            "answer": concise_answer,
            "timestamp": time.time()
        })

    # Log
    log_data = {
        "timestamp": time.time(),
        "conversation_id": conversation_id,
        "question": question,
        "query_type": query_type,
        "expanded_queries": expanded_queries,
        "retrieved_sources": limited_sources,
        "final_answer": concise_answer,
        "response_time": time.time() - start_time,
        "reflection_results": reflection_results,
        "iteration_count": iteration_count + 1,
        "improved_answer": improved_answer
    }
    log_query(log_data)

    reflection_metadata = {
        "iteration_count": iteration_count + 1,
        "improved_answer": improved_answer
    }

    return concise_answer, limited_sources, query_type, len(short_chunks), short_chunks, reflection_metadata

if __name__ == "__main__":
    engine, llm = create_query_engine()
    answer, sources, query_type, retrieved_chunks, highlighted_chunks, reflection = query_with_sources("What skills will I learn?", engine, llm)
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")
    print(f"Query Type: {query_type}")
    print(f"Retrieved Chunks: {retrieved_chunks}")
    print(f"Highlighted Chunks: {highlighted_chunks}")
    print(f"Reflection: {reflection}")