# LangChain

**Package**: `langchain`, `langchain-core`, `langchain-text-splitters`
**Docs**: https://python.langchain.com/docs/

Core framework for building LLM-powered applications with chains, prompts, retrievers, and output parsers.

---

## Prompt Templates

### PromptTemplate (string input)

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
    template="Answer the question based on context:\n{context}\n\nQuestion: {question}",
    input_variables=["context", "question"],
)

# Format into a string
formatted = prompt.format(context="Paris is the capital of France.", question="What is the capital of France?")
```

### ChatPromptTemplate (message input)

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use this context:\n{context}"),
    ("human", "{question}"),
])

# Format into messages list
messages = prompt.format_messages(context="...", question="What is RAG?")
```

---

## Output Parsers

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
# Use in a chain: prompt | llm | parser
```

---

## Document Loaders

### PyPDFLoader (requires `pypdf`)

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./path/to/document.pdf")
documents = loader.load()  # list[Document], one per page

# Lazy loading (memory-efficient)
for doc in loader.lazy_load():
    print(doc.page_content)
```

### Single-document mode

```python
loader = PyPDFLoader("document.pdf", mode="single")  # whole PDF as one Document
documents = loader.load()
```

---

## Text Splitters

### RecursiveCharacterTextSplitter

Splits text hierarchically by paragraphs → sentences → words. The recommended default for most use cases.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,     # max characters per chunk
    chunk_overlap=200,   # characters overlapping between consecutive chunks
    length_function=len,
)

# From a list of Document objects
chunks = text_splitter.split_documents(documents)

# From raw text
texts = text_splitter.split_text("Long text string here...")
```

---

## LCEL — LangChain Expression Language

LCEL composes runnables with the `|` pipe operator. Every component (prompt, model, parser, retriever) is a `Runnable`.

### Basic chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("What is the capital of {country}?")
parser = StrOutputParser()

chain = prompt | llm | parser
response = chain.invoke({"country": "France"})
```

### RAG chain

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_template(
    "Answer based on the context:\n{context}\n\nQuestion: {question}"
)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("What is LangChain?")
```

---

## Core Types

### Document

```python
from langchain_core.documents import Document

doc = Document(
    page_content="Text content of the document",
    metadata={"source": "file.pdf", "page": 0},
)
```

### Messages

```python
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Tell me about RAG."),
]
```

---

## Full RAG Pipeline Example

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres.vectorstores import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Load
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# 2. Split
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# 3. Embed + Store
embeddings = OpenAIEmbeddings()
vectorstore = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    connection="postgresql+psycopg://user:pass@localhost:5432/db",
    collection_name="docs",
)

# 4. Retrieve + Generate
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template(
    "Context:\n{context}\n\nQuestion: {question}"
)

chain = (
    {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
     "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(chain.invoke("What is the document about?"))
```
