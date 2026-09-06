"""
Ingestion des documents dans ChromaDB.

Pourquoi un module séparé de retriever.py :
- l'ingestion (indexer des docs) et la récupération (chercher dans l'index)
  sont deux opérations distinctes dans le temps — on ingère une fois (ou
  périodiquement), on récupère à chaque question de l'utilisateur.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agent_veille.config import settings


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Instancie le modèle d'embeddings local.

    Pourquoi une fonction et pas juste une variable globale : évite de charger
    le modèle (quelques centaines de Mo) dès l'import du module, seulement
    quand on en a réellement besoin.
    """
    return HuggingFaceEmbeddings(model_name=settings.embedding_model_name)


def load_documents(source_dir: str = "data/sample_docs") -> list[Document]:
    """Charge tous les fichiers .txt d'un dossier comme documents LangChain."""
    documents = []
    for path in Path(source_dir).glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        documents.append(Document(page_content=text, metadata={"source": path.name}))
    return documents


def ingest_documents(source_dir: str = "data/sample_docs") -> Chroma:
    """
    Charge, découpe (chunk) et indexe les documents dans ChromaDB.

    Pourquoi découper en chunks : un document entier est souvent trop long
    pour être un résultat de recherche pertinent — on découpe en petits
    morceaux avec chevauchement pour ne pas couper une idée au milieu.
    """
    documents = load_documents(source_dir)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )
    return vectorstore


if __name__ == "__main__":
    # Permet de lancer l'ingestion manuellement : python -m agent_veille.rag.ingest
    store = ingest_documents()
    print(f"Ingestion terminée : {store._collection.count()} chunks indexés.")