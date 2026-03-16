# EduNavigator Course Assistant Backend

A complete AI-powered educational assistant with advanced RAG capabilities.

## Features

- **Hybrid Retrieval**: BM25 + Vector Search with reciprocal rank fusion
- **Semantic Document Tagging**: Automatic metadata assignment using LLM
- **Knowledge Graph**: Entity extraction and relational queries using NetworkX
- **Query Classification**: BART zero-shot classification
- **Query Expansion**: LLM-generated related queries
- **Answer Validation**: Context sufficiency checking
- **Conversation Memory**: Follow-up question support
- **Source Highlighting**: Exact text chunks used for answers
- **Comprehensive Logging**: Query tracking and observability
- **Async FastAPI**: High-performance API endpoints
- **Admin Dashboard**: Document upload, index rebuilding, log viewing
- **Embedding Caching**: Faster repeated queries
- **Evaluation Framework**: Automated performance testing

## Project Structure

```
backend/
├── data/                 # Document storage
├── storage/              # Vector index storage
├── logs/                 # Query logs and evaluation results
├── cache/                # Embedding cache
├── ingestion.py          # Document loading
├── build_index.py        # Index building and persistence
├── query_engine.py       # Query engine with retrieval pipeline
├── query_classifier.py   # Query classification
├── answer_validator.py   # Answer validation
├── evaluate_rag.py       # Evaluation script
├── api.py                # FastAPI server
├── requirements.txt      # Python dependencies
└── README.md
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   - Copy `.env` file and add your Google Gemini API key:
   ```bash
   cp .env .env.local
   ```
   - Edit `.env.local` and configure GPT4All model:
   ```
   LLM_MODEL=gpt4all-mini
   ```
   - GPT4All will automatically download the model on first use (no API key required)
   - The `.env.local` file is gitignored for security

3. **Place your program documents** (text/PDF) in the `data/` folder.

4. **Build the vector index:**
   ```bash
   python build_index.py
   ```

4. Start the API server:
   ```bash
   python api.py
   ```

5. (Optional) Run evaluation:
   ```bash
   python evaluate_rag.py
   ```

## Configuration

### Environment Variables

- `LLM_MODEL`: GPT4All model to use (default: gpt4all-mini)
  - Options: `gpt4all-mini`, `orca-mini`, `llama-2-7b-chat`, etc.
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 8001)

### Model Recommendations

- **gemini-3-flash-preview**: Latest and fastest model, excellent performance (default)
- **gemini-pro**: Fast and cost-effective for most use cases
- **gemini-pro-vision**: For multimodal inputs (images + text)

## API Usage

## API Usage

### POST /ask

Request:
```json
{
  "question": "What skills will I learn?",
  "conversation_id": "123",  // optional for follow-up questions
  "filters": {"document_type": "curriculum"}  // optional metadata filters
}
```

Response:
```json
{
  "answer": "You will learn Python programming, data analysis, machine learning basics, and web development with FastAPI.",
  "sources": ["curriculum.txt"],
  "query_type": "curriculum",
  "retrieved_chunks": 5
}
```

## Configuration

- GPT4All models run locally - no API key required
- Optionally set `LLM_MODEL` env var (defaults to gpt4all-mini)
- Query logs saved to `logs/query_logs.json`
- Evaluation results saved to `logs/evaluation_results.json`

## Query Classification

Queries are automatically classified into:
- informational
- comparison
- temporal
- admission
- curriculum
- fees

Classification adds relevant metadata filters for better retrieval.

## Conversation Memory

Use `conversation_id` to maintain context for follow-up questions. The system remembers the last 5 exchanges.

## Evaluation

Run `evaluate_rag.py` to measure:
- Retrieval accuracy
- Response latency
- Answer completeness

Results are saved to `logs/evaluation_results.json`.