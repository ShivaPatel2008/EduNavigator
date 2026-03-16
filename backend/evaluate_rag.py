import time
import json
from query_engine import create_query_engine, query_with_sources
from answer_validator import AnswerValidator

# Sample questions for evaluation
EVALUATION_QUESTIONS = [
    "What skills will I learn?",
    "What are the admission requirements?",
    "How much does the program cost?",
    "What programming languages are taught?",
    "When does the program start?",
    "What is the duration of the course?"
]

def evaluate_rag():
    """
    Evaluate the RAG system on retrieval accuracy, latency, and answer completeness.
    """
    # Load engine
    query_engine, llm = create_query_engine()

    results = []
    total_latency = 0
    total_accuracy = 0

    validator = AnswerValidator()

    for question in EVALUATION_QUESTIONS:
        start_time = time.time()
        answer, sources, query_type, retrieved_chunks = query_with_sources(question, query_engine, llm)
        latency = time.time() - start_time

        # Simple accuracy check (if answer is not the not found message)
        accuracy = 1 if answer != "I could not find that information in the program documents." else 0

        # Completeness (length of answer)
        completeness = len(answer.split()) / 50  # Normalize to 50 words

        result = {
            "question": question,
            "answer": answer,
            "sources": sources,
            "query_type": query_type,
            "retrieved_chunks": retrieved_chunks,
            "latency": latency,
            "accuracy": accuracy,
            "completeness": min(completeness, 1.0)  # Cap at 1
        }
        results.append(result)
        total_latency += latency
        total_accuracy += accuracy

    # Summary
    avg_latency = total_latency / len(EVALUATION_QUESTIONS)
    avg_accuracy = total_accuracy / len(EVALUATION_QUESTIONS)
    avg_completeness = sum(r["completeness"] for r in results) / len(results)

    summary = {
        "total_questions": len(EVALUATION_QUESTIONS),
        "average_latency": avg_latency,
        "average_accuracy": avg_accuracy,
        "average_completeness": avg_completeness
    }

    # Save results
    with open("logs/evaluation_results.json", "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    print("Evaluation completed.")
    print(f"Average Latency: {avg_latency:.2f}s")
    print(f"Average Accuracy: {avg_accuracy:.2f}")
    print(f"Average Completeness: {avg_completeness:.2f}")

if __name__ == "__main__":
    evaluate_rag()