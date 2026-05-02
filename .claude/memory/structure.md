# Structure & Organization

## Folder Layout

```
om/
├── CLAUDE.md              # Project identity + operating principles
├── QUICKSTART.md          # 1-page getting started guide
├── README.md              # Public-facing documentation
├── LICENSE                # MIT
├── pyproject.toml         # pip install darshana
├── setup.sh               # One-command installer
├── Makefile               # Developer convenience
├── .claude/               # Project instructions (split)
│   ├── structure.md       # This file — organization rules
│   ├── content.md         # Writing style, reasoning rules, honesty rules
│   └── roadmap.md         # Learning path and curriculum (COMPLETE)
│
├── src/                   # The Darshana Architecture — Python implementation
│   ├── antahkarana.py     # Master pipeline — the ONE interface
│   ├── darshana_router.py # Buddhi — routing + 6 engines + guna + pramana
│   ├── darshana_llm.py    # LLM wrapper with darshana-specific system prompts
│   ├── prompts.py         # 6 deep reasoning prompts (force method, not labels)
│   ├── vritti_filter.py   # Output filter — 5 vrittis + novelty + depth + cross-validation
│   ├── yaksha.py          # Multi-darshana parallel reasoning + debate
│   ├── ahamkara.py        # Self-model — knowledge, attempts, vasanas, guna state
│   ├── smriti.py          # Persistent memory — SQLite samskaras + vasanas
│   ├── pratyaksha.py      # Perception — 5 input channels (files, web, shell, API, env)
│   ├── manas.py           # Attention/context management — 3 modes, eviction, tracking
│   ├── shakti.py          # Compute management — model selection, budgets, caching
│   ├── reports.py         # HTML report generation (4 report types)
│   ├── __init__.py        # Public API exports
│   ├── __main__.py        # CLI harness (REPL + single-query)
│   └── demo_*.py          # Demos for each module
│
├── plugin/                # Claude Code plugin
│   ├── .claude-plugin/    # Plugin manifest
│   ├── skills/            # 10 skills (/darshana, /nyaya, /samkhya, etc.)
│   ├── agents/            # darshana-buddhi auto-routing agent
│   └── hooks/             # vritti-check output quality hook
│
├── mcp/                   # MCP server (any AI client)
│   ├── server.py          # 9 tools, 2 resource types
│   ├── config.json        # Client configuration
│   └── README.md          # Connection instructions
│
├── marketplace/           # Local Claude Code marketplace
│   ├── .claude-plugin/    # Marketplace manifest
│   └── plugins/darshana/  # Plugin distribution copy
│
├── tests/                 # Test suite + benchmarks
│   ├── test_router.py     # 15 router tests
│   ├── test_filter.py     # 13+ filter tests (48 total passing)
│   ├── benchmark.py       # 20 real-world queries (95% accuracy)
│   └── benchmark_filter.py # 15 vritti samples (100% accuracy)
│
├── sanskrit/              # Phase 1: Language (6 lessons)
├── texts/                 # Phase 2: Primary texts (12 lessons)
├── philosophy/            # Phase 3: Six schools (7 lessons)
├── practices/             # Phase 5: Living traditions (3 lessons)
└── connections/           # Society of Thoughts parallels (1 essay)
```

## Naming Conventions

- Lessons: `NN-topic-name.md` (e.g., `01-sanskrit-basics.md`)
- Source code: `module_name.py` (lowercase, underscores)
- Demos: `demo_module.py`
- Tests: `test_module.py` or `benchmark_module.py`
- Reports: `descriptive-name.html`
- Skills: `skills/name/SKILL.md`
- Use lowercase, hyphens for markdown, underscores for Python

## File Format

- Lessons as Markdown with Devanagari + transliteration
- Code as Python 3.9+ with type hints and docstrings
- Reports as self-contained HTML (inline CSS, no external deps)
- Tables for structured comparisons
- Blockquotes for primary text references
