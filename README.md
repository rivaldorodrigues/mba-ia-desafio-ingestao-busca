# Semantic Ingestion and Search with LangChain and Postgres

A RAG (Retrieval-Augmented Generation) system that reads a PDF file, stores its chunks as vectors in PostgreSQL with pgVector, and allows users to ask questions via CLI receiving answers based exclusively on the document's content.

---

## Technologies

- **Python 3.12**
- **LangChain** — orchestration of the ingestion and search pipeline
- **PostgreSQL + pgVector** — vector database for storage and similarity search
- **Docker & Docker Compose** — database execution
- **OpenAI** (`text-embedding-3-small` + `gpt-4o-mini`) or **Gemini** (`models/embedding-001` + `gemini-2.5-flash-lite`)

---

## Project Structure

```
├── docker-compose.yml        # PostgreSQL with pgVector
├── requirements.txt          # Pinned dependencies
├── .env.example              # Environment variables template
├── src/
│   ├── ingest.py             # Reads the PDF, creates chunks and saves embeddings to the database
│   ├── search.py             # Prompt template and similarity search
│   └── chat.py               # Interactive CLI for questions and answers
├── assets/
│   └── document.pdf          # Sample PDF for ingestion
└── README.md
```

---

## Prerequisites

- Python 3.12+
- Docker and Docker Compose installed
- API key from **OpenAI** or **Google (Gemini)**

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd mba-ia-desafio-ingestao-busca
```

### 2. Create the `.env` file

Copy the template and fill in the variables:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# OpenAI (choose OpenAI or Gemini)
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Gemini (alternative to OpenAI)
GOOGLE_API_KEY=AI...
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# PGVector settings
PG_VECTOR_COLLECTION_NAME=documents

# Path to the PDF to be ingested
PDF_PATH=assets/document.pdf
```

> **Note:** fill in only the keys for the provider you intend to use (OpenAI **or** Gemini). Leave the others blank.

### 3. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 4. Install dependencies

With **pip**:

```bash
pip install -r requirements.txt
```

With **uv** (faster):

```bash
uv sync
```

---

## Execution Order

### 1. Start the database

```bash
docker compose up -d
```

Wait for the container to become healthy. The `docker-compose.yml` automatically provisions the `pgvector` extension via the `bootstrap_vector_ext` service.

### 2. Run the PDF ingestion

```bash
python src/ingest.py
```

This script will:
- Load the PDF defined in `PDF_PATH`
- Split the content into chunks of **1000 characters** with an overlap of **150**
- Generate embeddings for each chunk
- Store the vectors in PostgreSQL via `PGVector`

### 3. Start the chat

```bash
python src/chat.py
```

---

## Usage Example

```
Ask your question (or 'exit' to quit):

QUESTION: What is the revenue of SuperTechIABrazil?
ANSWER: The revenue was 10 million reais.

QUESTION: What is the capital of France?
ANSWER: I do not have the necessary information to answer your question.

QUESTION: exit
```

---

## Important Considerations

- **The model answers only based on the ingested PDF.** Questions outside the document's context return a default "no information" message — the model never uses external knowledge.
- **Ingestion is not idempotent by default:** re-running `ingest.py` with the same collection and document will create duplicate entries in the database. To re-ingest from scratch, remove the Docker volume first:
  ```bash
  docker compose down -v
  docker compose up -d
  ```
- **API cost:** each `ingest.py` run consumes embedding tokens. For large documents, run ingestion only once.
- **Free-tier rate limits** for Gemini models change frequently; check the [official documentation](https://ai.google.dev/pricing) if you encounter quota errors.
- The database binds to port **5432**. Make sure it is free before running `docker compose up`.
- The similarity search retrieves the **top 10** most relevant chunks (`k=10`) to build the context passed to the LLM.
