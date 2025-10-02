# PDF RAG Application

A Retrieval-Augmented Generation (RAG) application that allows you to upload PDF documents, index them into a vector database, and ask questions about their content using AI.

## Features

- 📄 PDF document ingestion and chunking
- 🔍 Semantic search using vector embeddings
- 🤖 AI-powered question answering with context
- 🎯 Powered by Google Gemini 2.0 Flash for embeddings and generation
- 📊 Vector storage with Qdrant
- 🔄 Workflow orchestration with Inngest
- 🎨 User-friendly interface with Streamlit

## Tech Stack

- **Python 3.11+**
- **UV** - Fast Python package installer
- **Streamlit** - Web interface
- **Inngest** - Workflow orchestration and observability
- **Qdrant** - Vector database
- **Google Generative AI** - Embeddings and LLM
- **FastAPI** - Backend API
- **LlamaIndex** - Document processing

## Prerequisites

- Python 3.11 or higher
- Docker (for Qdrant)
- Google Gemini API key
- UV package manager

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd pdf-rag-app

2. Install UV (if not already installed)

3. Create and activate virtual environment
    uv venv
    source .venv/bin/activate  # On Mac/Linux
    # or
    .venv\Scripts\activate  # On Windows

4. Install dependencies
    uv pip install -r requirements.txt

5. Set up environment variables
Create a .env file in the project root:
    GEMINI_API_KEY=your_gemini_api_key_here

Setup Qdrant Vector Database
Option 1: Using Docker (Recommended)
    docker run -d --name qdrant_vec_DB -p 6333:6333 -v "./qdrant_storage:/qdrant/storage" qdrant/qdrant 
    (change the file path in windows)

Setup Inngest Dev Server
1. Install Inngest CLI, Setup
     npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery

Running the Application
    1. Start the FastAPI backend
    In one terminal:
    uv run uvicorn main:app --reload

2. Start the Streamlit frontend
    In another terminal:    
    uv run streamlit run streamlit_app.py


3. Verify all services are running
    FastAPI Backend: http://localhost:8000
    Streamlit Frontend: http://localhost:8501
    Inngest Dev Server: http://localhost:8288
    Qdrant Dashboard: http://localhost:6333/dashboard
Usage
1. Upload a PDF
    Open the Streamlit app at http://localhost:8501
    Click "Browse files" and select a PDF document
    Wait for the ingestion to complete
    The PDF will be chunked, embedded, and stored in Qdrant
2. Ask Questions
    In the "Ask a question about your PDFs" section
    Enter your question
    Adjust the number of chunks to retrieve (default: 5)
    Click "Ask"
    The AI will search relevant context and generate an answer

Project Structure
pdf-rag-app/
├── main.py                 # FastAPI app and Inngest functions
├── streamlit_app.py        # Streamlit UI
├── data_loader.py          # PDF loading and embedding
├── vector_db.py            # Qdrant storage class
├── custom_types.py         # Pydantic models
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── uploads/                # Uploaded PDFs (created automatically)
└── qdrant_storage/         # Qdrant data (created automatically)



Architecture:
┌─────────────┐
│  Streamlit  │
│     UI      │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────┐
│   FastAPI   │────▶│  Inngest │
│   Backend   │     │    Dev   │
└──────┬──────┘     └────┬─────┘
       │                 │
       ▼                 ▼
┌─────────────┐     ┌──────────┐
│   Qdrant    │     │  Gemini  │
│  Vector DB  │     │   API    │
└─────────────┘     └──────────┘


Key Components
Ingestion Workflow (rag_ingest_pdf)
    1.Loads PDF document
    2.Chunks text into manageable pieces
    3.Generates embeddings using Google's text-embedding-004 (768 dimensions)
    4.Stores vectors in Qdrant with metadata
Query Workflow (rag_query_pdf_ai)
    1.Embeds user question
    2.Performs semantic search in Qdrant
    3.Retrieves top-k relevant chunks
    4.Sends context to Gemini 2.0 Flash
    5.Returns AI-generated answer with sources
<img width="1440" height="900" alt="Screenshot 2025-10-02 at 8 26 34 AM" src="https://github.com/user-attachments/assets/8a39ccd3-64d8-4109-a444-5f9bbe603498" />

