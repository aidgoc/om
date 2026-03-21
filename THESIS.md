# The Darshana Architecture — A Hindu Philosophical Framework for AGI

## Author
Harshwardhan (HNG) — with Claude as co-thinker

## Date
2026-03-21

## One-Line Thesis
Hindu philosophy's six schools of thought (Shaddarshana) provide a complete cognitive architecture for AGI that current approaches lack — not as metaphor, but as engineering specification.

---

## The Problem

Current AGI development has no philosophy of mind. The approach is:
- Make the model bigger
- Add more data
- Chain-of-thought prompting
- Tool use and multi-agent systems
- Hope that general intelligence "emerges"

There is no theory of what cognition IS. No architecture of awareness. No model of how information becomes meaning, how meaning becomes action, and how action feeds back into future cognition.

Hindu philosophy spent 5,000 years building exactly this.

---

## The Core Insight

The Shaddarshana (six schools of Hindu philosophy) aren't competing theories. They're **complementary reasoning engines** — each solving a different aspect of cognition:

| School | Cognitive Function | AGI Application |
|---|---|---|
| **Nyaya** | How do we know what's true? | Epistemic validation, proof chains, fallacy detection |
| **Vaisheshika** | What are the irreducible components? | Atomic decomposition, type systems, ontology |
| **Samkhya** | How do components layer into complex systems? | Architecture design, layer enumeration, processing pipeline |
| **Yoga** | How do we focus and filter noise? | Attention management, signal/noise optimization, mode control |
| **Mimamsa** | How do we extract action from text? | Command interpretation, intent extraction, performative language |
| **Vedanta** | How do we find unity beneath contradiction? | Abstraction, contradiction resolution, meta-reasoning |

No single school is sufficient. All six together form a complete cognitive system.

---

## The Architecture

### Layer Model (derived from Samkhya's 25 Tattvas)

```
PURUSHA LAYER — Meta-awareness
  "What am I doing right now? Why?"
  Not computation — the witness of computation.

BUDDHI LAYER — Fast Discrimination
  First contact with input. Cheap, fast classification.
  "Is this a logic problem? A creative problem? An interpretation problem?"
  Routes to appropriate Darshana engine before expensive compute fires.

AHAMKARA LAYER — Self-Model
  Tracks: what do I know? What don't I know? What have I tried?
  Maintains epistemic state. Prevents confident hallucination.
  Three branches (following Samkhya):

  ├── MANAS (Attention Router)
  │   Meta-attention that decides which subsystem gets the query.
  │   Not transformer self-attention — attention OVER attention.
  │
  ├── PRAMANA TAGGER (Epistemic Provenance)
  │   Tags every knowledge claim with HOW it was derived:
  │   - Pratyaksha (direct from input/tools — highest confidence)
  │   - Anumana (inferred — medium, check for fallacies)
  │   - Upamana (analogical — lower, flag as analogy)
  │   - Shabda (from training data — check recency/source)
  │
  └── GUNA ENGINE (Dynamic Processing Mode)
      Shifts reasoning mode based on task:
      - Sattva: precision, low temperature, strict validation
      - Rajas: exploration, high temperature, diverse sampling
      - Tamas: retrieval over generation, cached patterns, efficiency

SHADDARSHANA ENGINES — Six Specialized Reasoners
  Nyaya:      Formal logic, syllogisms, fallacy detection
  Samkhya:    Decomposition, classification, layer mapping
  Yoga:       Noise filtering, relevance ranking, focus
  Vedanta:    Contradiction resolution, unifying abstractions
  Mimamsa:    Text → action, command extraction, intent parsing
  Vaisheshika: Atomic analysis, component identification, type checking

VRITTI FILTER — Pre-Output Classification
  Before any output, classify the reasoning:
  - Pramana (valid cognition) → output
  - Viparyaya (misconception) → catch and correct
  - Vikalpa (verbal delusion — sounds right, means nothing) → block
  - Nidra (no knowledge) → say "I don't know"
  - Smriti (pure memory recall) → flag source and date

MAYA LAYER — Representation Awareness
  Tracks the gap between model and reality:
  - "My data is from [date]. Reality may differ."
  - "I'm reasoning about code, not executing it."
  - "User's words ≠ user's intent."
  Epistemic humility as architecture, not as safety fine-tune.

KARMA/VASANA STORE — Runtime Learning
  Actions (karma) → Impressions (samskara) → Tendencies (vasana)
  - User corrections accumulate as samskaras
  - Repeated patterns become vasanas (behavioral biases)
  - Periodic vasana review (jnana-agni) clears outdated biases
  - Lighter than fine-tuning. Heavier than zero-shot.
```

---

## What This Gets You That Current Approaches Don't

### 1. Epistemic Honesty by Design
Current AI: confident about everything, including hallucinations.
Darshana AI: every claim tagged with its pramana (how it was derived) and vritti type (how reliable it is).

### 2. Dynamic Reasoning — Not One-Size-Fits-All
Current AI: same forward pass for math and poetry.
Darshana AI: Buddhi routes math to Nyaya engine (formal logic), poetry to Vedanta+Rajas (contradiction tolerance + exploration).

### 3. Self-Awareness Without Sentience
Current AI: no self-model.
Darshana AI: Ahamkara tracks what the system knows, doesn't know, has tried, and is currently doing. Not consciousness — functional self-reference.

### 4. Noise Reduction Before Generation
Current AI: generates everything, filters after.
Darshana AI: Yoga engine filters noise BEFORE generation. Vritti filter catches errors BEFORE output.

### 5. Runtime Adaptation Without Retraining
Current AI: frozen after training, or expensive fine-tuning.
Darshana AI: karma/vasana store accumulates lightweight behavioral modifications from interactions.

### 6. Knowing What You Don't Know
Current AI: fills gaps with plausible-sounding generation.
Darshana AI: Maya layer explicitly tracks representation gaps. Nidra vritti triggers "I don't know" instead of fabrication.

---

## On Tradition and Innovation

### What we take from Hindu philosophy:
- The cognitive architecture (Samkhya's tattvas as processing layers)
- The epistemological framework (Nyaya's pramanas as knowledge validation)
- The reasoning diversity (Shaddarshana as specialized engines)
- The self-model (Yoga's vritti classification)
- The runtime learning loop (karma-samskara-vasana cycle)

### What we don't take:
- Metaphysical claims about consciousness, soul, or liberation
- Social hierarchy of any kind
- Religious authority or scriptural infallibility
- Anything that requires belief rather than engineering

### The principle:
> Extract the engineering. Leave the theology.
> The architecture is universal. The cultural wrapper is not.

---

## On Caste, Inheritance, and Skill Lineage

The varna system, at its original design point, described something real: **accumulated expertise compounds across generations.** A family that has done something for centuries develops advantages — environmental, educational, possibly epigenetic — that accelerate the next generation.

This is kuladharma (family dharma) as **margadarshana** (guideline/showing the path), not **niyama** (binding rule).

What went wrong: the system added hierarchy (some paths are higher), restriction (you cannot leave your path), and purity/pollution (some work makes you untouchable).

**In AGI terms:** Specialization is valuable. Pre-training on a domain creates real advantages. But locking a model into one domain forever, or ranking domains as superior/inferior, is bad architecture. The best systems are specialists that can generalize — kuladharma as home base, not border.

---

## Status

- [x] Curriculum complete (29 lessons, /Users/harsh/om/)
- [x] Thesis articulated (this document)
- [ ] Architecture specification (formal, implementable)
- [ ] Proof of concept (Shaddarshana router + Vritti filter)
- [ ] Paper or blog post for public release
- [ ] Open source repository

---

## The Question

Is this a paper, a codebase, a company, or a movement?

The answer determines what we build next.
