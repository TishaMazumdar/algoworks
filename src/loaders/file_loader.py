import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.docstore.document import Document

def load_pdf(path: str) -> List[Document]:
    loader = PyPDFLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = path
    return docs

def load_docx(path: str) -> List[Document]:
    loader = Docx2txtLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = path
    return docs

def load_all_documents(directory_path: str) -> List[Document]:
    all_docs = []
    for file in os.listdir(directory_path):
        file_path = os.path.abspath(os.path.join(directory_path, file))
        if file.lower().endswith(".pdf"):
            docs = load_pdf(file_path)
        elif file.lower().endswith(".docx"):
            docs = load_docx(file_path)
        else:
            continue
        all_docs.extend(docs)
    return all_docs