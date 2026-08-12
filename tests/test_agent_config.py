from agent import graph


def test_falls_back_to_ollama_when_groq_key_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    model = graph.get_model()

    assert model.__class__.__name__ == "ChatOllama"


def test_uses_groq_when_api_key_is_present(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    model = graph.get_model()

    assert model.__class__.__name__ == "ChatGroq"
