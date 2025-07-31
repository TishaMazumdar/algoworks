from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import markdown

from src.rag.qa_engine import create_qa_chain, query_rag
from src.rag.retriever import get_vectorstore_retriever
from src.rag.vector_store import build_vectorstore
from src.models.history import ChatEntry, load_cache, save_cache, clear_cache
from src.loaders.file_loader import load_all_documents
from app.auth_routes import router as auth_router

# Load env vars
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# FastAPI app setup
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(auth_router)
templates = Jinja2Templates(directory="templates")

# History setup
chat_history = load_cache()

# 🧠 Check if a question is already cached
def get_cached_answer(question: str):
    question = question.strip().lower()
    for entry in chat_history:
        if entry.question.strip().lower() == question:
            return entry
    return None

def get_user_folder(user_id: str):
    upload_dir = os.path.join("user_uploads", user_id)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def get_embedding_folder(user_id: str):
    embed_dir = os.path.join("embeddings", user_id)
    os.makedirs(embed_dir, exist_ok=True)
    return embed_dir

# 🏠 Home route (requires login)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")

    toast = request.session.pop("toast", None)

    user_id = user["name"]
    upload_dir = get_user_folder(user_id)
    files = os.listdir(upload_dir) if os.path.exists(upload_dir) else []

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_name": user["name"],
        "toast": toast,
        "files": files  # ✅ Add this line
    })

# 💬 Handle UI-based query asking
@app.post("/ask-ui", response_class=HTMLResponse)
def ask_ui(request: Request, question: str = Form(...)):
    cached = get_cached_answer(question)

    if cached:
        answer = cached.answer
        sources = cached.sources
    else:
        # Fallback to global qa_chain if user hasn’t uploaded
        qa_chain = getattr(request.app.state, "qa_chain", None) or globals().get("qa_chain")
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

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Use username as unique user ID
    user_id = user["name"]  # or user["name"] if you prefer username-based folder

    # Store files in data/<user_id>/filename.pdf
    upload_dir = get_user_folder(user_id)  # Make sure this returns "data/<user_id>"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Load all user documents from their folder
    documents = load_all_documents(upload_dir)

    # Create or update vectorstore for this user
    embed_dir = get_embedding_folder(user_id)  # should return "embeddings/<user_id>"
    os.makedirs(embed_dir, exist_ok=True)
    build_vectorstore(documents, persist_directory=embed_dir)

    # Set retriever + QA chain in app state for querying
    retriever = get_vectorstore_retriever(persist_directory=embed_dir)
    request.app.state.qa_chain = create_qa_chain(retriever)

    request.session["toast"] = f"✅ Uploaded {file.filename} successfully."
    return RedirectResponse("/", status_code=303)