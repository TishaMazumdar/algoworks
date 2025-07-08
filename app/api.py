from fastapi import FastAPI
from pydantic import BaseModel
from src.rag.qa_engine import run_qa_chain  

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    response = run_qa_chain(request.question)
    return response