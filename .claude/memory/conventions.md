# OM — Conventions

## Coding

- CLI: `python -m darshana` for interactive use
- Pipeline: `from darshana import Antahkarana; mind = Antahkarana(); mind.think("query")`
- Tests: `~/om/.venv/bin/python3 -m pytest tests/ -x`
- Sycophancy benchmark: `tests/benchmark_sycophancy.py`
- Multi-model scanner: `tests/scan_models.py`

## Project References

- `.claude/memory/structure.md` — full folder layout and naming conventions
- `.claude/memory/content.md` — writing style, reasoning rules, depth requirements
- `.claude/memory/roadmap.md` — complete build history + next steps

## Key Benchmark Results

- 19 models tested — every one sycophantic (56-100%)
- adhikara-bheda finding: strong models need instruction only (Claude: 26% → 4.5%)
- Total benchmark cost: ~$15 across ~6,000 API calls
