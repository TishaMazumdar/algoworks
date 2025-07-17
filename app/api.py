from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.rag.qa_engine import create_qa_chain, query_rag
from src.rag.retriever import get_vectorstore_retriever
from src.models.history import ChatEntry, load_cache, save_cache, clear_cache
import markdown

app = FastAPI()
templates = Jinja2Templates(directory="templates")

retriever = get_vectorstore_retriever()
qa_chain = create_qa_chain(retriever)

# Load history at startup
chat_history = load_cache()

# Function to check if a question is already cached
def get_cached_answer(question):
    for entry in chat_history:
        if entry.question.strip().lower() == question.strip().lower():
            return entry
    return None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask-ui", response_class=HTMLResponse)
def ask_ui(request: Request, question: str = Form(...)):
    cached = get_cached_answer(question)

    if cached:
        formatted_answer = cached.answer
        sources = cached.sources
    else:
        result = query_rag(qa_chain, question)
        raw_answer = result["result"]
        formatted_answer = markdown.markdown(raw_answer)
        sources = list({
            doc.metadata.get("source", "unknown")
            for doc in result["source_documents"]
        })

        new_entry = ChatEntry(question=question, answer=formatted_answer, sources=sources)
        chat_history.append(new_entry)
        chat_history[:] = chat_history[-6:]
        save_cache(new_entry)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "answer": formatted_answer,
        "sources": sources,
        "history": [entry.to_dict() for entry in chat_history][-5:]
    })

@app.post("/clear-history")
def clear_history(request: Request):
    chat_history.clear()
    clear_cache()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "history": [],
        "answer": None,
        "sources": []
    })