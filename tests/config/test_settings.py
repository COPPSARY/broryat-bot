from bot.config.settings import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("BRORYAT_API_KEY", "test-broryat-key")
    monkeypatch.setenv("VT_API_KEY", "test-vt-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/postgres")

    settings = Settings(_env_file=None)

    assert settings.telegram_bot_token == "test-token"
    assert settings.gemini_api_key == "test-gemini-key"
    assert settings.broryat_api_key == "test-broryat-key"
    assert settings.vt_api_key == "test-vt-key"
    assert settings.database_url == "postgresql://user:pass@localhost:5432/postgres"


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("VT_API_KEY", "test-vt-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/postgres")

    settings = Settings(_env_file=None)

    assert settings.ai_provider == "gemini"
    assert settings.llm_model == "google/gemma-4-31B-it"
    assert settings.max_file_size_bytes == 20 * 1024 * 1024
    assert settings.vt_rpm_limit == 4
    assert settings.vt_daily_limit == 500
    assert settings.vt_monthly_limit == 15500
    assert settings.group_scan_enabled is True
    assert settings.log_level == "INFO"


def test_numbered_api_keys_are_sorted_and_deduplicated(monkeypatch):
    monkeypatch.setenv("HUGGINGFACE_API_KEY10", "hf-ten")
    monkeypatch.setenv("HUGGINGFACE_API_KEY2", "hf-two")
    monkeypatch.setenv("HUGGINGFACE_API_KEY1", "hf-primary")
    monkeypatch.setenv("VT_API_KEY3", "vt-three")
    monkeypatch.setenv("VT_API_KEY1", "vt-primary")

    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
        database_url="sqlite://",
        huggingface_api_key="hf-primary",
        vt_api_key="vt-primary",
    )

    assert settings.huggingface_api_keys == ["hf-primary", "hf-two", "hf-ten"]
    assert settings.vt_api_keys == ["vt-primary", "vt-three"]


def test_numbered_keys_load_from_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            (
                "TELEGRAM_BOT_TOKEN=test-token",
                "DATABASE_URL=sqlite://",
                "HUGGINGFACE_API_KEY1=hf-one",
                "HUGGINGFACE_API_KEY2=hf-two",
                "VT_API_KEY1=vt-one",
                "VT_API_KEY2=vt-two",
            )
        )
    )

    settings = Settings(_env_file=env_file)

    assert settings.huggingface_api_keys == ["hf-one", "hf-two"]
    assert settings.vt_api_keys == ["vt-one", "vt-two"]
