"""
Configuration centralisée du projet.

Stack 100% gratuite :
- Groq pour le LLM (function calling fiable, sans carte bancaire)
- sentence-transformers + ChromaDB en local pour le RAG (aucune clé requise)
- Open-Meteo pour la météo (aucune clé requise)
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Groq — obligatoire, c'est le cœur du function calling de l'agent.
    # Field(...) = si absent du .env, l'app plante au démarrage avec un
    # message clair, plutôt qu'une erreur HTTP 401 confuse plus tard.
    groq_api_key: str = Field(..., description="Clé API Groq (console.groq.com/keys)")
    llm_model_name: str = Field(default="openai/gpt-oss-120b")

    # RAG — 100% local, aucune clé
    chroma_persist_dir: str = Field(default="src/agent_veille/rag/vectorstore")
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    # Météo — API publique sans clé
    open_meteo_base_url: str = Field(default="https://api.open-meteo.com/v1/forecast")


settings = Settings()