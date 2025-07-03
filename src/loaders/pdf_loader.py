import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document

def load_pdf(path: str) -> List[Document]:
    loader = PyPDFLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = path
    return docs

def load_all_pdfs(directory_path: str) -> List[Document]:
    all_docs = []
    for file in os.listdir(directory_path):
        if file.lower().endswith(".pdf"):
            file_path = os.path.abspath(os.path.join(directory_path, file))
            docs = load_pdf(file_path)
            all_docs.extend(docs)
    return all_docs