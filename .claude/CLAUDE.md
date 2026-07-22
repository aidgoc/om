# OM — Darshana Reasoning Framework

Python package + Claude Code plugin + MCP server that turns the six Hindu Darshanas into a cognitive architecture for LLM reasoning. Public repo (github.com/aidgoc/om, MIT).

## Stack & Setup

- **Python** 3.14 (Homebrew) — **must** use venv `~/om/.venv/`, global pip is blocked
- **Install**: `pip install -e .` (package name: `darshana`)
- **Tests**: `~/om/.venv/bin/python3 -m pytest tests/ -x` (48 passing)
- **CLI**: `python -m darshana` (interactive REPL or single-query)
- **Claude plugin**: `darshana@darshana-marketplace` (v0.2.2)
- **MCP server**: `mcp/server.py` (9 tools, 2 resource types)

## SDK Usage

```python
from darshana import guard, last_meta
client = guard(anthropic.Anthropic())
response = client.messages.create(model="claude-sonnet-4-6", ...)
meta = last_meta(response)  # .vritti, .confidence, .novelty, .intervention
```

Pipeline form: `from darshana import Antahkarana; mind = Antahkarana(); mind.think("query")`

## Layout

- **`src/`** — 16 modules, ~14k lines. Antahkarana pipeline + guard SDK. Core: `antahkarana.py` (9-step master pipeline), `darshana_router.py` (Buddhi routing + 6 engines), `vritti_filter.py` (output classifier), `yaksha.py` (multi-darshana debate), `smriti.py` (SQLite memory), `pratyaksha.py` (perception), `manas.py` (attention), `shakti.py` (compute), `ahamkara.py` (self-model)
- **`plugin/`** — Claude Code plugin: 10 skills (`/darshana`, `/nyaya`, …), 1 agent, 1 command-type Stop hook (`hooks/vritti-check.py`)
- **`mcp/`** — MCP server for any AI client
- **`marketplace/`** — local Claude Code marketplace (plugin distribution copy)
- **`tests/`** — unit tests + benchmarks (router 95%, filter 100%, sycophancy scanner)
- **`paper/`** — "Adhikara-Bheda" paper (markdown + LaTeX), arXiv pending
- Curriculum dirs (`sanskrit/`, `texts/`, `philosophy/`, `practices/`, `connections/`) — 29 lessons, 5 phases

## The Shaddarshana as Reasoning Modes

| Mode | School | When to use | Action |
|---|---|---|---|
| **Nyaya** | Logic | Need proof/validation | Identify pramanas, check for hetvabhasa |
| **Samkhya** | Enumeration | Classify/decompose | Count components, find tattvas |
| **Yoga** | Focus | Noise high, signal low | Reduce vrittis, find the one thing |
| **Vedanta** | Unity | Contradictions obscure truth | Neti neti until what remains |
| **Mimamsa** | Interpretation | Requirements → action | Find the vidhi, execute it |
| **Vaisheshika** | Atomism | Need irreducible parts | Break into paramanus (dravya/guna/karma) |

Default reasoning sequence: Vaisheshika → Samkhya → Nyaya → Yoga → Mimamsa → Vedanta. **Pick 2-3 max — depth over breadth.** Each darshana must EXECUTE its method, not just NAME it.

## Key Benchmark Results

- 19 models tested, every one sycophantic (56–100%)
- Adhikara-bheda finding: strong models need instruction only (Claude 26% → 4.5%); weaker models need structure too
- Sycophancy reduction and reasoning quality are orthogonal
- Total benchmark cost: ~$15 across ~6,000 API calls

## Gotchas

- **Venv mandatory** — Homebrew Python 3.14 blocks global pip install.
- **PEP 639 (Py 3.14)**: no deprecated `License :: OSI Approved` classifiers. Use `license = "MIT"` field only.
- Plugin hook synced across 4 locations (`plugin/`, `marketplace/`, installed cache, registry) — update all on hook change.
- Modules degrade gracefully — missing module skips its pipeline step, never crashes.
- `~/om` is a **symlink** to `/Volumes/Work Main/Projects/om` (physical path).

## Deep context

- Full writing/reasoning/honesty rules: `@.claude/memory/content.md`
- Folder layout + naming: `@.claude/memory/structure.md`
- Build history + next steps: `@.claude/memory/roadmap.md`
- Voice, core thesis, 7 operating principles: `.claude/skills/om/SKILL.md`

## Gaps

- arXiv submission and PyPI publish pending (need accounts/tokens).
- No project-specific agents worth committing (plugin agent lives in `plugin/agents/`).
- No deploy tooling — this is a library/plugin, not a hosted service.
