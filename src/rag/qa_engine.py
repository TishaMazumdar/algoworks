from src.rag.mcp_llm import McpLLM
from langchain.chains import RetrievalQA
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from typing import List


class CustomRetrieverWrapper(BaseRetriever):
    """Wrapper to make our custom retriever compatible with LangChain"""
    
    def __init__(self, custom_retriever):
        super().__init__()
        self._custom_retriever = custom_retriever
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        return self._custom_retriever.get_relevant_documents(query)


def create_qa_chain(
    retriever,  # Can be VectorStoreRetriever or our custom retriever
    model_name: str = "mistral"
) -> RetrievalQA:
    """
    Creates a RetrievalQA chain with a custom prompt and retriever.
    """
    llm = McpLLM(
        model=model_name,
        mcp_url="http://localhost:11434/api/chat"
    )

    # Wrap custom retriever if needed
    if not isinstance(retriever, VectorStoreRetriever):
        retriever = CustomRetrieverWrapper(retriever)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain


def query_rag(chain: RetrievalQA, question: str) -> dict:
    result = chain.invoke({"query": question})
    print("\n--- Retrieved Chunks ---")
    for doc in result['source_documents']:
        print(doc.metadata.get("source", "Unknown source"))
        print(doc.page_content[:300], "\n---")  # First 300 characters
    return result