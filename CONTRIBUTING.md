# Contributing to Broryat AI

Thanks for your interest in improving Broryat AI. This is a small, focused project — the notes below should be enough to get a change from idea to merged PR.

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting set up

```bash
git clone https://github.com/COPPSARY/broryat-bot
cd broryat-ai
cp .env.example .env   # fill in tokens/keys, see README for details
uv sync
```

You don't need real API keys to develop or run the test suite — VirusTotal and every AI provider are mocked at their client boundary, and the database layer runs against an in-memory SQLite engine. Real credentials are only needed to run the bot itself (`uv run main.py`) against live Telegram/VirusTotal/AI services.

## Running tests

```bash
uv run -m pytest
```

Run a single file or test while iterating:

```bash
uv run -m pytest tests/services/test_pipeline.py
uv run -m pytest tests/services/test_pipeline.py::test_vt_malicious_forces_high_even_when_ai_says_safe
```

Please add or update tests alongside any behavior change — see the existing suite under `tests/` for the patterns used (mocked SDK clients for AI providers, `respx` for HTTP, in-memory SQLite for the database layer).

## Before opening a PR

- Run the full test suite and make sure it's green.
- Keep the change scoped to what the PR describes — avoid unrelated refactors or formatting churn in the same diff.
- If you're adding a new AI provider, follow the existing pattern in `bot/services/ai/providers/` (and `bot/services/ai/image_extractors/` if it supports vision) rather than branching on provider name in caller code.
- Update `CLAUDE.md` / `README.md` if the change affects module layout, setup steps, or configuration.

## Reporting bugs / requesting features

Open a GitHub issue with:
- What you expected vs. what happened (for bugs), including logs if relevant (redact any tokens/keys).
- The scope of the feature and why it's needed (for feature requests).

## Code style

- Python 3.13, managed with [uv](https://docs.astral.sh/uv/).
- No enforced linter/formatter is configured yet — match the existing style in the file you're editing.
- Prefer small, composable functions and dependency injection (see how `bot/services/virustotal/rate_limiter.py` injects `time_func`/`sleep_func` for deterministic tests) over adding global state or hidden singletons.

## License

By contributing, you agree that your contributions will be licensed under the project's [Apache License 2.0](LICENSE).
