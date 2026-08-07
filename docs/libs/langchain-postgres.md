# langchain-postgres

**Package**: `langchain-postgres`
**Repo**: https://github.com/langchain-ai/langchain-postgres
**Version used**: `>=0.0.17`

LangChain abstractions backed by PostgreSQL. Provides:
- `PGVector` — legacy vector store (synchronous, SQLAlchemy-based)
- `PGVectorStore` — new async-first vector store with `PGEngine`
- `PostgresChatMessageHistory` — persist chat history in Postgres

Requires PostgreSQL with the [`pgvector`](https://github.com/pgvector/pgvector) extension enabled.

---

## Docker — Local PostgreSQL with pgvector

```bash
docker run --name pgvector-db \
  -e POSTGRES_USER=langchain \
  -e POSTGRES_PASSWORD=langchain \
  -e POSTGRES_DB=langchain \
  -p 6024:5432 \
  -d pgvector/pgvector:pg16
```

---

## PGVector (legacy, sync)

The original vector store class. Works with synchronous psycopg connections.

### Initialize from documents

```python
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

embeddings = OpenAIEmbeddings()

vectorstore = PGVector.from_documents(
    documents=docs,           # list[Document]
    embedding=embeddings,
    collection_name="my_docs",
    connection=CONNECTION_STRING,
    use_jsonb=True,           # recommended for metadata filtering
)
```

### Initialize empty, add later

```python
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="my_docs",
    connection=CONNECTION_STRING,
    use_jsonb=True,
)

vectorstore.add_documents(docs)
```

### Similarity search

```python
# Basic similarity search
results = vectorstore.similarity_search("What is RAG?", k=4)

# With score
results_with_score = vectorstore.similarity_search_with_score("What is RAG?", k=4)
for doc, score in results_with_score:
    print(f"Score: {score:.4f} | {doc.page_content[:80]}")

# With metadata filter
results = vectorstore.similarity_search(
    "What is RAG?",
    k=4,
    filter={"source": "document.pdf"},
)
```

### Use as retriever

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",   # "similarity" | "mmr" | "similarity_score_threshold"
    search_kwargs={"k": 4},
)

# In a chain
docs = retriever.invoke("What is the document about?")
```

---

## PGVectorStore (new, async-first)

Newer class with explicit engine management and async support.

### Initialize engine and store

```python
from langchain_postgres import PGEngine, PGVectorStore
from langchain_core.embeddings import DeterministicFakeEmbedding  # replace with real embedding

CONNECTION_STRING = "postgresql+asyncpg://langchain:langchain@localhost:6024/langchain"
TABLE_NAME = "my_doc_collection"
VECTOR_SIZE = 1536  # must match the embedding model's output dimension

engine = PGEngine.from_connection_string(url=CONNECTION_STRING)

# Create the table (run once)
engine.init_vectorstore_table(table_name=TABLE_NAME, vector_size=VECTOR_SIZE)

store = PGVectorStore.create_sync(
    engine=engine,
    table_name=TABLE_NAME,
    embedding_service=embeddings,
)
```

### Add and search documents

```python
import uuid
from langchain_core.documents import Document

docs = [
    Document(id=str(uuid.uuid4()), page_content="Apples and oranges", metadata={"topic": "food"}),
    Document(id=str(uuid.uuid4()), page_content="Cars and airplanes", metadata={"topic": "transport"}),
]

# Sync
store.add_documents(docs)
results = store.similarity_search("I'd like a fruit.", k=2)

# Async
await store.aadd_documents(docs)
results = await store.asimilarity_search("I'd like a fruit.", k=2)

# By vector
query_vector = embeddings.embed_query("I'd like a fruit.")
results = await store.asimilarity_search_by_vector(query_vector, k=2)
```

### Metadata filtering

```python
# Supported operators: $eq, $ne, $lt, $lte, $gt, $gte, $in, $nin, $and, $or
results = await store.asimilarity_search(
    "fruit",
    filter={"topic": {"$eq": "food"}},
)

results = await store.asimilarity_search(
    "vehicle",
    filter={"content": {"$gte": 1}},
)
```

---

## PostgresChatMessageHistory

Persist conversation history in PostgreSQL. Useful for multi-turn chatbots.

```python
import uuid
import psycopg
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Connection
CONN_INFO = "dbname=langchain user=langchain password=langchain host=localhost port=6024"
sync_connection = psycopg.connect(CONN_INFO)

# Create the schema (run once)
TABLE_NAME = "chat_history"
PostgresChatMessageHistory.create_tables(sync_connection, TABLE_NAME)

# Initialize per session
session_id = str(uuid.uuid4())
chat_history = PostgresChatMessageHistory(
    TABLE_NAME,
    session_id,
    sync_connection=sync_connection,
)

# Add messages
chat_history.add_message(SystemMessage("You are a helpful assistant."))
chat_history.add_message(HumanMessage("Hi there!"))
chat_history.add_message(AIMessage("Hello! How can I help you today?"))

# Retrieve messages
print(chat_history.messages)

# Clear session
chat_history.clear()

sync_connection.close()
```

---

## Connection string formats

| Driver        | Connection string prefix              | Use case          |
|---------------|---------------------------------------|-------------------|
| psycopg (v3)  | `postgresql+psycopg://...`            | Sync (PGVector)   |
| asyncpg       | `postgresql+asyncpg://...`            | Async (PGVectorStore) |
| psycopg async | `postgresql+psycopg://...`            | Both via psycopg  |
