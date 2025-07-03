from langchain.prompts import PromptTemplate

def get_default_prompt() -> PromptTemplate:
    """
    Returns the default prompt template for the RAG system.
    Ensures the model answers only from the provided context and avoids hallucination.
    """
    template = """
You are a professional support assistant helping customers with accurate, context-specific answers.

Answer the question strictly based on the following documentation:

{context}

Question: {question}

If the answer is not found in the context, respond with:
"I’m sorry, I don’t have enough information to answer that."

Do not attempt to guess or make up an answer.
"""
    return PromptTemplate(
        input_variables=["context", "question"],
        template=template.strip()
    )