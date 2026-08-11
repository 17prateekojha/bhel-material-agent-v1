import config


def test_get_setting_prefers_streamlit_secrets(monkeypatch):
    class DummyStreamlit:
        def __init__(self):
            self.secrets = {"OPENAI_API_KEY": "secret-from-cloud"}

    monkeypatch.setattr(config, "st", DummyStreamlit(), raising=False)
    assert config.get_setting("OPENAI_API_KEY", "fallback") == "secret-from-cloud"


def test_get_setting_falls_back_to_environment(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    assert config.get_setting("OPENAI_MODEL", "fallback") == "gpt-4o-mini"
