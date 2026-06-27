# AI Document Q&A System (RAG)

A full-stack Retrieval-Augmented Generation application for PDF question answering. Users can upload PDF files, index semantic content into ChromaDB, and query documents with Gemini-powered responses.

## Project Structure

- `backend/` - FastAPI backend, AI pipeline, database models, ChromaDB integration
- `frontend/` - Next.js 15 client application with TypeScript and TailwindCSS
- `docker-compose.yml` - Local orchestration for Postgres, ChromaDB, backend, and frontend

## Backend

### Core Features

- JWT authentication
- PDF upload and validation
- PDF text extraction with PyPDF
- Chunking using `RecursiveCharacterTextSplitter`
- Gemini embeddings and chat via LangChain
- ChromaDB vector storage with metadata
- Semantic search and RAG answer generation
- Citation metadata and multi-document querying
- Chat history persistence
- Document summarization endpoint

### Run locally

1. Copy the sample environment template: `cp backend/.env.template backend/.env`
2. Set `GEMINI_API_KEY` and any other production values inside `backend/.env`
3. Start the backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend

### Features

- Login/Register pages
- Dashboard and document listing
- PDF upload UI
- Chat interface with citations
- Responsive dark mode layout

### Run locally

```bash
cd frontend
npm install
npm run dev
```

## Docker

Bring up all services with:

```bash
docker-compose up --build
```

The frontend will be available at `http://localhost:3000`, and the backend at `http://localhost:8000`.

## API Endpoints

### Authentication

- `POST /auth/register` - register a new user
- `POST /auth/login` - obtain JWT token

### Documents

- `POST /documents/upload` - upload a PDF
- `GET /documents/` - list user documents
- `POST /documents/{document_id}/summary` - generate document summary

### Chat

- `POST /chat/query` - ask a question across uploaded documents
- `GET /chat/history` - retrieve chat history
- `DELETE /chat/history` - clear chat history

## Environment Variables

- `DATABASE_URL` - Postgres connection string
- `JWT_SECRET` - JWT signing secret
- `JWT_ALGORITHM` - signing algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES` - token lifetime
- `GEMINI_API_KEY` - Gemini API key
- `GEMINI_MODEL` - Gemini chat model
- `GEMINI_EMBEDDING_MODEL` - Gemini embedding model
- `ALLOWED_ORIGINS` - CORS allowed origin(s)

## Testing

Run backend tests from the `backend/` directory:

```bash
pytest
```

## Deployment

1. Build containers with Docker Compose
2. Provide secrets via environment variables or a vault
3. Persist uploads and Chroma data using mounted volumes
4. Set `ALLOWED_ORIGINS` to your production frontend URL

## Notes

- The backend uses async FastAPI endpoints with PostgreSQL and SQLAlchemy
- The vector database persists locally under `backend/chroma_db`
- The chatbot is grounded in retrieved text chunks to reduce hallucinations
