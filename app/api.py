from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.rag.qa_engine import create_qa_chain, query_rag
from src.rag.retriever import get_vectorstore_retriever

app = FastAPI()
templates = Jinja2Templates(directory="templates")

retriever = get_vectorstore_retriever()
qa_chain = create_qa_chain(retriever)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask-ui", response_class=HTMLResponse)
def ask_ui(request: Request, question: str = Form(...)):
    result = query_rag(qa_chain, question)
    sources = list({
        doc.metadata.get("source", "unknown")
        for doc in result["source_documents"]
    })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "answer": result["result"],
        "sources": sources
    })