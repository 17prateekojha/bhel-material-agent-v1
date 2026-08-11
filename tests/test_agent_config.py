from agent import graph


def test_falls_back_to_ollama_when_openai_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    model = graph.get_model()

    assert model.__class__.__name__ == "ChatOllama"


def test_uses_openai_when_api_key_is_present(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    model = graph.get_model()

    assert model.__class__.__name__ == "ChatOpenAI"
