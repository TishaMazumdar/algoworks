from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_core.vectorstores import VectorStoreRetriever
from src.utils.prompts import get_default_prompt


def create_qa_chain(
    retriever: VectorStoreRetriever,
    model_name: str = "mistral"
) -> RetrievalQA:
    """
    Creates a RetrievalQA chain with a custom prompt and retriever.
    """
    llm = OllamaLLM(
        model="mistral",
        system_message="You are a helpful support assistant. Only use the provided context. Do not hallucinate."
    )


    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": get_default_prompt()}
    )
    return qa_chain


def query_rag(chain: RetrievalQA, question: str) -> dict:
    result = chain.invoke({"query": question})
    print("\n--- Retrieved Chunks ---")
    for doc in result['source_documents']:
        print(doc.metadata.get("source", "Unknown source"))
        print(doc.page_content[:300], "\n---")  # First 300 characters
    return result