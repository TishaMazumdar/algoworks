from src.loaders.pdf_loader import load_all_pdfs
from src.rag.vector_store import build_vectorstore, load_vectorstore
from src.rag.retriever import get_retriever
from src.rag.qa_engine import create_qa_chain, query_rag


def main():
    # === Config ===
    data_dir = "data/"
    persist_dir = "embeddings/"
    model_name = "llama3"

    # === Load documents ===
    print("Loading PDFs...")
    docs = load_all_pdfs(data_dir)
    print(f"Loaded {len(docs)} documents.\n")

    # === Build / Load Vectorstore ===
    print("Building vector store...")
    vectorstore = build_vectorstore(docs, persist_dir, model_name)

    # === Setup Retriever ===
    print("Creating retriever...")
    retriever = get_retriever(vectorstore)

    # === Setup QA Chain ===
    print("Initializing QA system...")
    qa_chain = create_qa_chain(retriever, model_name)

    # === Run Query ===
    while True:
        query = input("\n💬 Enter your question (or type 'exit' to quit):\n> ")
        if query.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        result = query_rag(qa_chain, query)

        print("\n📤 Answer:")
        print(result["result"])

        print("\n📚 Source Documents:")
        for doc in result["source_documents"]:
            print("-", doc.metadata.get("source", "unknown"))
            print(doc.page_content[:300].strip() + "\n---")


if __name__ == "__main__":
    main()