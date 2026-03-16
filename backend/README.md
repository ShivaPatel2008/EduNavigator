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
   - Copy `.env` file and add your OpenAI API key:
   ```bash
   cp .env .env.local
   ```
   - Edit `.env.local` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
   - Get your API key from: https://platform.openai.com/api-keys
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

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LLM_MODEL`: LLM model to use (default: gpt-3.5-turbo)
  - Options: `gpt-4`, `gpt-4-turbo-preview`, `gpt-3.5-turbo`
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 8001)

### Model Recommendations

- **gpt-3.5-turbo**: Fast and cost-effective for most use cases
- **gpt-4**: Higher quality responses, slower and more expensive
- **gpt-4-turbo-preview**: Latest GPT-4 model with improved performance

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

- Set `OPENAI_API_KEY` environment variable for LLM access
- Optionally set `LLM_MODEL` env var (defaults to gpt-3.5-turbo)
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