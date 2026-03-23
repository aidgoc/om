# Roadmap

## COMPLETED — Curriculum (29 lessons, 5 phases)

### Phase 1: Sanskrit Foundation ✅
### Phase 2: Core Texts ✅ (Vedas, 5 Upanishads, Gita, Yoga Sutras)
### Phase 3: Philosophical Schools ✅ (all 6 Darshanas)
### Phase 4: Epics & Mythology ✅ (Ramayana, Mahabharata, Puranas)
### Phase 5: Living Traditions ✅ (Bhakti, Tantra, Modern thought)
### Society of Thoughts Thread ✅ (12 parallels mapped)

---

## COMPLETED — Architecture Implementation

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
- [x] Antahkarana — master 9-step pipeline (perceive → remember → assemble → route → budget → reason → filter → learn → respond)

### Harness ✅
- [x] CLI harness — interactive REPL + single-query mode
- [x] HTML report generator — 4 report types
- [x] pip package (pyproject.toml v0.2.0)
- [x] setup.sh + Makefile
- [x] README + QUICKSTART docs

### Integration ✅
- [x] Claude Code plugin — 10 skills, 1 agent, 1 hook
- [x] MCP server — 9 tools, 2 resource types
- [x] Local marketplace registered and plugin installed

### Quality ✅
- [x] 48 tests passing
- [x] 20-query router benchmark (95%)
- [x] 15-sample filter benchmark (100%)
- [x] Blog post draft (BLOG.md)
- [x] Layman outcomes report (reports/what-this-means.html)

---

## NEXT — What to Build

### Depth Improvements
- [ ] LLM-based Buddhi classifier (replace keyword matching for 95% → 99%)
- [ ] Embedding-based memory retrieval (replace keyword matching in Smriti)
- [ ] Run full Yaksha Protocol on 10 real hard problems, evaluate quality honestly
- [ ] Test with actual Anthropic API calls end-to-end

### Mik Integration
- [ ] Replace Mik's agent routing with Buddhi
- [ ] Add Smriti as Mik's persistent memory
- [ ] Add Vritti Filter to Mik's output pipeline
- [ ] Darshana-aligned agents in Mik's fleet

### Training the Darshana LLM ✅ (pipeline ready, awaiting GPU)
- [x] Training data generator — 329 darshana reasoning examples (331K tokens)
- [x] Curriculum converter — 1,461 entries from 29 lessons (965K tokens)
- [x] Fine-tuning infrastructure — LoRA on Llama/Mistral/Qwen (finetune.py)
- [x] Vritti reward model — 5-class classifier for RLHF (reward_model.py)
- [x] Evaluation suite — method adherence, depth, novelty, vritti (evaluate.py)
- [x] Serving infrastructure — Flask API with auto-routing (serve.py)
- [x] Kimi K2.5 pipeline — KTransformers + LlamaFactory (finetune_kimi.py)
- [x] Kimi K2.5 serving — MoE offloading with LoRA hot-swap (serve_kimi.py)
- [x] Kimi K2.5 setup script — one-command environment (setup_kimi.sh)

### AWS GPU Access ⏳ WAITING
- [x] AWS account verified (Heft Energy, 390449413787)
- [x] Active credits confirmed (~$1,098 used, credits still covering 100%)
- [x] On-Demand P instance quota requested (96 vCPUs, Case #177425473500754)
- [x] Spot P instance quota requested (96 vCPUs, Case #177425469800882)
- [ ] Quota approved — CHECK STATUS EACH SESSION
- [ ] Upload training data to S3
- [ ] Launch p4d.24xlarge spot (8× A100, ~$10-13/hr)
- [ ] Train all 8 adapters (~16-22 hrs, ~$160-200 covered by credits)
- [ ] Evaluate and publish adapters to HuggingFace

### Mik Integration
- [ ] Replace Mik's agent routing with Buddhi
- [ ] Add Smriti as Mik's persistent memory
- [ ] Add Vritti Filter to Mik's output pipeline
- [ ] Darshana-aligned agents in Mik's fleet

### Community
- [ ] Publish blog post
- [ ] Submit to Hacker News / AI Twitter
- [ ] Invite Sanskrit scholars to review curriculum
- [ ] Invite AI researchers to challenge the isomorphisms

### Advanced Architecture
- [ ] Multi-round Yaksha debate with actual LLM calls
- [ ] Ahamkara integration into live pipeline (not just standalone)
- [ ] Shakti auto-learning which model tier works best per darshana
- [ ] Cross-session memory building (Smriti across conversations)
- [ ] Vritti Filter as a real-time middleware (not post-hoc)

---

## Session Stats

Built across 1 session. ~48 parallel agents across 12 waves.
- Wave 1: 5 agents (Sanskrit Phase 1 completion + Philosophy + Connections)
- Wave 2: 9 agents (5 Upanishads + 3 Gita sections + Samkhya)
- Wave 3: 11 agents (Yoga Sutras + 5 remaining schools + 3 epics + 3 traditions)
- Wave 4: 6 agents (DarshanaLLM + Package + Yaksha + Ahamkara + Benchmark + Blog)
- Wave 5: 2 agents (Router POC + Vritti Filter POC)
- Wave 6: 3 agents (Deep prompts + Smart routing + Vritti self-catch fixes)
- Wave 7: 5 agents (Smriti + Pratyaksha + Manas + Shakti + Antahkarana)
- Wave 8: 3 agents (CLI harness + Setup/install + HTML reports)
- Wave 9: 2 agents (Claude Code plugin + MCP server)
- Wave 10: 3 agents (Training data generator + Fine-tune infra + Curriculum converter)
- Wave 11: 1 agent (Kimi K2.5 pipeline)
- Wave 12: AWS quota requests submitted

## Key Numbers
- Curriculum: 29 lessons, ~15,000 lines
- Architecture: 16 Python modules, ~14,000 lines of code
- Training data: 1,790 examples, ~1.3M tokens
- Tests: 48 passing, 95% router accuracy, 100% filter accuracy
- Plugin: 10 skills, 1 agent, 1 hook (installed in Claude Code)
- MCP: 9 tools, 2 resource types
- AWS: credits active, GPU quota pending
