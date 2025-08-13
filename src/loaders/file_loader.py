import os
import hashlib
from datetime import datetime
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, UnstructuredExcelLoader
from langchain.docstore.document import Document

def generate_file_id(file_path: str, user_id: str) -> str:
    """Generate a unique file ID based on file path, user, and upload time"""
    content = f"{file_path}_{user_id}_{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()

def add_enhanced_metadata(docs: List[Document], file_path: str, user_id: str, file_type: str) -> List[Document]:
    """Add comprehensive metadata to documents"""
    file_id = generate_file_id(file_path, user_id)
    filename = os.path.basename(file_path)
    upload_timestamp = datetime.now().isoformat()
    
    for i, doc in enumerate(docs):
        doc.metadata.update({
            "source": file_path,
            "filename": filename,
            "file_id": file_id,
            "user_id": user_id,
            "file_type": file_type,
            "upload_timestamp": upload_timestamp,
            "chunk_index": i,
            "total_chunks": len(docs)
        })
    return docs

def load_pdf(file_path: str, user_id: str) -> List[Document]:
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return add_enhanced_metadata(docs, file_path, user_id, "pdf")

def load_docx(file_path: str, user_id: str) -> List[Document]:
    loader = UnstructuredWordDocumentLoader(file_path)
    docs = loader.load()
    return add_enhanced_metadata(docs, file_path, user_id, "docx")

def load_txt(file_path: str, user_id: str) -> List[Document]:
    loader = TextLoader(file_path, encoding='utf-8')
    docs = loader.load()
    return add_enhanced_metadata(docs, file_path, user_id, "txt")

def load_xlsx(file_path: str, user_id: str) -> List[Document]:
    loader = UnstructuredExcelLoader(file_path)
    docs = loader.load()
    return add_enhanced_metadata(docs, file_path, user_id, "xlsx")

def load_all_documents(directory_path: str, user_id: str) -> List[Document]:
    all_docs = []
    for file in os.listdir(directory_path):
        file_path = os.path.abspath(os.path.join(directory_path, file))
        if file.lower().endswith(".pdf"):
            docs = load_pdf(file_path, user_id)
        elif file.lower().endswith(".docx"):
            docs = load_docx(file_path, user_id)
        elif file.lower().endswith(".txt"):
            docs = load_txt(file_path, user_id)
        elif file.lower().endswith(".xlsx"):
            docs = load_xlsx(file_path, user_id)
        else:
            continue
        all_docs.extend(docs)
    return all_docs

def load_single_document(file_path: str, user_id: str) -> List[Document]:
    """Load a single document with enhanced metadata"""
    filename = os.path.basename(file_path).lower()
    
    if filename.endswith(".pdf"):
        return load_pdf(file_path, user_id)
    elif filename.endswith(".docx"):
        return load_docx(file_path, user_id)
    elif filename.endswith(".txt"):
        return load_txt(file_path, user_id)
    elif filename.endswith(".xlsx"):
        return load_xlsx(file_path, user_id)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def get_file_metadata(file_path: str, user_id: str) -> dict:
    """Get file metadata without loading the full document"""
    filename = os.path.basename(file_path)
    file_type = filename.split('.')[-1].lower()
    file_id = generate_file_id(file_path, user_id)
    
    return {
        "filename": filename,
        "file_path": file_path,
        "file_id": file_id,
        "file_type": file_type,
        "user_id": user_id,
        "upload_timestamp": datetime.now().isoformat()
    }