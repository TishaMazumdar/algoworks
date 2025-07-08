from langchain_community.vectorstores import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from src.rag.vector_store import load_vectorstore


def get_retriever(
    vectorstore: Chroma,
    search_type: str = "mmr",
    k: int = 3,
    fetch_k: int = 12
) -> VectorStoreRetriever:
    """
    Returns a configured retriever from the vectorstore.
    """
    retriever = vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k
        }
    )
    return retriever

def get_vectorstore_retriever() -> VectorStoreRetriever:
    """
    Loads persisted vectorstore and returns retriever.
    """
    vectorstore = load_vectorstore()
    return get_retriever(vectorstore)