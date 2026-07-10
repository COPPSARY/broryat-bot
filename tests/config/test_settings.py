from bot.config.settings import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("VT_API_KEY", "test-vt-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/postgres")

    settings = Settings(_env_file=None)

    assert settings.telegram_bot_token == "test-token"
    assert settings.gemini_api_key == "test-gemini-key"
    assert settings.vt_api_key == "test-vt-key"
    assert settings.database_url == "postgresql://user:pass@localhost:5432/postgres"


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("VT_API_KEY", "test-vt-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/postgres")

    settings = Settings(_env_file=None)

    assert settings.ai_provider == "gemini"
    assert settings.llm_model == "gemini-2.0-flash"
    assert settings.huggingface_base_url == "https://router.huggingface.co/v1"
    assert settings.vt_rpm_limit == 4
    assert settings.vt_daily_limit == 500
    assert settings.vt_monthly_limit == 15500
    assert settings.group_scan_enabled is True
    assert settings.log_level == "INFO"
