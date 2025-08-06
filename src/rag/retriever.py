from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from src.rag.vector_store import load_vectorstore

def get_retriever(
    vectorstore: Chroma,
    search_type: str = "similarity",
    k: int = 8
) -> VectorStoreRetriever:
    """
    Returns a configured retriever from the vectorstore.
    """
    retriever = vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs={
            "k": k
        }
    )
    return retriever

def get_vectorstore_retriever(persist_directory: str) -> VectorStoreRetriever:
    """
    Loads user-specific vectorstore and returns retriever.
    """
    vectorstore = load_vectorstore(persist_directory=persist_directory)
    return get_retriever(vectorstore)