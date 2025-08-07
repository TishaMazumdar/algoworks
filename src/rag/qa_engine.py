from src.rag.mcp_llm import McpLLM
from langchain.chains import RetrievalQA
from langchain_core.vectorstores import VectorStoreRetriever


def create_qa_chain(
    retriever: VectorStoreRetriever,
    model_name: str = "mistral"
) -> RetrievalQA:
    """
    Creates a RetrievalQA chain with a custom prompt and retriever.
    """
    llm = McpLLM(
        model=model_name,
        mcp_url="http://localhost:11434/api/chat"
    )


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