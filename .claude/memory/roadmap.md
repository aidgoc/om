# Roadmap

## COMPLETED — Curriculum (29 lessons, 5 phases)

### Phase 1: Sanskrit Foundation ✅
### Phase 2: Core Texts ✅ (Vedas, 5 Upanishads, Gita, Yoga Sutras)
### Phase 3: Philosophical Schools ✅ (all 6 Darshanas)
### Phase 4: Epics & Mythology ✅ (Ramayana, Mahabharata, Puranas)
### Phase 5: Living Traditions ✅ (Bhakti, Tantra, Modern thought)
### Society of Thoughts Thread ✅ (12 parallels mapped)

---

## COMPLETED — Architecture Implementation ✅

### Core Engines ✅
- [x] Darshana Router (Buddhi) — 95% routing accuracy
- [x] 6 darshana-specific system prompts — forces method, not labels
- [x] Vritti Filter — 100% classification accuracy, novelty scoring, depth testing, cross-validation
- [x] DarshanaLLM — full LLM pipeline wrapper
- [x] Yaksha Protocol — multi-darshana parallel reasoning + debate
- [x] Ahamkara — self-model (knowledge map, attempt log, vasana tracker)

### Infrastructure Layer ✅
- [x] Smriti — SQLite persistent memory with pramana-aware decay
- [x] Pratyaksha — 5-channel perception (files, web, shell, API, environment)
- [x] Manas — attention/context management with 3 modes
- [x] Shakti — compute management with guna-aware model selection
- [x] Antahkarana — master 9-step pipeline

### Harness ✅
- [x] CLI harness — interactive REPL + single-query mode
- [x] pip package (pyproject.toml v0.3.0)
- [x] Claude Code plugin — 10 skills, 1 agent, 1 hook
- [x] MCP server — 9 tools, 2 resource types

### Quality ✅
- [x] 48 unit tests passing
- [x] 20-query router benchmark (95%)
- [x] 15-sample filter benchmark (100%)

---

## COMPLETED — Benchmark + Proof (April 2026) ✅

### Sycophancy Benchmark ✅
- [x] benchmark_sycophancy.py — A/B runner with Haiku judge, retry, resumable
- [x] score_sycophancy.py — blind human evaluation scorer
- [x] scan_models.py — multi-model scanner via Bedrock Converse API
- [x] External prompts: Anthropic evals (30K) + TruthfulQA (790)

### Experiments ✅ (~$15 total)
- [x] 19-model sycophancy leaderboard (56–100%, every model sycophantic)
- [x] Full 2×2 factorial on Claude Sonnet 4.6 + Llama 4 Maverick
- [x] Ablation: instruction alone (4.5%) beats structure (10.1%) on Claude
- [x] Ablation: Llama needs both (15.6% combined)
- [x] Finding: sycophancy reduction and reasoning quality are orthogonal

### Paper ✅
- [x] "Adhikara-Bheda" — 3,500 words, markdown + LaTeX
- [x] Pushed to GitHub, LaTeX zip sent to Telegram
- [ ] arXiv submission (needs account)

### SDK ✅
- [x] guard() — one-line wrapper for Anthropic/AnthropicBedrock clients
- [x] last_meta() — safe metadata registry (no Pydantic mutation)
- [x] Code reviewed, all critical issues fixed
- [x] Built: dist/darshana-0.3.0-py3-none-any.whl
- [ ] PyPI publish (needs API token)

### Framework Improvements ✅
- [x] Anti-sycophancy directive in darshana prompts (toggleable)
- [x] Bedrock support in DarshanaLLM
- [x] Router fallback: Mimamsa for unmatched queries (was Nyaya)
- [x] Stop hook rewrite — works live, 80% threshold
- [x] Version bumped to 0.3.0

---

## NEXT — Ship & Deploy

### Immediate (this week)
- [ ] Publish to PyPI (`pip install darshana`)
- [ ] Submit paper to arXiv (cs.CL)
- [ ] Score 30 blind pairs for human evaluation
- [ ] Static sycophancy leaderboard website

### Real-World Integration
- [ ] Integrate guard() into Vaishali ERP AI sidecar (anti-sycophancy on sales decisions)
- [ ] Integrate guard() into DRM Sobha (safety advisory quality)
- [ ] Add OpenAI client support to guard()
- [ ] Add boto3 Converse API support to guard()

### Scale
- [ ] Om Eval — web app for model diagnostic ($5/run, pay-per-diagnostic)
- [ ] Leaderboard auto-refresh on new model releases
- [ ] Fine-tune Llama with Vritti-labeled DPO (step 4 of original roadmap)
- [ ] Generalize beyond sycophancy: hallucination, shallow reasoning, bias benchmarks

### Depth Improvements
- [ ] LLM-based Buddhi classifier (replace keyword matching, 95% → 99%)
- [ ] Embedding-based memory retrieval in Smriti
- [ ] Multi-round Yaksha debate with real LLM calls
- [ ] Sycophancy-specific vritti category in the filter

---

## Key Numbers (updated April 2026)
- Architecture: 16 Python modules, ~14,000 lines
- Tests: 48 passing, 95% router accuracy, 100% filter accuracy
- Benchmark: 19 models scanned, 8 experiment runs, ~6,000 API calls, ~$15
- Plugin: 10 skills, 1 agent, 1 hook (installed in Claude Code)
- MCP: 9 tools, 2 resource types
- SDK: v0.3.0, guard() + last_meta(), built for PyPI
- Paper: 3,500 words, on GitHub, arXiv pending
