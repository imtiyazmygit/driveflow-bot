from pathlib import Path

from src.auth import load_config


def test_load_config_from_environment(monkeypatch):
    monkeypatch.setenv("DVSA_USERNAME", "user")
    monkeypatch.setenv("DVSA_PASSWORD", "pass")
    config = load_config()
    assert config["credentials"]["user_id"] == "user"
    assert config["credentials"]["password"] == "pass"


def test_load_config_falls_back_to_empty_when_missing():
    config = load_config()
    assert config == {}
