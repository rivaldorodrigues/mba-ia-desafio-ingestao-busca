import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.0-flash")


def format_docs(docs):
    """Format a list of documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def search_prompt(question=None):
    """Build and return the LCEL RAG chain.

    Returns the chain on success, None on configuration error.
    The returned chain accepts a question string via chain.invoke(question).
    """
    try:
        # 1. Select provider (embeddings + LLM must match the ingest.py provider)
        if OPENAI_API_KEY:
            embeddings = OpenAIEmbeddings(
                model=OPENAI_EMBEDDING_MODEL,
                chunk_size=300,
            )
            llm = ChatOpenAI(model=OPENAI_LLM_MODEL, temperature=0)
        elif GOOGLE_API_KEY:
            embeddings = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)
            llm = ChatGoogleGenerativeAI(model=GOOGLE_LLM_MODEL, temperature=0)
        else:
            print("Erro: nenhuma chave de API configurada. Configure OPENAI_API_KEY ou GOOGLE_API_KEY.")
            return None

        # 2. Connect to existing pgVector collection (query-time — NOT from_documents)
        vectorstore = PGVector(
            embeddings=embeddings,
            collection_name=PG_VECTOR_COLLECTION_NAME,
            connection=DATABASE_URL,
            use_jsonb=True,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

        # 3. Build LCEL chain: question string → retriever → format → prompt → LLM → string
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        chain = {"contexto": retriever | format_docs, "pergunta": RunnablePassthrough()} | prompt | llm | StrOutputParser()
        return chain

    except Exception as e:
        print(f"Erro ao inicializar o chat: {e}")
        return None
