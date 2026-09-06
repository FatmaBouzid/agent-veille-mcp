"""
Schémas Pydantic v2 pour valider les inputs des tools AVANT exécution.

Pourquoi des schémas séparés plutôt que de valider dans le corps de chaque
tool : ça découple la validation (règle métier : "une query ne doit pas être
vide") de l'exécution (aller chercher dans ChromaDB / appeler Open-Meteo).
Un schéma peut aussi être réutilisé pour la doc du tool (LangChain peut
lire un schéma Pydantic comme args_schema).
"""

from pydantic import BaseModel, Field, field_validator


class SearchDocsInput(BaseModel):
    query: str = Field(..., min_length=3, description="La question à rechercher dans les docs")

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La requête ne peut pas être vide ou composée uniquement d'espaces")
        return v.strip()


class WeatherInput(BaseModel):
    city_name: str = Field(..., min_length=2, description="Nom de la ville")

    @field_validator("city_name")
    @classmethod
    def city_name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom de ville ne peut pas être vide")
        return v.strip()