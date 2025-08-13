from typing import Optional, List
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from src.rag.vector_store import load_vectorstore, search_with_metadata_filter

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

def get_filtered_retriever(
    persist_directory: str = "embeddings/",
    user_id: Optional[str] = None,
    file_types: Optional[List[str]] = None,
    file_ids: Optional[List[str]] = None,
    k: int = 4
) -> VectorStoreRetriever:
    """
    Create a retriever with metadata filtering for faster, targeted search.
    """
    class FilteredRetriever:
        def __init__(self, persist_directory, user_id, file_types, file_ids, k):
            self.persist_directory = persist_directory
            self.user_id = user_id
            self.file_types = file_types
            self.file_ids = file_ids
            self.k = k
        
        def get_relevant_documents(self, query: str) -> List[Document]:
            return search_with_metadata_filter(
                persist_directory=self.persist_directory,
                query=query,
                user_id=self.user_id,
                file_types=self.file_types,
                file_ids=self.file_ids,
                k=self.k
            )
        
        def invoke(self, query: str) -> List[Document]:
            return self.get_relevant_documents(query)
    
    return FilteredRetriever(persist_directory, user_id, file_types, file_ids, k)
