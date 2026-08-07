import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")


def ingest_pdf() -> None:
    """Ingest a PDF file into the pgVector vector store.

    Loads the PDF from PDF_PATH, splits it into chunks, generates embeddings
    using the configured provider (OpenAI or Gemini), and stores vectors in PostgreSQL.
    """
    # Validate required env vars
    if not PDF_PATH:
        raise ValueError("PDF_PATH não configurado. Verifique o arquivo .env.")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não configurado. Verifique o arquivo .env.")
    if not PG_VECTOR_COLLECTION_NAME:
        raise ValueError("PG_VECTOR_COLLECTION_NAME não configurado. Verifique o arquivo .env.")

    # 1. Load PDF
    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"PDF carregado: {len(documents)} página(s)")

    # 2. Split into chunks
    print("Dividindo em chunks (tamanho=1000, overlap=150)...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(documents)
    print(f"Total de chunks: {len(chunks)}")

    # 3. Select embedding provider
    if OPENAI_API_KEY:
        print(f"Provedor de embeddings: OpenAI ({OPENAI_EMBEDDING_MODEL})")
        embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            chunk_size=300,  # Avoid 300k token/request limit (langchain-openai bug #31227)
        )
    elif GOOGLE_API_KEY:
        print(f"Provedor de embeddings: Gemini ({GOOGLE_EMBEDDING_MODEL})")
        # Do NOT set task_type here — library auto-selects RETRIEVAL_DOCUMENT for embed_documents()
        embeddings = GoogleGenerativeAIEmbeddings(
            model=GOOGLE_EMBEDDING_MODEL,
        )
    else:
        raise ValueError("Nenhuma chave de API configurada. Configure OPENAI_API_KEY ou GOOGLE_API_KEY no arquivo .env.")

    # 4. Store vectors in pgVector
    print("Armazenando vetores no PostgreSQL...")
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
    print("Ingestão concluída com sucesso!")


if __name__ == "__main__":
    ingest_pdf()
