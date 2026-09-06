"""
Wrapper du RAG en tant que "tool" utilisable par l'agent LangGraph.

Pourquoi un wrapper séparé plutôt qu'appeler retrieve() directement dans
le graphe : LangGraph/LangChain attendent une interface "tool" standardisée
(nom, description, schéma d'input) pour que le LLM puisse décider QUAND
l'appeler. La description ci-dessous EST ce que le LLM lit pour juger si
ce tool est pertinent pour la question posée — elle doit être précise.
"""

from langchain_core.tools import tool

from agent_veille.rag.retriever import retrieve


@tool
def search_internal_docs(query: str) -> str:
    """
    Recherche des informations dans la base de connaissances interne
    (documents techniques indexés : LangGraph, MCP, RAG, etc.).
    Utilise ce tool pour toute question portant sur des concepts techniques
    ou des documents que l'utilisateur a fournis, PAS pour des questions
    sur l'actualité, la météo, ou des faits en temps réel.
    """
    chunks = retrieve(query, k=3)
    if not chunks:
        return "Aucun document pertinent trouvé dans la base de connaissances."
    return "\n\n---\n\n".join(chunks)