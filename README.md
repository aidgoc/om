# OM — The Darshana Architecture

**Hindu philosophy as a cognitive architecture for AI.**

Not metaphor. Not spiritual tourism. Engineering specification derived from 5,000 years of systematic inquiry into how information becomes meaning.

```
pip install -e .
darshana "Is this argument logically valid?"
```

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/aidgoc/om.git
cd om
pip install -e .

# Route a query through the six reasoning engines
darshana "Is this argument logically valid?"

# Multi-engine analysis (up to 3 perspectives)
darshana --multi "Should we rewrite our backend in Rust?"

# Run with real Anthropic LLM calls
export ANTHROPIC_API_KEY="sk-ant-..."
darshana --llm "What is consciousness?"

# Classify output quality
darshana --filter "The moon is made of cheese"

# Run built-in demos
darshana --demo
```

Or use the one-command installer:

```bash
curl -sSL https://raw.githubusercontent.com/aidgoc/om/main/setup.sh | bash
```

---

## What Is This?

Two things:

### 1. A Cognitive Architecture

A working Python implementation where queries flow through a pipeline inspired by the Antahkarana (inner instrument) of Samkhya/Vedanta philosophy:

```
                          QUERY
                            |
                     +------v------+
                     |  Pratyaksha |  Perception — parse, detect type,
                     |  (perceive) |  extract structure from raw input
                     +------+------+
                            |
                     +------v------+
                     |   Smriti    |  Memory — recall relevant samskaras
                     |  (remember) |  (past experiences) from SQLite
                     +------+------+
                            |
                     +------v------+
                     |    Manas    |  Attention — assemble context,
                     |  (assemble) |  rank relevance, manage token budget
                     +------+------+
                            |
                     +------v------+
                     |   Buddhi    |  Routing — classify query, select
                     |   (route)   |  darshana engine(s), set guna mode
                     +------+------+
                            |
              +-------------+-------------+
              |             |             |
        +-----v----+  +----v-----+  +----v-------+
        |  Nyaya   |  | Samkhya  |  |  Vedanta   |  ... up to 6 engines
        | (reason) |  | (reason) |  |  (reason)  |  run in parallel
        +-----+----+  +----+-----+  +----+-------+
              |             |             |
              +-------------+-------------+
                            |
                     +------v------+
                     |   Vritti    |  Filter — classify output as
                     |  (filter)   |  valid / error / empty / absent / recalled
                     +------+------+
                            |
                     +------v------+
                     |  Ahamkara   |  Self-model — track what I know,
                     |   (learn)   |  what I tried, where I failed
                     +------+------+
                            |
                     +------v------+
                     |   Shakti    |  Compute — track cost, select model
                     |  (budget)   |  tier, enforce daily limits
                     +------+------+
                            |
                         RESPONSE
```

Every step is optional. The pipeline degrades gracefully. Minimum viable path: Route -> Reason -> Respond.

### 2. A Complete Hinduism Curriculum (29 Lessons)

Built in a single session using 25 parallel AI agents. Covers Sanskrit, primary texts (Upanishads, Gita, Yoga Sutras), all six Darshana schools, and living traditions. Every lesson includes Sanskrit in Devanagari + transliteration + root meaning.

### 3. A Thesis

The argument that Hindu philosophy's six schools provide a complete cognitive architecture that current AI approaches lack. See [THESIS.md](THESIS.md).

---

## The Six Darshanas

These are not metaphors. They are structural isomorphisms — two knowledge systems solving the same problem.

| School | Sanskrit Root | Cognitive Function | What It Does |
|---|---|---|---|
| **Nyaya** | नय (naya, rule) | Epistemology | Proof chains, fallacy detection, logical validation |
| **Vaisheshika** | विशेष (vishesha, distinction) | Ontology | Atomic decomposition, type systems, root cause |
| **Samkhya** | सङ्ख्या (sankhya, enumeration) | Architecture | Layer decomposition, classification, pipeline design |
| **Yoga** | युज् (yuj, to yoke) | Attention | Noise filtering, focus, relevance ranking |
| **Mimamsa** | मीमांसा (mimamsa, investigation) | Interpretation | Command extraction, intent parsing, action planning |
| **Vedanta** | वेद + अन्त (end of knowledge) | Synthesis | Contradiction resolution, abstraction, meta-reasoning |

---

## Module Reference

| Module | Sanskrit | Description |
|---|---|---|
| `darshana_router.py` | Buddhi (बुद्धि) | Routes queries to the right engine(s), classifies guna mode, tags pramana |
| `vritti_filter.py` | Vritti (वृत्ति) | Five-fold output classification: valid, error, empty, absent, recalled |
| `darshana_llm.py` | — | Anthropic Claude wrapper with darshana-specific system prompts |
| `antahkarana.py` | Antahkarana (अन्तःकरण) | Master pipeline wiring all components together |
| `smriti.py` | Smriti (स्मृति) | SQLite-backed persistent memory with samskaras and vasanas |
| `shakti.py` | Shakti (शक्ति) | Compute/cost management, model tier selection, budget enforcement |
| `manas.py` | Manas (मनस्) | Attention and context management, token budget allocation |
| `ahamkara.py` | Ahamkara (अहंकार) | Self-model: knowledge map, capability tracking, gap detection |
| `pratyaksha.py` | Pratyaksha (प्रत्यक्ष) | Perception layer: input parsing, structure detection, type classification |
| `yaksha.py` | Yaksha (यक्ष) | Multi-darshana parallel reasoning protocol |
| `prompts.py` | — | Darshana-specific system prompts for each reasoning engine |

---

## CLI Reference

```
darshana [OPTIONS] QUERY

Positional:
  QUERY                     The query or text to process

Options:
  --multi                   Activate multiple engines (up to 3 perspectives)
  --darshana NAME           Force a specific engine: nyaya, samkhya, yoga,
                            vedanta, mimamsa, vaisheshika
  --filter                  Run Vritti Filter instead of router
  --llm                     Use real Anthropic API calls (requires API key)
  --explain                 Show routing classification only (no API call)
  --model MODEL             Anthropic model (default: claude-sonnet-4-20250514)
  --api-key KEY             Anthropic API key (or set ANTHROPIC_API_KEY)
  --demo                    Run built-in demos
  -h, --help                Show help
```

**The three gunas** (processing modes):

| Guna | Mode | Behavior |
|---|---|---|
| Sattva | Precision | Low temperature, strict validation, formal reasoning |
| Rajas | Exploration | High temperature, creative divergence, brainstorming |
| Tamas | Retrieval | Cached patterns, efficient lookup, known-answer recall |

---

## Examples

### Route a logic question through the Buddhi layer

```bash
$ darshana "All humans are mortal. Socrates is human. Therefore Socrates is mortal."

Darshana: nyaya
Guna:     sattva

Approach:
  Syllogistic validation via Nyaya's five-member proof (panchavayava)...

Prompt template:
  You are a Nyaya logician. Validate this argument using...
```

### Multi-engine analysis

```bash
$ darshana --multi "Should we rewrite our backend in Rust?"

Activated 3 engine(s):

=== SAMKHYA ===
Approach: Decompose the decision into layers — current architecture,
  migration cost, team capability, performance requirements...

=== NYAYA ===
Approach: Evaluate the logical validity of "rewrite = better performance"...

=== VEDANTA ===
Approach: Find the underlying truth — is this really about Rust,
  or about architectural debt?...
```

### Classify output with Vritti Filter

```bash
$ darshana --filter "Studies show that 73% of statistics are made up on the spot"

Vritti:     viparyaya
Confidence: 87.3%
Explanation: Self-referential claim with fabricated statistic
Fallacies:  ungrounded_claim
Suggestions:
  - Cite the actual source for this statistic
  - Distinguish between the meta-joke and factual claim
```

### Use with real LLM calls

```bash
$ darshana --llm "What is the relationship between computation and consciousness?"

Darshana:    vedanta, samkhya
Guna:        rajas
Vritti:      pramana
Pramana:     anumana
Confidence:  0.82
Model:       claude-sonnet-4-20250514
Latency:     3241ms
Tokens:      847 in / 1923 out

--- RESPONSE ---
The question maps to a fundamental tension that both Vedanta and
computational theory grapple with...
```

---

## Python API

```python
# Quick — single query through the full pipeline
from darshana import Antahkarana

mind = Antahkarana(api_key="sk-ant-...")
response = mind.think("Should we rewrite our backend in Rust?")

print(response.text)           # The answer
print(response.darshana)       # Which engine(s) reasoned
print(response.vritti)         # Output quality classification
print(response.cost)           # What this query cost in USD
print(response.trace)          # Full pipeline trace
```

```python
# Direct — use the router without LLM calls
from darshana import DarshanaRouter

router = DarshanaRouter()
result = router.route_and_reason("Prove that X implies Y")

print(result.routing.primary)  # "nyaya"
print(result.routing.guna)     # Guna.SATTVA
```

```python
# Specific engine — force a particular darshana
from darshana import NyayaEngine

nyaya = NyayaEngine()
output = nyaya.reason("All swans are white. This bird is white. Therefore it is a swan.")
print(output.approach)         # Identifies the affirming-the-consequent fallacy
```

```python
# Filter — classify any text
from darshana import VrittiFilter

vf = VrittiFilter()
result = vf.classify("The earth is flat according to my research")
print(result.vritti)           # Vritti.VIPARYAYA (error/misperception)
print(result.confidence)       # 0.94
print(result.fallacies)        # [Fallacy.UNGROUNDED_CLAIM, ...]
```

```python
# Memory — persistent samskaras across sessions
from src.smriti import SmritiStore

store = SmritiStore(db_path="~/.darshana/db/smriti.db")
store.record_samskara(query="Rust rewrite", response="...", domain="engineering")
memories = store.recall(query="backend architecture", top_k=5)
```

```python
# Budget — track and limit compute costs
from src.shakti import ShaktiManager

shakti = ShaktiManager(budget_daily=10.0)
print(shakti.remaining_budget())  # $8.47
print(shakti.today_summary())     # {calls: 23, cost: $1.53, ...}
```

---

## Curriculum Structure

```
om/
├── sanskrit/          6 lessons — alphabet, sandhi, vibhakti, verbs, numbers, shlokas
├── texts/            12 lessons — Upanishads, Gita, Yoga Sutras, epics, Puranas
├── philosophy/        7 lessons — all 6 Darshanas + Vedas overview
├── practices/         3 lessons — Bhakti, Tantra/Shakta, modern thought
├── connections/       1 essay  — structural parallels: Hindu philosophy <-> AI/ML
├── src/              11 modules — the working architecture implementation
├── tests/             benchmarks and test suites
├── THESIS.md          the AGI architecture proposal
├── BLOG.md            narrative of how this was built
└── README.md          you are here
```

---

## How This Was Built

25 parallel AI agents. 3 waves. One session.

Each agent received a focused brief and wrote independently — no shared context between agents. Coherence emerged from shared rules, not central coordination.

This mirrors the Vedic oral tradition: different shakhas (schools) preserved different parts independently across centuries, coherent through shared chandas (meter) and sandhi (rules).

---

## What's Honest

This project takes Hindu philosophy seriously as a knowledge system while being honest about what the tradition got wrong:

**What we keep:** The cognitive architecture, the epistemological framework, the reasoning diversity, the skill lineage (parampara), the compositional language.

**What we drop:** Caste hierarchy, gender restriction, purity/pollution frameworks, ritual as transaction, exclusive claims to authority. The tradition's own reformers — the Bhakti saints, Ambedkar, the Upanishads themselves — already made the case.

**The principle:** Inherited advantage as a launchpad, not a cage.

---

## Development

```bash
# Install with dev dependencies
make install

# Run tests
make test

# Run benchmarks
make benchmark

# Run all demos
make demo

# Lint
make lint

# Clean temp files
make clean
```

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step getting started guide.

---

## Contributing

Fork it. Improve it. Translate it. Disagree with it. Build on the architecture.

**If you're an AI researcher:** The Shaddarshana Router and Vritti Filter are implementable today. The Antahkarana pipeline is the integration point. Start there.

**If you're a Sanskrit scholar:** These lessons were written by AI agents. They need expert review. Corrections welcome.

**If you're a philosopher:** Challenge the isomorphisms. Where do the parallels genuinely break? That's where the interesting work is.

**If you're a developer:** Pick a module. Write tests. Improve the prompts. The `src/` directory is where the architecture lives.

```bash
# Development workflow
git clone https://github.com/aidgoc/om.git
cd om
pip install -e ".[dev]"
make test
# hack on things
make test
# submit PR
```

---

## License

MIT. Free as in the Vedas were free — oral, open, belonging to no one.

---

## Credits

- The rishis, grammarians, and philosophers who built this over 5,000 years
- The Bhakti saints who tore down the gates
- Ambedkar, who forced the tradition to face its worst failure
- Panini, the first compiler engineer
- Built by Harshwardhan (HNG) — [@aidgoc](https://github.com/aidgoc) — with Claude (Anthropic)

> **ekam sad vipra bahudha vadanti**
> "Truth is one. The wise call it by many names."
> — Rig Veda 1.164.46
