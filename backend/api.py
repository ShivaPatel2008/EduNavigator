from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import os
import json
from datetime import datetime
from query_engine import query_with_sources, create_query_engine

app = FastAPI(title="EduNavigator Course Assistant", version="3.0.0")

class QuestionRequest(BaseModel):
    question: str
    conversation_id: str = None
    filters: dict = None

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    query_type: str
    retrieved_chunks: int
    highlighted_chunks: list[str]
    reflection: dict = None

# Mock responses for testing
MOCK_RESPONSES = {
    "courses": {
        "answer": "We offer several courses including Computer Science, Data Science, and AI/ML programs. Our flagship courses are:\n\n1. **Computer Science Fundamentals** - Covers programming, algorithms, and software engineering\n2. **Data Science & Analytics** - Focuses on data analysis, machine learning, and visualization\n3. **Artificial Intelligence** - Advanced AI concepts including deep learning and neural networks\n\nEach course includes hands-on projects and industry-relevant skills.",
        "sources": ["course_catalog.pdf", "program_overview.pdf"],
        "query_type": "informational",
        "retrieved_chunks": 5,
        "highlighted_chunks": [
            "Computer Science Fundamentals covers core programming concepts",
            "Data Science program includes machine learning algorithms",
            "AI course features deep learning and neural networks"
        ]
    },
    "admission": {
        "answer": "Admission requirements vary by program, but generally include:\n\n- Bachelor's degree in relevant field\n- Minimum GPA of 3.0\n- GRE/GMAT scores (waived for some programs)\n- Two letters of recommendation\n- Statement of purpose\n\nInternational students need TOEFL/IELTS scores. Applications are reviewed holistically.",
        "sources": ["admissions_guide.pdf", "requirements.pdf"],
        "query_type": "informational",
        "retrieved_chunks": 3,
        "highlighted_chunks": [
            "Minimum GPA requirement is 3.0",
            "GRE scores are required for most programs",
            "International students need English proficiency tests"
        ]
    },
    "fees": {
        "answer": "Tuition fees for our programs:\n\n- **Computer Science**: $45,000/year\n- **Data Science**: $42,000/year\n- **AI/ML**: $48,000/year\n\nAdditional costs include:\n- Books and materials: $1,500\n- Health insurance: $2,500\n- Living expenses: $15,000\n\nFinancial aid and scholarships are available for eligible students.",
        "sources": ["tuition_fees.pdf", "financial_aid.pdf"],
        "query_type": "informational",
        "retrieved_chunks": 4,
        "highlighted_chunks": [
            "CS program tuition is $45,000 per year",
            "Financial aid available for qualified students",
            "Additional costs include books and insurance"
        ]
    }
}

def get_mock_response(question: str) -> AnswerResponse:
    """Return mock response based on question keywords"""
    question_lower = question.lower()

    if any(word in question_lower for word in ["course", "program", "curriculum", "subjects"]):
        return AnswerResponse(**MOCK_RESPONSES["courses"])
    elif any(word in question_lower for word in ["admission", "apply", "requirement", "eligible"]):
        return AnswerResponse(**MOCK_RESPONSES["admission"])
    elif any(word in question_lower for word in ["fee", "cost", "tuition", "price", "pay"]):
        return AnswerResponse(**MOCK_RESPONSES["fees"])
    else:
        return AnswerResponse(
            answer="I'd be happy to help you with information about our educational programs. Could you please specify what you're looking for? I can provide details about courses, admissions, fees, or other program information.",
            sources=["general_info.pdf"],
            query_type="general",
            retrieved_chunks=2,
            highlighted_chunks=["General program information available"]
        )

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Answer questions about educational programs"""
    try:
        # Create query engine
        engine, llm = create_query_engine()
        
        # Query with self-reflection
        answer, sources, query_type, retrieved_chunks, highlighted_chunks, reflection = query_with_sources(
            request.question, engine, llm, request.filters, request.conversation_id
        )
        
        return AnswerResponse(
            answer=answer,
            sources=sources,
            query_type=query_type,
            retrieved_chunks=retrieved_chunks,
            highlighted_chunks=highlighted_chunks,
            reflection=reflection
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    """Upload documents to the knowledge base"""
    uploaded_files = []
    for file in files:
        # Save file
        file_path = Path("data") / file.filename
        file_path.parent.mkdir(exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        uploaded_files.append(file.filename)

    return {"message": f"Uploaded {len(uploaded_files)} files", "files": uploaded_files}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/logs")
async def get_logs():
    """Get system logs"""
    return {"logs": ["System initialized", "Mock responses active"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a new document to the data directory.
    """
    try:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        file_path = data_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"message": f"Document {file.filename} uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rebuild_index")
async def rebuild_index():
    """
    Rebuild the vector index with new documents.
    """
    try:
        # Run rebuild in background
        import subprocess
        subprocess.Popen(["python", "build_index.py"])
        return {"message": "Index rebuild started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs():
    """
    Get recent query logs.
    """
    try:
        logs = []
        with open("logs/query_logs.json", "r") as f:
            for line in f:
                logs.append(json.loads(line.strip()))
        return {"logs": logs[-50:]}  # Last 50 logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluation")
async def get_evaluation():
    """
    Get evaluation results.
    """
    try:
        with open("logs/evaluation_results.json", "r") as f:
            results = json.load(f)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)