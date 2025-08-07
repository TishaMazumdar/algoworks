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
from src.models.history import ChatEntry, load_user_cache, save_user_cache, clear_user_cache, get_user_cached_entry
from src.loaders.file_loader import load_all_documents
from app.auth_routes import router as auth_router
from app.mcp_client import ask_mcp  # used as fallback if RAG is not ready

# Load env vars
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# FastAPI app setup
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(auth_router)
templates = Jinja2Templates(directory="templates")

def get_user_folder(user_id: str):
    upload_dir = os.path.join("user_uploads", user_id)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def get_embedding_folder(user_id: str):
    embed_dir = os.path.join("embeddings", user_id)
    os.makedirs(embed_dir, exist_ok=True)
    return embed_dir

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return render_home(request)

@app.post("/ask-ui", response_class=HTMLResponse)
def ask_ui(request: Request, question: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    user_id = user["name"]
    cached = get_user_cached_entry(user_id, question)

    if cached:
        answer = cached.answer
        sources = cached.sources
    else:
        qa_chain = getattr(request.app.state, "qa_chain", None)
        use_rag = qa_chain is not None

        if use_rag:
            try:
                result = query_rag(qa_chain, question)
                raw_answer = result["result"]
                answer = markdown.markdown(raw_answer)
                sources = list({
                    doc.metadata.get("source", "unknown")
                    for doc in result["source_documents"]
                })
            except Exception as e:
                print(f"[RAG ERROR] {e}")
                use_rag = False  # fallback to MCP only

        if not use_rag:
            mcp_result = ask_mcp(question)
            answer = markdown.markdown(mcp_result.get("answer", "No answer."))
            sources = mcp_result.get("sources", [])

        # Save to user cache
        new_entry = ChatEntry(question=question, answer=answer, sources=sources)
        history = load_user_cache(user_id)
        history.append(new_entry)
        history[:] = history[-6:]
        save_user_cache(user_id, new_entry)

    return render_home(request, answer=answer, sources=sources)

@app.post("/clear-history", response_class=HTMLResponse)
def clear_history(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    user_id = user["name"]
    clear_user_cache(user_id)
    return render_home(request)

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    user_id = user["name"]
    upload_dir = get_user_folder(user_id)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Load + build vectorstore
    documents = load_all_documents(upload_dir)
    embed_dir = get_embedding_folder(user_id)
    build_vectorstore(documents, persist_directory=embed_dir)

    # Create retriever + RAG chain
    retriever = get_vectorstore_retriever(persist_directory=embed_dir)
    request.app.state.qa_chain = create_qa_chain(retriever)

    request.session["toast"] = f"✅ Uploaded {file.filename} successfully."
    return RedirectResponse("/", status_code=303)

def render_home(request: Request, answer=None, sources=None):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    user_id = user["name"]
    upload_dir = get_user_folder(user_id)
    files = os.listdir(upload_dir) if os.path.exists(upload_dir) else []

    toast = request.session.pop("toast", None)
    history = load_user_cache(user_id)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_name": user_id,
        "toast": toast,
        "files": files,
        "answer": answer,
        "sources": sources,
        "history": [entry.to_dict() for entry in history][-5:]
    })