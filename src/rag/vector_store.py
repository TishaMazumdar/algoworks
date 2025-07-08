import os
from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


def split_documents(
    documents: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Document]:
    """
    Splits the input documents into smaller chunks for embedding.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)


def build_vectorstore(
    documents: List[Document],
    persist_directory: str = "embeddings/",
    model_name: str = "llama3"
) -> Chroma:
    """
    Builds and persists a Chroma vector store using Ollama embeddings.
    """
    os.environ["CHROMA_TELEMETRY_ENABLED"] = "FALSE"
    embedding_model = OllamaEmbeddings(model=model_name)

    # Split documents
    chunks = split_documents(documents)

    # Create and persist vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory
    )
    return vectorstore


def load_vectorstore(
    persist_directory: str = "embeddings/",
    model_name: str = "llama3"
) -> Chroma:
    """
    Loads an existing Chroma vector store from disk.
    """
    embedding_model = OllamaEmbeddings(model=model_name)
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model
    )