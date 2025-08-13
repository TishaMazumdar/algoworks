from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import markdown

from src.rag.qa_engine import create_qa_chain, query_rag
from src.rag.retriever import get_vectorstore_retriever, get_filtered_retriever
from src.rag.vector_store import (
    build_vectorstore, delete_documents_by_file_id, 
    delete_documents_by_filename, get_user_files,
    add_documents_to_vectorstore, load_vectorstore
)
from src.models.history import ChatEntry, load_user_cache, save_user_cache, clear_user_cache, get_user_cached_entry
from src.loaders.file_loader import load_all_documents, load_single_document, get_file_metadata
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

    # Save the uploaded file
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        request.session["toast"] = f"❌ Error saving {file.filename}: {str(e)}"
        return RedirectResponse("/", status_code=303)

    # Load the single document with enhanced metadata
    try:
        print(f"Loading document: {file.filename} for user: {user_id}")
        documents = load_single_document(file_path, user_id)
        print(f"Successfully loaded {len(documents)} document chunks")
        
        embed_dir = get_embedding_folder(user_id)
        print(f"Embedding directory: {embed_dir}")
        
        # Check if vectorstore exists, if so add to it, otherwise create new
        vectorstore_path = os.path.join(embed_dir, "chroma.sqlite3")
        if os.path.exists(vectorstore_path):
            print("Adding to existing vectorstore...")
            vectorstore = load_vectorstore(embed_dir)
            add_documents_to_vectorstore(vectorstore, documents)
        else:
            print("Creating new vectorstore...")
            vectorstore = build_vectorstore(documents, persist_directory=embed_dir)

        # Create retriever with user filtering for better performance
        print("Creating filtered retriever...")
        retriever = get_filtered_retriever(
            persist_directory=embed_dir,
            user_id=user_id
        )
        request.app.state.qa_chain = create_qa_chain(retriever)
        print("QA chain created successfully")

        request.session["toast"] = f"✅ Uploaded {file.filename} successfully with enhanced metadata."
        
    except Exception as e:
        # Clean up file if processing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        
        print(f"Error processing {file.filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        request.session["toast"] = f"❌ Error processing {file.filename}: {str(e)}"
        
    return RedirectResponse("/", status_code=303)

@app.get("/api/files")
def get_user_files_api(request: Request):
    """Get list of uploaded files for the current user with metadata."""
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    user_id = user["name"]
    embed_dir = get_embedding_folder(user_id)
    
    try:
        files = get_user_files(embed_dir, user_id)
        return JSONResponse({"files": files})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.delete("/api/files/{filename}")
def delete_file(request: Request, filename: str):
    """Delete a file and its embeddings."""
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    user_id = user["name"]
    upload_dir = get_user_folder(user_id)
    embed_dir = get_embedding_folder(user_id)
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Delete physical file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete embeddings
        success = delete_documents_by_filename(embed_dir, filename, user_id)
        
        if success:
            # Rebuild the QA chain with remaining documents
            if os.path.exists(embed_dir):
                retriever = get_filtered_retriever(
                    persist_directory=embed_dir,
                    user_id=user_id
                )
                request.app.state.qa_chain = create_qa_chain(retriever)
            else:
                request.app.state.qa_chain = None
            
            return JSONResponse({"message": f"Successfully deleted {filename}"})
        else:
            return JSONResponse({"error": f"Failed to delete embeddings for {filename}"}, status_code=500)
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.delete("/api/files/by-id/{file_id}")
def delete_file_by_id(request: Request, file_id: str):
    """Delete a file by its unique file_id."""
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    user_id = user["name"]
    embed_dir = get_embedding_folder(user_id)
    
    try:
        success = delete_documents_by_file_id(embed_dir, file_id)
        
        if success:
            # Rebuild the QA chain
            retriever = get_filtered_retriever(
                persist_directory=embed_dir,
                user_id=user_id
            )
            request.app.state.qa_chain = create_qa_chain(retriever)
            
            return JSONResponse({"message": f"Successfully deleted file with ID {file_id}"})
        else:
            return JSONResponse({"error": f"Failed to delete file with ID {file_id}"}, status_code=500)
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

def render_home(request: Request, answer=None, sources=None):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    user_id = user["name"]
    upload_dir = get_user_folder(user_id)
    embed_dir = get_embedding_folder(user_id)
    
    # Get enhanced file information from vector store
    try:
        file_metadata = get_user_files(embed_dir, user_id)
        # Also get physical files for fallback
        physical_files = os.listdir(upload_dir) if os.path.exists(upload_dir) else []
    except Exception as e:
        print(f"Error getting file metadata: {e}")
        file_metadata = []
        physical_files = os.listdir(upload_dir) if os.path.exists(upload_dir) else []

    toast = request.session.pop("toast", None)
    history = load_user_cache(user_id)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_name": user_id,
        "toast": toast,
        "files": physical_files,  # Keep for backward compatibility
        "file_metadata": file_metadata,  # Enhanced metadata
        "answer": answer,
        "sources": sources,
        "history": [entry.to_dict() for entry in history][-5:]
    })