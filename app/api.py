from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import markdown

from src.rag.qa_engine import create_qa_chain, query_rag
from src.rag.retriever import get_vectorstore_retriever
from src.models.history import ChatEntry, load_cache, save_cache, clear_cache
from app.auth_routes import router as auth_router

# Load env vars
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# FastAPI app setup
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(auth_router)
templates = Jinja2Templates(directory="templates")

# RAG + history setup
retriever = get_vectorstore_retriever()
qa_chain = create_qa_chain(retriever)
chat_history = load_cache()

# 🧠 Check if a question is already cached
def get_cached_answer(question: str):
    question = question.strip().lower()
    for entry in chat_history:
        if entry.question.strip().lower() == question:
            return entry
    return None

# 🏠 Home route (requires login)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")

    toast = request.session.pop("toast", None)  # ✅ Get & clear the toast

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_name": user["name"],
        "toast": toast  # ✅ Pass to template
    })

# 💬 Handle UI-based query asking
@app.post("/ask-ui", response_class=HTMLResponse)
def ask_ui(request: Request, question: str = Form(...)):
    cached = get_cached_answer(question)

    if cached:
        answer = cached.answer
        sources = cached.sources
    else:
        result = query_rag(qa_chain, question)
        raw_answer = result["result"]
        answer = markdown.markdown(raw_answer)
        sources = list({
            doc.metadata.get("source", "unknown")
            for doc in result["source_documents"]
        })

        new_entry = ChatEntry(question=question, answer=answer, sources=sources)
        chat_history.append(new_entry)
        chat_history[:] = chat_history[-6:]
        save_cache(new_entry)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "answer": answer,
        "sources": sources,
        "history": [entry.to_dict() for entry in chat_history][-5:]
    })

# 🧹 Clear history
@app.post("/clear-history", response_class=HTMLResponse)
def clear_history(request: Request):
    chat_history.clear()
    clear_cache()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "history": [],
        "answer": None,
        "sources": []
    })