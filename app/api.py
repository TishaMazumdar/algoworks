from fastapi import FastAPI
from pydantic import BaseModel
from src.rag.qa_engine import create_qa_chain, query_rag
from src.rag.retriever import get_vectorstore_retriever

app = FastAPI()

# Build chain once (on app startup)
retriever = get_vectorstore_retriever()
qa_chain = create_qa_chain(retriever)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    result = query_rag(qa_chain, request.question)

    # Extract sources
    sources = list({
        doc.metadata.get("source", "unknown")
        for doc in result["source_documents"]
    })

    return {
        "answer": result["result"],
        "sources": sources
    }