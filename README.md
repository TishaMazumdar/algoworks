# 🧠 AlgoAnswers - AI-Powered Document QA Assistant

A FastAPI-based Question-Answering application that allows users to upload documents (`.pdf`, `.docx`, `.txt`) and ask questions using natural language. Powered by LangChain, Ollama, and ChromaDB for accurate, context-aware answers with source citations.

---

## 🚀 Features

- 📄 **Multi-format Document Support**: Upload `.pdf`, `.docx`, and `.txt` files
- 💬 **Natural Language Queries**: Ask questions in plain English
- 🎯 **Context-Aware Responses**: Answers strictly based on uploaded documents
- 🔒 **Hallucination Prevention**: Returns "I don't know" when information isn't available
- 📚 **Source Citations**: Responses include references to source documents
- 👤 **User Authentication**: Session-based user management
- 💾 **Chat History**: Persistent conversation history per user
- ⚡ **Fast API Backend**: Clean, modular FastAPI architecture
- 🤖 **Ollama Integration**: Local LLM processing with custom MCP client

---

## 📁 Project Structure

```
algoworks/
├── app/
│   ├── api.py                 # Main FastAPI application and routes
│   ├── auth_routes.py         # Authentication endpoints
│   ├── auth.py                # Authentication utilities
│   └── mcp_client.py          # Model Context Protocol client
├── src/
│   ├── loaders/
│   │   └── file_loader.py     # Document loading for multiple formats
│   ├── rag/
│   │   ├── mcp_llm.py         # Custom LangChain LLM wrapper for Ollama
│   │   ├── qa_engine.py       # Core question-answering logic
│   │   ├── retriever.py       # Document retrieval and similarity search
│   │   └── vector_store.py    # ChromaDB vector store management
│   └── models/
│       ├── history.py         # Chat history management
│       └── users.json         # User data storage
├── templates/
│   ├── auth.html              # Authentication page
│   └── index.html             # Main application interface
├── chat_cache/                # User conversation cache
├── embeddings/                # ChromaDB vector embeddings
├── user_uploads/              # Uploaded documents storage
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+** installed
2. **Ollama** installed and running locally
   ```bash
   # Install Ollama (visit https://ollama.ai for platform-specific instructions)
   # Pull a model (e.g., Mistral)
   ollama pull mistral
   ```
3. **Git** (for cloning the repository)

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/TishaMazumdar/algoworks.git
cd algoworks
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Ollama Configuration
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434

# Session Configuration
SECRET_KEY=your-secret-key-here

# Application Settings
DEBUG=True
```

---

## 🚀 Running the Application

### 1. Start Ollama Server
Ensure Ollama is running on your system:
```bash
# Check if Ollama is running
ollama list

# If not running, start it (usually starts automatically after installation)
ollama serve
```

### 2. Start the FastAPI Application
```bash
# Development mode with auto-reload
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

### 3. Access the Application
Open your browser and navigate to:
- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## 💻 Usage

### Document Upload
1. Navigate to the main page
2. Register/Login with your credentials
3. Use the upload interface to add documents
4. Supported formats: PDF, DOCX, TXT

### Asking Questions
1. Type your question in the chat interface
2. The system will:
   - Search through uploaded documents
   - Generate context-aware responses
   - Provide source citations
   - Maintain conversation history

### Example Queries
```
"What are the main findings in the research paper?"
"Summarize the financial data from the Excel file"
"What does the document say about implementation costs?"
```

---

## 🔧 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout

### Document Management
- `POST /upload` - Upload documents
- `GET /` - Main application interface

### Question-Answering
- `POST /ask` - Submit questions and get answers

---

## 🏗️ Architecture

### Components

1. **FastAPI Backend** (`app/api.py`)
   - Handles HTTP requests and responses
   - Manages user sessions and authentication
   - Coordinates document processing and QA

2. **Document Processing** (`src/loaders/`)
   - Multi-format document loading
   - Text extraction and preprocessing

3. **RAG System** (`src/rag/`)
   - Vector embeddings with ChromaDB
   - Similarity search and retrieval
   - Custom Ollama LLM integration
   - Question-answering pipeline

4. **User Management** (`src/models/`)
   - Session handling
   - Chat history persistence
   - User data management

### Data Flow
1. **Document Upload** → Text Extraction → Chunking → Embeddings → Vector Store
2. **Question** → Embedding → Similarity Search → Context Retrieval → LLM → Response

---

## 🛠️ Technical Details

### Technologies Used
- **Backend**: FastAPI, Uvicorn
- **LLM Framework**: LangChain, Ollama
- **Vector Database**: ChromaDB
- **Document Processing**: PyPDF, python-docx, unstructured
- **Frontend**: HTML, JavaScript, CSS
- **Authentication**: Session-based with FastAPI

### Model Integration
The application uses a custom `McpLLM` class that interfaces with Ollama's API, providing:
- Custom prompt templates
- Response formatting
- Error handling and fallbacks
- Local model execution

---

## 🔍 Troubleshooting

### Common Issues

1. **Connection Error to Ollama**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama if needed
   ollama serve
   ```

2. **Module Import Errors**
   ```bash
   # Ensure virtual environment is activated
   pip install -r requirements.txt
   ```

3. **Document Upload Issues**
   - Check file permissions in `user_uploads/` directory
   - Verify supported file formats
   - Ensure files are not corrupted

4. **Vector Store Issues**
   ```bash
   # Clear embeddings cache if needed
   rm -rf embeddings/
   ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **LangChain** for the RAG framework
- **Ollama** for local LLM execution
- **ChromaDB** for vector storage
- **FastAPI** for the web framework
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

> ❌ `.doc` files are **not** supported.
> ⚠️ `.csv` and `.xlsx` support coming soon!

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