"""
On teste ingestion + récupération de bout en bout sur un dossier de test
isolé (pas data/sample_docs, pour ne pas dépendre de son contenu réel et
pour ne pas polluer le vrai index ChromaDB à chaque run de test).
"""

import shutil

import pytest

from agent_veille.rag.ingest import ingest_documents
from agent_veille.tools.rag_tool import search_internal_docs


@pytest.fixture
def test_docs_dir(tmp_path, monkeypatch):
    """Crée un dossier de docs temporaire + redirige ChromaDB vers un dossier temporaire."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "test.txt").write_text(
        "LangGraph permet de construire des agents avec état et boucles.",
        encoding="utf-8",
    )

    persist_dir = tmp_path / "chroma"
    monkeypatch.setattr("agent_veille.config.settings.chroma_persist_dir", str(persist_dir))

    yield docs_dir

    shutil.rmtree(persist_dir, ignore_errors=True)


def test_ingest_and_retrieve(test_docs_dir):
    ingest_documents(source_dir=str(test_docs_dir))
    result = search_internal_docs.invoke({"query": "Qu'est-ce que LangGraph ?"})
    assert "LangGraph" in result


def test_search_internal_docs_no_results(test_docs_dir, monkeypatch):
    monkeypatch.setattr(
        "agent_veille.tools.rag_tool.retrieve",
        lambda query, k=3: [],
    )
    result = search_internal_docs.invoke({"query": "question sans rapport"})
    assert "Aucun document pertinent" in result

def test_search_internal_docs_rejects_empty_query():
    result = search_internal_docs.invoke({"query": "ab"})
    assert "Entrée invalide" in result