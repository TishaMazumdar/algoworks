from langchain_community.vectorstores import Chroma
from langchain_core.vectorstores import VectorStoreRetriever


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
