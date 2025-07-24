# 🧠 AlgoAnswers - AI-Powered Document QA Assistant

A FastAPI-based Question-Answering app that lets users upload `.pdf`, `.docx`, `.txt`, and `.xlsx` documents and ask questions using natural language. Powered by LangChain, Ollama, and local embeddings for accurate, source-backed answers.

---

## 🚀 Features

- 📄 Upload multiple document types: `.pdf`, `.docx`, `.txt`, `.xlsx`
- 💬 Ask natural language questions
- 📚 Context-aware answers strictly based on uploaded documents
- 🔒 "I don't know" responses for hallucination prevention
- 🧠 LLM-powered responses with citation of source files
- ⚡ FastAPI backend with clean modular architecture

---

## 📁 Folder Structure

```

.
├── app/
│   └── api.py                 # FastAPI routes
├── src/
│   ├── loaders/
│   │   └── file\_loader.py     # Handles .pdf, .docx, .txt, .xlsx loading
│   ├── rag/
│   │   ├── retriever.py       # Embedding & similarity search
│   │   ├── qa\_engine.py       # Core Q\&A logic
│   │   └── vector\_store.py    # ChromaDB vector store
│   └── utils/
│       └── prompts.py         # Custom LangChain prompt template
├── data/                      # Place your documents here
├── test/
│   └── test\_queries.py        # Optional test cases
├── .env                       # Env variables (like model name)
├── requirements.txt
└── main.py                    # Entrypoint

````

---

## ⚙️ Installation

```bash
# 1. Clone the repo
git clone https://github.com/TishaMazumdar/algoworks.git
cd algoworks

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Ollama (if using a local model)
ollama run llama3

# 5. Run the API
python main.py
````

---

## 🔍 Supported File Types

* ✅ PDF (`.pdf`)
* ✅ Word Document (`.docx`)
* ✅ Text File (`.txt`)
* ✅ Excel File (`.xlsx`)

> ❌ `.doc` files are **not** supported.
> ⚠️ `.csv` support coming soon!

---

## 🧪 Sample Usage

Start the server and run the CLI in `main.py`. You’ll be prompted to enter a question after loading documents from the `/data` folder.

```bash
Enter your question (or type 'exit' to quit):
> What are the key features mentioned in the AirPods PRD?

📤 Answer:
- Enhanced touch interactions
- Improved sound quality
- Technological components like H1 chip, Bluetooth 5.2

📚 Source Documents:
- PRD - AirPods Pro.docx
```

---

## 🧠 Tech Stack

* [LangChain](https://www.langchain.com/)
* [Ollama](https://ollama.com/)
* [ChromaDB](https://www.trychroma.com/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Python](https://www.python.org/)

---

## 🛡️ Anti-Hallucination Measures

* ✅ Prompt explicitly instructs the LLM to avoid assumptions.
* ✅ If answer isn't found in the source, response will be:
  *"I’m sorry, I don’t have enough information to answer that."*

---

## 🙌 Acknowledgments

Built with 💛 by [Tisha Mazumdar](https://github.com/TishaMazumdar)

---