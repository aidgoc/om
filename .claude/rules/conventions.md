# OM — Non-Negotiables (Code & Repo)

## Environment
- **Always use the venv** `~/om/.venv/`. Never global pip (Homebrew Python 3.14 blocks it).
- Package name is `darshana`; install editable with `pip install -e .`.
- Tests must pass before done: `~/om/.venv/bin/python3 -m pytest tests/ -x` (48 passing).

## Packaging (Python 3.14 / PEP 639)
- No deprecated `License :: OSI Approved` classifiers — use `license = "MIT"` field only.

## Code
- Python 3.9+ with type hints; docstrings reference the philosophical concept.
- Every module works standalone AND inside the Antahkarana pipeline.
- Degrade gracefully — a missing module skips its step, never crashes.
- Pure Python + stdlib where possible (SQLite for persistence, urllib for web); external deps only when essential (anthropic SDK).

## Plugin hook discipline
- `plugin/hooks/vritti-check.py` is duplicated across 4 locations: `plugin/`, `marketplace/`, installed cache, registry. Change one → sync ALL four.

## Public repo hygiene
- github.com/aidgoc/om is **PUBLIC**. Never commit secrets, API keys, PII, or private business data.
- New `.claude/memory/` files are gitignored (local-only). Existing tracked memory is clean public content — leave it tracked; do not add anything sensitive to it.
