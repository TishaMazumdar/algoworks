from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_core.vectorstores import VectorStoreRetriever
from src.utils.prompts import get_default_prompt


def create_qa_chain(
    retriever: VectorStoreRetriever,
    model_name: str = "llama3"
) -> RetrievalQA:
    """
    Creates a RetrievalQA chain with a custom prompt and retriever.
    """
    llm = OllamaLLM(model=model_name)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": get_default_prompt()}
    )
    return qa_chain


def query_rag(
    chain: RetrievalQA,
    question: str
) -> dict:
    """
    Queries the QA chain with a given question.
    """
    return chain.invoke({"query": question})