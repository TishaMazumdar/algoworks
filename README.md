# 🧠 AlgoAnswers - AI-Powered Document QA Assistant

A FastAPI-based Question-Answering application that allows users to upload documents (`.pdf`, `.docx`, `.txt`) and ask questions using natural language. Powered by LangChain, Ollama, and ChromaDB for accurate, context-aware answers with intelligent web search fallback and enhanced user experience.

---

## 🚀 Features

### Core Functionality
- 📄 **Multi-format Document Support**: Upload `.pdf`, `.docx`, and `.txt` files
- 💬 **Natural Language Queries**: Ask questions in plain English
- 🎯 **Context-Aware Responses**: Answers based on uploaded documents with intelligent relevance checking
- 🌐 **Web Search Fallback**: Automatic web search when documents don't contain relevant information
- 🤖 **LLM-Synthesized Web Results**: Ollama Mistral synthesizes web search results into coherent answers
- 📚 **Source Citations**: Clear distinction between document sources and web sources
- 🔗 **Clickable Web Links**: Direct access to external sources with visual indicators

### User Experience
- 🎉 **Enhanced Toast Notifications**: Welcome messages, upload progress, and operation feedback
- ⚡ **Real-time Upload Feedback**: File size display and immediate upload status
- 🗂️ **Enhanced File Management**: File metadata display with chunk counts and unique IDs
- 💾 **Persistent Chat History**: Conversation history per user with easy access
- 👤 **Session-based Authentication**: Secure user management with welcome messages

### Technical Features
- 🔒 **Intelligent Fallback System**: RAG → Web Search → MCP fallback chain
- 📊 **Enhanced Metadata System**: Comprehensive file tracking and management
- ⚡ **Fast API Backend**: Clean, modular FastAPI architecture
- 🌍 **Dual Search APIs**: Serper API (premium) with DuckDuckGo fallback (free)
- 💡 **Smart Relevance Detection**: Automatic determination of when to use web search

---

## 📁 Project Structure

```
algoworks/
├── app/
│   ├── api.py                 # Main FastAPI application with enhanced web search integration
│   ├── auth_routes.py         # Authentication endpoints
│   ├── auth.py                # Authentication utilities
│   └── mcp_client.py          # Model Context Protocol client
├── src/
│   ├── loaders/
│   │   └── file_loader.py     # Enhanced document loading with metadata tracking
│   ├── rag/
│   │   ├── mcp_llm.py         # Custom LangChain LLM wrapper for Ollama
│   │   ├── qa_engine.py       # Core question-answering logic
│   │   ├── retriever.py       # Document retrieval and similarity search
│   │   └── vector_store.py    # ChromaDB vector store with enhanced metadata
│   ├── web_search/
│   │   ├── __init__.py        # Web search module initialization
│   │   └── search_engine.py   # Comprehensive web search with LLM synthesis
│   └── models/
│       ├── history.py         # Chat history management
│       └── users.json         # User data storage
├── templates/
│   ├── auth.html              # Authentication page
│   └── index.html             # Enhanced UI with toast notifications and source distinction
├── chat_cache/                # User conversation cache
├── embeddings/                # ChromaDB vector embeddings with user separation
├── user_uploads/              # Uploaded documents with user-specific folders
├── requirements.txt           # Updated with web search dependencies
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

# Web Search Configuration (Optional)
SERPER_API_KEY=your-serper-api-key-here  # For premium Google search via Serper
# Note: DuckDuckGo fallback works without API key

# Session Configuration
SECRET_KEY=your-secret-key-here

# Application Settings
DEBUG=True
```

**Web Search Setup (Optional):**
- **Serper API**: Sign up at [serper.dev](https://serper.dev) for premium Google search results
- **DuckDuckGo**: Works automatically as fallback - no setup required

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
2. Register/Login with your credentials (enjoy the welcome toast! 🎉)
3. Use the upload interface to add documents
   - Real-time file size display
   - Immediate upload feedback
   - Support for PDF, DOCX, TXT formats
4. View enhanced file metadata with chunk counts

### Asking Questions
1. Type your question in the chat interface
2. The system intelligently:
   - **First**: Searches through uploaded documents
   - **If insufficient**: Automatically searches the web
   - **Synthesizes**: Web results using Ollama Mistral for coherent answers
   - **Displays**: Clear source distinction (📄 documents vs 🌐 web sources)
   - **Provides**: Clickable links for web sources
   - **Maintains**: Conversation history

### Enhanced Features
- **Smart Fallback**: System automatically determines when document information is insufficient
- **Toast Notifications**: Get instant feedback for all operations
- **Source Clarity**: Easily distinguish between your documents and web sources
- **File Management**: Enhanced file display with metadata and easy deletion

### Example Queries
```
"What are the main findings in the research paper?"
"What does the document say about implementation costs?"

# Web search fallback examples:
"What's the current weather in New York?"  # Will search web automatically
"Latest developments in AI technology"     # Will search web if not in documents
"How does quantum computing work?"         # Will provide synthesized web results
```

---

## 🔧 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout

### Document Management
- `POST /upload` - Upload documents with enhanced metadata
- `GET /api/files` - Get user files with metadata
- `DELETE /api/files/{filename}` - Delete files by filename
- `DELETE /api/files/by-id/{file_id}` - Delete files by unique ID
- `GET /` - Main application interface with enhanced UI

### Question-Answering & Search
- `POST /ask-ui` - Submit questions with intelligent RAG + Web Search fallback

---

## 🏗️ Architecture

### Components

1. **FastAPI Backend** (`app/api.py`)
   - Enhanced HTTP request/response handling
   - Session-based user authentication with welcome toasts
   - Intelligent RAG + Web Search coordination
   - Toast notification system

2. **Document Processing** (`src/loaders/`)
   - Multi-format document loading with enhanced metadata
   - User-specific file management
   - Chunk counting and file tracking

3. **Enhanced RAG System** (`src/rag/`)
   - Vector embeddings with ChromaDB and user filtering
   - Intelligent relevance detection
   - Smart similarity search and retrieval
   - Custom Ollama LLM integration

4. **Web Search Integration** (`src/web_search/`)
   - Serper API integration for premium Google search
   - DuckDuckGo fallback for free search
   - Ollama Mistral synthesis of web results
   - Smart fallback decision making

5. **User Management** (`src/models/`)
   - Enhanced session handling
   - Improved chat history persistence
   - User-specific data isolation

### Data Flow
1. **Document Upload** → Enhanced Metadata → Text Extraction → Chunking → User-Filtered Embeddings → Vector Store
2. **Question Processing**:
   - **RAG First**: Question → Embedding → Similarity Search → Relevance Check
   - **Web Fallback**: If insufficient → Web Search → LLM Synthesis → Formatted Response
   - **Final Output**: Unified response with clear source attribution

---

## 🛠️ Technical Details

### Technologies Used
- **Backend**: FastAPI, Uvicorn
- **LLM Framework**: LangChain, Ollama (Mistral for synthesis)
- **Vector Database**: ChromaDB with enhanced metadata
- **Web Search**: Serper API, DuckDuckGo API
- **Document Processing**: PyPDF, python-docx, unstructured
- **Frontend**: Enhanced HTML, JavaScript, CSS with toast notifications
- **HTTP Client**: Requests for web search APIs
- **Authentication**: Session-based with FastAPI

### Model Integration
The application uses multiple LLM integrations:
- **Custom `McpLLM`**: Primary interface with Ollama for document QA
- **Web Search Synthesis**: Ollama Mistral for synthesizing web search results
- **Enhanced Features**:
  - Custom prompt templates
  - Intelligent response formatting
  - Error handling and graceful fallbacks
  - Local model execution for privacy

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

2. **Web Search Not Working**
   ```bash
   # Check if Serper API key is set (optional)
   echo $SERPER_API_KEY
   
   # DuckDuckGo fallback should work without API key
   # Check internet connection
   ```

3. **Module Import Errors**
   ```bash
   # Ensure virtual environment is activated
   pip install -r requirements.txt
   ```

4. **Document Upload Issues**
   - Check file permissions in `user_uploads/` directory
   - Verify supported file formats (PDF, DOCX, TXT)
   - Ensure files are not corrupted
   - Check toast notifications for specific error messages

5. **Vector Store Issues**
   ```bash
   # Clear embeddings cache if needed
   rm -rf embeddings/
   ```

6. **Toast Notifications Not Appearing**
   - Check browser console for JavaScript errors
   - Ensure JavaScript is enabled
   - Try refreshing the page

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

---

## 🙏 Acknowledgments

- **LangChain** for the RAG framework and LLM integrations
- **Ollama** for local LLM execution and Mistral model
- **ChromaDB** for vector storage and similarity search
- **FastAPI** for the excellent web framework
- **Serper** for premium Google search API
- **DuckDuckGo** for free web search fallback

Built with 💛 by [Tisha Mazumdar](https://github.com/TishaMazumdar)

---