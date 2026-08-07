# langchain-google-genai

**Package**: `langchain-google-genai`
**Repo**: https://github.com/langchain-ai/langchain-google
**Version used**: `>=4.3.1`

Provides LangChain integrations for Google's Generative AI (Gemini) models:
- `ChatGoogleGenerativeAI` — Gemini chat models
- `GoogleGenerativeAIEmbeddings` — Gemini embedding models

Requires `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) environment variable.

---

## Installation & setup

```bash
uv add langchain-google-genai
```

```env
# .env
GOOGLE_API_KEY=AIza...
```

---

## ChatGoogleGenerativeAI

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # or "gemini-1.5-pro", "gemini-2.5-pro"
    temperature=0,
    # google_api_key="AIza...",   # optional: override env var
)
```

### Invoke with messages

```python
from langchain_core.messages import HumanMessage, SystemMessage

response = llm.invoke(
    [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is RAG?"),
    ]
)

print(response.content)  # str
```

### In a chain (LCEL)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Answer based on the context:\n{context}\n\nQuestion: {question}")
chain = prompt | llm | StrOutputParser()

answer = chain.invoke({"context": "...", "question": "What is this about?"})
```

### Streaming

```python
for chunk in llm.stream([HumanMessage(content="Tell me about embeddings")]):
    print(chunk.content, end="", flush=True)
```

### Async

```python
response = await llm.ainvoke([HumanMessage(content="Hello!")])
```

### With Vertex AI backend

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    project="your-gcp-project-id",
    vertexai=True,
)
```

---

## GoogleGenerativeAIEmbeddings

Converts text into dense vector representations using Google's embedding models.

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",  # current stable model
    # task_type="retrieval_document",      # optional: tune for document embedding
    # output_dimensionality=768,           # optional: reduce output size
)
```

### task_type values

| Value                   | Use case                                    |
|-------------------------|---------------------------------------------|
| `retrieval_document`    | Embedding documents to be stored/retrieved  |
| `retrieval_query`       | Embedding a user query at search time       |
| `semantic_similarity`   | Comparing sentence similarity               |
| `classification`        | Text classification tasks                   |
| `clustering`            | Text clustering tasks                       |

### Embed a query

```python
vector = embeddings.embed_query("What is retrieval augmented generation?")
# Returns list[float]
```

### Embed documents (batch)

```python
texts = ["Document one", "Document two"]
vectors = embeddings.embed_documents(texts)
# Returns list[list[float]]
```

### Per-call dimensionality override

```python
# embed_documents and embed_query both accept output_dimensionality
vectors = embeddings.embed_documents(
    texts,
    output_dimensionality=512,  # override instance default for this call
)
```

### Async variants

```python
vector = await embeddings.aembed_query("query text")
vectors = await embeddings.aembed_documents(["doc1", "doc2"])
```

### With PGVector

```python
from langchain_postgres.vectorstores import PGVector

vectorstore = PGVector(
    embeddings=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"),
    collection_name="my_collection",
    connection="postgresql+psycopg://langchain:langchain@localhost:6024/langchain",
    use_jsonb=True,
)
```

---

## Available models

| Model                          | Type       | Dimensions | Notes                          |
|--------------------------------|-----------|-----------|--------------------------------|
| `gemini-2.5-pro`               | Chat       | —         | Best quality                   |
| `gemini-2.0-flash`             | Chat       | —         | Fast, low latency              |
| `gemini-1.5-pro`               | Chat       | —         | Long context (1M tokens)       |
| `models/gemini-embedding-001`  | Embedding  | 768       | Current stable embedding model |

---

## Environment variable reference

| Variable          | Description                          |
|-------------------|--------------------------------------|
| `GOOGLE_API_KEY`  | Required. Your Google AI Studio key. |
| `GEMINI_API_KEY`  | Alternative to `GOOGLE_API_KEY`.     |
| `GOOGLE_CLOUD_LOCATION` | Optional. GCP region for Vertex AI. |
