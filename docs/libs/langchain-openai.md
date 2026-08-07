# langchain-openai

**Package**: `langchain-openai`
**Docs**: https://python.langchain.com/docs/integrations/providers/openai/
**Version used**: `>=1.4.1`

Provides LangChain integrations for OpenAI models:
- `ChatOpenAI` — chat completion models (GPT-4o, GPT-4o-mini, etc.)
- `OpenAIEmbeddings` — text embedding models (text-embedding-3-small, text-embedding-3-large)

Requires `OPENAI_API_KEY` environment variable.

---

## Installation & setup

```bash
uv add langchain-openai
```

```env
# .env
OPENAI_API_KEY=sk-...
```

---

## ChatOpenAI

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",   # or "gpt-4o", "gpt-4-turbo", etc.
    temperature=0,         # 0 = deterministic, 1 = creative
    max_tokens=None,       # None = model default
)
```

### Invoke with messages

```python
from langchain_core.messages import HumanMessage, SystemMessage

response = llm.invoke([
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is RAG?"),
])

print(response.content)  # str
```

### In a chain (LCEL)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Answer this question: {question}")
chain = prompt | llm | StrOutputParser()

answer = chain.invoke({"question": "What is vector search?"})
```

### Streaming

```python
for chunk in llm.stream([HumanMessage(content="Tell me a joke")]):
    print(chunk.content, end="", flush=True)
```

### Async

```python
response = await llm.ainvoke([HumanMessage(content="Hello!")])
```

---

## OpenAIEmbeddings

Converts text into dense vector representations for similarity search.

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",   # or "text-embedding-3-large" (higher quality)
    # dimensions=512,                 # optional: reduce output dimensions
)
```

### Embed a query (single string)

```python
vector = embeddings.embed_query("What is retrieval augmented generation?")
# Returns list[float] of length 1536 (text-embedding-3-small default)
```

### Embed documents (batch)

```python
texts = ["Document one", "Document two", "Document three"]
vectors = embeddings.embed_documents(texts)
# Returns list[list[float]]
```

### With PGVector

```python
from langchain_postgres.vectorstores import PGVector

vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="my_collection",
    connection="postgresql+psycopg://langchain:langchain@localhost:6024/langchain",
    use_jsonb=True,
)
```

---

## Available models

| Model                        | Dimensions | Notes                            |
|------------------------------|-----------|----------------------------------|
| `gpt-4o`                     | —         | Best quality, higher cost        |
| `gpt-4o-mini`                | —         | Fast, low cost, good quality     |
| `text-embedding-3-small`     | 1536      | Fast, low cost embeddings        |
| `text-embedding-3-large`     | 3072      | Higher quality embeddings        |
| `text-embedding-ada-002`     | 1536      | Legacy, superseded by v3         |

---

## Environment variable reference

| Variable              | Description                        |
|-----------------------|------------------------------------|
| `OPENAI_API_KEY`      | Required. Your OpenAI API key.     |
| `OPENAI_BASE_URL`     | Optional. Custom API endpoint.     |
| `OPENAI_ORG_ID`       | Optional. Organization ID.         |
