# 🎓 TutorRAG: AI-Powered Teaching Assistant

TutorRAG is a sophisticated **Retrieval-Augmented Generation (RAG)** platform designed to bridge the gap between static educational materials and interactive learning. It allows teachers to upload curriculum-specific documents and empowers students to interact with those materials through AI-driven chat and automated quiz generation.

### 🔗 Deployed Links

- **Frontend (Streamlit):** [https://rag-teaching-assistant-nikg6gzewcy6m5rce8wz8l.streamlit.app](https://rag-teaching-assistant-nikg6gzewcy6m5rce8wz8l.streamlit.app)
- **Backend (FastAPI):** Deployed on Render
- **GitHub Repository:** [https://github.com/ranak8811/RAG-Teaching-Assistant.git](https://github.com/ranak8811/RAG-Teaching-Assistant.git)

---

## 🌟 Key Features

### 👨‍🏫 For Teachers

- **Document Indexing:** Upload PDF textbooks, notes, or research papers.
- **Grade-Level Targeting:** Assign specific grades to documents to ensure content relevance.
- **Knowledge Base Management:** Automatically process and chunk documents for the RAG pipeline.

### 🎓 For Students

- **Contextual Chat:** Ask questions and get answers derived _strictly_ from uploaded educational materials.
- **Source Transparency:** Every AI response includes citations from the original documents (Source name & Page numbers).
- **AI Quiz Generator:** Generate custom multiple-choice quizzes based on specific topics from the knowledge base.
- **Performance Tracking:** Submit quizzes for instant grading and view historical performance.

### 🔒 Core System

- **Role-Based Access Control (RBAC):** Secure authentication for Students and Teachers.
- **Smart Filtering:** Students only see content relevant to their grade level or marked as "Public".

---

## 🛠️ Tech Stack

| Layer                | Technology                                                            |
| -------------------- | --------------------------------------------------------------------- |
| **Frontend**         | [Streamlit](https://streamlit.io/)                                    |
| **Backend**          | [FastAPI](https://fastapi.tiangolo.com/), Uvicorn                     |
| **LLM Inference**    | [Groq LPU](https://groq.com/) (Llama-3.3-70b-versatile)               |
| **Embeddings**       | [Google Gemini](https://ai.google.dev/) (models/gemini-embedding-001) |
| **Vector Database**  | [Pinecone](https://www.pinecone.io/)                                  |
| **Primary Database** | [MongoDB](https://www.mongodb.com/) (Atlas)                           |
| **Orchestration**    | [LangChain](https://www.langchain.com/)                               |
| **Authentication**   | BCrypt Hashing                                                        |

---

## 🚀 How It Works (RAG Pipeline)

TutorRAG uses a **Dual-Storage Strategy** for maximum efficiency:

1.  **Ingestion:** When a teacher uploads a PDF, it is parsed and split into 500-character chunks using `RecursiveCharacterTextSplitter`.
2.  **Embedding:** Each chunk is converted into a high-dimensional vector using Google's Gemini Embedding model.
3.  **Storage:**
    - **Pinecone:** Stores the vectors + metadata (role, grade, source) for fast similarity search.
    - **MongoDB:** Stores the actual text content mapped to IDs for high-fidelity retrieval.
4.  **Retrieval:** When a student asks a question, the system embeds the query, finds the top 5 relevant vectors in Pinecone (filtered by grade), and fetches the corresponding text from MongoDB.
5.  **Generation:** The retrieved context + the original question are sent to the **Llama-3.3-70b** model via Groq to generate a precise, grounded answer.

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.9+
- MongoDB Atlas Account
- Pinecone API Key
- Groq API Key
- Google AI Studio (Gemini) API Key

### 1. Clone the Repository

```bash
git clone https://github.com/ranak8811/RAG-Teaching-Assistant.git
cd RAG-Teaching-Assistant
```

### 2. Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the `server/` directory:

```env
# API Keys
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key

# Database
MONGO_URI=your_mongodb_atlas_uri
DB_NAME=your_database_name

# Configuration
PINECONE_INDEX_NAME=tutor-rags
PINECONE_ENV=us-east-1
```

### 4. Frontend Setup

```bash
# Navigate to client directory
cd ../client

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` in `client/`:

```env
BACKEND_URL=http://localhost:8000
```

---

## 🏃 How to Run

### Start the Backend

```bash
cd server
uvicorn main:app --reload
```

### Start the Frontend

```bash
cd client
streamlit run main.py
```

---

## 📁 Project Structure

```text
.
├── client/                # Streamlit Frontend
│   ├── main.py            # UI Logic & Routing
│   ├── assets/            # UI Images
│   └── requirements.txt
├── server/                # FastAPI Backend
│   ├── main.py            # API Entry Point
│   ├── auth/              # User Authentication Logic
│   ├── chat/              # RAG Query & Quiz Logic
│   ├── config/            # DB Connections (MongoDB)
│   ├── docs/              # Vectorstore & PDF Processing
│   ├── upload_docs/       # Temporary storage for PDFs
│   └── requirements.txt
└── requirements.txt       # Global dependencies
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

**Built with ❤️ for better education.**
