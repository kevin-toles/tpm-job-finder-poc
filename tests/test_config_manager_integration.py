from src.config.config_manager import ConfigManager

def test_integration_env_loading(tmp_path, monkeypatch):
    # Simulate .env loading
    env_file = tmp_path / ".env"
    env_file.write_text("INTEGRATION_KEY=integration_value\nINTEGRATION_FEATURE=true\n")
    monkeypatch.setenv("INTEGRATION_KEY", "integration_value")
    monkeypatch.setenv("INTEGRATION_FEATURE", "true")
    assert ConfigManager.get("INTEGRATION_KEY") == "integration_value"
    assert ConfigManager.is_feature_enabled("INTEGRATION_FEATURE") is True
