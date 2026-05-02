# OM — Darshana Reasoning Framework

Python 3.14, venv: `~/om/.venv/`. Install: `pip install -e .`

## Architecture

- **`src/`** — 16 Python modules, Antahkarana pipeline + guard SDK
- **`plugin/`** — Claude Code plugin (10 skills, darshana@darshana-marketplace)
- **`mcp/`** — MCP server (9 tools)
- **`tests/`** — 48 tests passing (`~/om/.venv/bin/python3 -m pytest tests/ -x`)
- **`paper/`** — "Adhikara-Bheda" paper (markdown + LaTeX), arXiv pending

## SDK Usage

```python
from darshana import guard, last_meta
client = guard(anthropic.Anthropic())
response = client.messages.create(model="claude-sonnet-4-6", ...)
meta = last_meta(response)  # .vritti, .confidence, .novelty, .intervention
```

@.claude/memory/conventions.md
