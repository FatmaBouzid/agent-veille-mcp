"""
Récupération de documents pertinents depuis ChromaDB déjà indexé.

Séparé de ingest.py : ce module est appelé à CHAQUE question utilisateur,
alors que ingest.py n'est appelé qu'une fois (ou périodiquement) pour
peupler l'index.
"""

from langchain_chroma import Chroma

from agent_veille.config import settings
from agent_veille.rag.ingest import get_embeddings


def get_vectorstore() -> Chroma:
    """Charge l'index ChromaDB existant depuis le disque (ne réindexe rien)."""
    return Chroma(
        persist_directory=settings.chroma_persist_dir,
        embedding_function=get_embeddings(),
    )


def retrieve(query: str, k: int = 3) -> list[str]:
    """
    Retourne les k chunks les plus pertinents pour une question donnée.

    Retourne des str (pas des objets Document) car c'est ce format que
    le LLM consommera directement dans le prompt du tool.
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in results]