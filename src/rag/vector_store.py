import os
from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


def split_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Splits the input documents into smaller chunks for embedding.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)


def build_vectorstore(documents, persist_directory):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    split_docs = splitter.split_documents(documents)

    embedding_model = OllamaEmbeddings(model="mistral")  
    Chroma.from_documents(
        documents=split_docs,
        embedding=embedding_model,
        persist_directory=persist_directory
    )


def load_vectorstore(
    persist_directory: str = "embeddings/",
    model_name: str = "mistral"
) -> Chroma:
    """
    Loads an existing Chroma vector store from disk.
    """
    embedding_model = OllamaEmbeddings(model=model_name)
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model
    )