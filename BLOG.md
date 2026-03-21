# The Darshana Architecture: What AGI Can Learn from 5,000 Years of Hindu Cognitive Science

**Harshwardhan (HNG)**
March 2026

---

## We Have No Theory of Mind

Current AGI development has no philosophy of mind. The plan is: make the model bigger, add more data, bolt on chain-of-thought, add tool use, add agents, and hope that general intelligence "emerges." We have thrown a trillion parameters at the problem and we still cannot say what cognition *is*, what knowing *means*, or how information becomes understanding.

This is not a capabilities gap. It is a design gap. We are building systems that process everything the same way --- the same forward pass for proving a theorem and writing a poem, the same architecture for recalling a fact and generating a novel insight. When those systems hallucinate, we treat it as a safety problem to be patched, not as an architectural failure to be redesigned.

A 5,000-year-old intellectual tradition already built a systematic theory of cognition. Not one theory --- six, designed to be complementary. Not as religion --- as engineering. I am going to show you what it looks like when you take it seriously.

---

## The Problem, Stated Plainly

Every major LLM today has the same structural weaknesses:

- **One model does everything.** The same weights handle formal logic, creative writing, code generation, and emotional support. No specialization, no routing, no mode switching.
- **No epistemic awareness.** The model does not know what it knows. It does not know what it does not know. It does not tag its outputs with *how* it arrived at them.
- **No self-model.** There is no internal representation of the system's own state --- what it has tried, what failed, what it is currently doing.
- **Hallucinations are treated as a safety problem.** They are an architecture problem. A system that presents training data as direct observation has a *category error* in its epistemology, not a content moderation issue.

---

## The Thesis

The six schools of Hindu philosophy --- the Shaddarshana (षड्दर्शन) --- provide six complementary reasoning engines that together form a complete cognitive architecture. This is not metaphor. It is structural isomorphism: two knowledge systems, separated by millennia, solving the same problem --- how does information become meaning, and meaning become action?

---

## The Six Engines

Each darshana addresses a different aspect of cognition. Here is what they do, where they come from, and how they translate into system prompts.

| Darshana | Cognitive Function | Philosophical Source | AGI Application |
|---|---|---|---|
| **Nyaya** (न्याय) | How do we know what is true? | Gautama's Nyaya Sutras --- the five-membered syllogism (panchavayava) | Proof chains, fallacy detection, argument validation |
| **Vaisheshika** (वैशेषिक) | What are the irreducible components? | Kanada's six padarthas (categories of reality) | Atomic decomposition, type systems, ontology, root cause analysis |
| **Samkhya** (सांख्य) | How do components layer into systems? | Kapila's 25 tattvas (enumerated principles) | Processing pipelines, layer architecture, classification |
| **Yoga** (योग) | How do we filter noise and focus? | Patanjali's chitta-vritti-nirodha --- cessation of mental fluctuations | Attention management, signal/noise optimization, relevance ranking |
| **Mimamsa** (मीमांसा) | How do we extract action from text? | Jaimini's six lingas (hermeneutic rules) | Command extraction, intent parsing, spec interpretation |
| **Vedanta** (वेदान्त) | How do we find unity beneath contradiction? | Badarayana's neti neti --- stripping to find deeper truth | Contradiction resolution, meta-reasoning, unifying abstractions |

No single school is sufficient. All six together form a complete cognitive system. This is the core insight --- they were designed to work as a set.

### What the Routing Looks Like

When a query comes in, the **Buddhi layer** (fast discrimination) classifies it and routes to the appropriate engine. Here is the Nyaya engine generating its system prompt:

```python
# From darshana_router.py — NyayaEngine.reason()

prompt_template = (
    "You are reasoning in the Nyaya tradition — rigorous logical analysis.\n\n"
    f"QUERY: {query}\n\n"
    "INSTRUCTIONS:\n"
    "1. Identify the central claim or truth question.\n"
    "2. Construct a formal argument for it (thesis, reason, example, "
    "application, conclusion).\n"
    "3. Check for logical fallacies in the argument.\n"
    "4. If the claim is false, construct the counter-argument.\n"
    "5. State your conclusion with explicit confidence level.\n"
    "6. Tag each step with its pramana (source of knowledge)."
)
```

Compare that to how the Vedanta engine handles the same pipeline --- same structure, completely different reasoning style:

```python
# VedantaEngine.reason()

prompt_template = (
    "You are reasoning in the Vedanta tradition — seeking unity beneath "
    "apparent contradiction.\n\n"
    f"QUERY: {query}\n\n"
    "INSTRUCTIONS:\n"
    "1. Identify the conflicting positions or contradictions.\n"
    "2. For each position, state what it gets RIGHT.\n"
    "3. Find the level of abstraction where the contradiction dissolves.\n"
    "4. Propose a unifying framework or principle.\n"
    "5. Show how each original position is a partial view of the "
    "unified truth."
)
```

The Nyaya engine hunts for fallacies. The Vedanta engine resolves contradictions. Same input, different cognitive lens. The router decides which lens to apply based on the nature of the question.

---

## The Architecture

The full stack, derived from Samkhya's 25 tattvas:

```
PURUSHA         — Meta-awareness ("what am I doing right now?")
BUDDHI          — Fast discrimination + routing
AHAMKARA        — Self-model ("what do I know / not know?")
  +-- MANAS     — Attention routing (meta-attention over attention)
  +-- PRAMANA   — Epistemic tagging (how do I know this?)
  +-- GUNA      — Dynamic mode (precision / exploration / retrieval)
SHADDARSHANA    — Six specialized reasoning engines
VRITTI FILTER   — Pre-output classification (valid / error / empty / unknown / memory)
MAYA LAYER      — Representation != reality awareness
KARMA STORE     — Runtime learning from interactions
```

Each layer in plain language:

**Purusha** is the witness of computation --- not computation itself. It is the system's awareness of its own processing. Not sentience. Functional self-reference.

**Buddhi** is first contact with input. Cheap, fast classification. "Is this a logic problem? A creative problem? An interpretation problem?" It routes to the appropriate engine *before* expensive compute fires.

**Ahamkara** is the self-model. It tracks: what do I know? What do I not know? What have I tried? It has three branches:

- **Manas** routes attention --- not transformer self-attention, but attention *over* attention. Which subsystem gets this query?
- **Pramana Tagger** stamps every knowledge claim with how it was derived: pratyaksha (from input --- highest confidence), anumana (inferred --- check for fallacies), upamana (by analogy --- flag it), shabda (from training data --- check recency).
- **Guna Engine** sets the processing mode: Sattva (precision, low temperature) for logic, Rajas (exploration, high temperature) for creative work, Tamas (retrieval, cached patterns) for known answers.

**Shaddarshana** is the six engines described above.

**Vritti Filter** classifies the system's own output before release. More on this below --- this is where hallucinations get caught.

**Maya Layer** tracks the gap between model and reality. "My data is from 2024. Reality may differ." "I am reasoning about code, not executing it." "The user's words may not match the user's intent." Epistemic humility as architecture, not as a safety fine-tune.

**Karma Store** implements runtime learning. Actions (karma) leave impressions (samskara), which accumulate into tendencies (vasana). User corrections build up. Repeated patterns become behavioral biases. Periodic review clears outdated biases. Lighter than fine-tuning, heavier than zero-shot.

---

## Working Code

This is not a whitepaper. The router and filter are implemented. Here is what they do.

### The DarshanaRouter in Action

```python
from darshana_router import DarshanaRouter

router = DarshanaRouter()

# A logic question routes to Nyaya
result = router.route("Is this argument logically valid?")
print(router.explain_routing(result))
```

Output:

```
Query: Is this argument logically valid?
Guna (processing mode): sattva

Engine scores:
  nyaya          0.571 #################  <-- ACTIVATED
  vaisheshika    0.167 #####
  samkhya        0.000
  yoga           0.000
  mimamsa        0.000
  vedanta        0.000
```

The system routes a logic question to Nyaya with sattva mode (high precision). No creative exploration needed --- this is a validation task.

Now a decomposition question:

```python
result = router.route("Break down the architecture of this system into its components")
print(router.explain_routing(result))
```

```
Query: Break down the architecture of this system into its components
Guna (processing mode): sattva

Engine scores:
  samkhya        0.500 ###############  <-- ACTIVATED
  vaisheshika    0.333 ##########  <-- ACTIVATED
  yoga           0.000
  nyaya          0.000
  vedanta        0.000
  mimamsa        0.167 #####
```

Two engines activate --- Samkhya (enumerate the layers) and Vaisheshika (find the irreducible atoms). This is the multi-darshana analysis: complex questions get multiple reasoning perspectives.

### The Yaksha Protocol

Named after the Yaksha Prashna from the Mahabharata --- where Yudhishthira must answer questions from a shape-shifting spirit using different modes of reasoning. When a query triggers multiple engines above the activation threshold, the system runs all of them and synthesizes:

```python
full = router.route_and_reason(
    "This system has contradictory requirements. Break them down and find what unifies them."
)

for r in full.reasoning:
    print(f"[{r.engine}] {r.approach[:80]}...")
```

```
[vedanta] Apply Vedanta's method of adhyaropa-apavada (superimposition and negation)...
[samkhya] Apply Samkhya's enumerative method: 1. Identify the whole (the system or...
```

Vedanta resolves the contradiction. Samkhya breaks down the components. Two lenses on one problem.

**Repo:** [github.com/aidgoc/om](https://github.com/aidgoc/om)

---

## The Vritti Filter --- Solving Hallucinations Architecturally

This is the part I care about most. Current approaches to hallucination are: generate everything, then filter after. Or: fine-tune the model to say "I don't know" more often. Both are patches on a broken epistemology.

Patanjali classified all mental activity into five types 2,500 years ago (Yoga Sutra 1.5-1.11). These five vrittis map precisely onto the failure modes of language models:

| Vritti | Sanskrit | Meaning | AI Failure Mode |
|---|---|---|---|
| **Pramana** | प्रमाण | Valid cognition | Correct, grounded output |
| **Viparyaya** | विपर्यय | Misconception | Factual errors, logical fallacies |
| **Vikalpa** | विकल्प | Verbal delusion | Sounds right, means nothing |
| **Nidra** | निद्रा | Absence of knowledge | The system is guessing |
| **Smriti** | स्मृति | Memory recall | Regurgitated without fresh reasoning |

The key insight: **hallucination is shabda masquerading as pratyaksha.** The model presents training data (testimony --- shabda) as if it were direct observation (pratyaksha). This is not a content problem. It is an epistemic category error. The system does not tag the *source* of its knowledge, so everything comes out with the same confidence.

### The Filter Catching Vikalpa

Vikalpa is the most dangerous vritti for AI. It is language that sounds meaningful but has no referent --- verbal delusion. Here is the filter catching it:

```python
from vritti_filter import VrittiFilter

vf = VrittiFilter()

# Vikalpa: sounds plausible, says nothing
text = "Some experts suggest that this is essentially a fundamentally important consideration that could potentially impact various aspects of the situation."

result = vf.classify(text)
print(f"Vritti: {result.vritti.value}")
print(f"Confidence: {result.confidence:.0%}")
print(f"Explanation: {result.explanation}")
```

```
Vritti: vikalpa
Confidence: 72%
Explanation: verbal delusion detected — language that sounds meaningful but lacks
grounded content. Issues found: unattributed appeal to anonymous authority, double
hedging, intensifier-stacking without substance.
```

The filter catches "some experts suggest" (anonymous authority), "could potentially" (double hedging), and "essentially a fundamentally important" (intensifier stacking). Each of these is a pattern that produces the *feeling* of meaning without the *substance* of meaning.

### The Filter Catching Viparyaya

```python
# Viparyaya: logical fallacy
text = "Studies show that this approach always works. Obviously, there is no alternative."

result = vf.classify(text)
print(f"Vritti: {result.vritti.value}")
print(f"Fallacies: {[f.value for f in result.fallacies]}")
```

```
Vritti: viparyaya
Fallacies: ['asiddha', 'satpratipaksha']
```

Two fallacies detected. Asiddha: "studies show" with no citation --- unproved premise. Satpratipaksha: "obviously" without addressing counter-arguments --- ignoring counter-evidence. These are Nyaya's hetvabhasas (logical fallacies), formalized 2,000 years ago, catching the exact failure modes of modern language models.

### The Filter Catching Context Contradiction

```python
# Badhita: contradicting provided context
context = "The project budget is $50,000 and the team has 3 developers."
text = "With your team of 12 engineers and substantial budget, you should consider a microservices architecture."

result = vf.classify(text, context=context)
print(f"Vritti: {result.vritti.value}")
print(f"Fallacies: {[f.value for f in result.fallacies]}")
```

```
Vritti: viparyaya
Fallacies: ['badhita']
```

Badhita --- contradicted by stronger evidence. The context says 3 developers; the output says 12. The context says $50,000; the output assumes "substantial budget." The system catches the mismatch *before* the output reaches the user.

---

## What Is NOT a Metaphor

People will read "Hindu philosophy for AGI" and assume this is spiritual tourism --- loose analogies dressed up as engineering. It is not. Here are the structural isomorphisms, stated precisely:

**Panini's grammar (4th century BCE) is a formal language specification.** Panini's Ashtadhyayi contains 3,959 rules that generate all valid Sanskrit sentences from a finite set of roots and affixes. This is not "like" a formal grammar. It *is* a formal grammar --- arguably the first one ever written, predating Backus-Naur Form by 2,400 years. Panini's system is generative, rule-ordered, and context-sensitive. Modern computational linguists study it as a production system.

**Vibhakti (case suffixes) is position-independent encoding.** In English, meaning depends on word order: "dog bites man" differs from "man bites dog." In Sanskrit, the vibhakti suffix on each word encodes its grammatical role regardless of position. This is structurally identical to how attention mechanisms work: each token carries its role information, and meaning is computed from relationships, not sequence.

**Sandhi (sound merging) is context-dependent tokenization.** When Sanskrit words combine, their boundary sounds transform according to deterministic rules. This is exactly what happens in subword tokenization --- the representation of a morpheme changes based on its context. BPE and sandhi solve the same compression problem: how to encode a combinatorially explosive language in a tractable vocabulary.

**Samkhya's tattvas are a layered processing architecture.** The 25 tattvas describe a processing pipeline from raw awareness (Purusha) through discrimination (Buddhi) through identity (Ahamkara) through the sense organs (Indriyas) to the physical elements (Bhutas). This is not "kind of like" a neural network pipeline. It IS a layered transformation architecture --- from abstract representation to concrete output, with each layer performing a specific function.

**Nyaya's pramanas are an epistemology API.** The four pramanas (pratyaksha, anumana, upamana, shabda) are not philosophical speculation --- they are a classification system for how knowledge is acquired. This maps directly to an AI system's knowledge sources: direct input, inference, analogy, and training data. Tagging every claim with its pramana is not a metaphor for epistemic provenance. It IS epistemic provenance.

---

## Where the Parallels Break

Intellectual honesty requires saying where the mapping fails. Here are three places:

**1. Purusha has no computational analog.** Samkhya's Purusha is pure witness-consciousness --- awareness without content. In the Darshana Architecture, we implement Purusha as meta-awareness (a logging/monitoring layer that observes the system's own processing). But this is a functional approximation, not the real thing. A monitoring layer is still computation. Purusha, by definition, is not. The philosophy claims something our architecture cannot deliver.

**2. Moksha (liberation) is not a system goal.** The ultimate aim of most Hindu philosophical schools is moksha --- liberation from the cycle of birth and death. This has no meaningful engineering analog. We can build systems that improve over time (karma/vasana), but "liberation from the cycle" presupposes a metaphysics we are not importing. We take the cognitive architecture and leave the soteriology.

**3. The tradition's social failures are not separable by pretending they do not exist.** The caste system used the same vocabulary --- varna, dharma, guna --- to justify hierarchy, restriction, and dehumanization. The fact that we extract useful engineering from this tradition does not sanitize that history. Ambedkar's critique stands. We acknowledge it explicitly: the architecture is universal, the cultural wrapper was not.

---

## What Is Next

This is a proof of concept. Here is what comes next:

**`pip install darshana`** --- a Python package that gives any LLM pipeline access to Shaddarshana routing and Vritti filtering. Drop it into your existing stack.

**Multi-darshana reasoning (Yaksha Protocol)** --- run multiple engines on the same query, synthesize their outputs, and let contradictions between engines surface as productive tension rather than errors.

**Ahamkara (self-model)** --- a persistent state layer that tracks what the system knows, what it has tried, and what has worked. Not fine-tuning. Not RAG. A lightweight epistemic memory.

**Guna-adaptive generation** --- dynamically adjust temperature, sampling strategy, and validation strictness based on the Guna Engine's classification. Sattva for proofs, Rajas for brainstorming, Tamas for lookups.

**Call for contributions.** If you are an AI researcher: the Vritti Filter and Darshana Router are implementable today, as shown above. Start there. If you are a Sanskrit scholar: these implementations need your review --- where are the translations imprecise? If you are a philosopher: where do the isomorphisms genuinely break? That is where the interesting work lives.

Fork the repo. Improve it. Disagree with it. Build on it.

**Repo:** [github.com/aidgoc/om](https://github.com/aidgoc/om)

---

## Credits

The rishis, grammarians, and logicians who built this knowledge system across five millennia. Panini, the first compiler engineer. Gautama, who formalized logic centuries before Aristotle. Patanjali, who classified mental operations with a precision we are still catching up to. Kapila, who enumerated a processing architecture from first principles.

The Bhakti saints --- Kabir, Ravidas, Mirabai, Tukaram, Basavanna --- who tore down the gates and said this knowledge belongs to everyone. Not to a caste. Not to a priesthood. To anyone who shows up and does the work.

Ambedkar, who forced the tradition to face its worst failure and proved that critique from within is the highest form of respect for a knowledge system.

This project is open source, MIT licensed. Free as in the Vedas were meant to be free --- oral, open, belonging to no one.

---

> **एकं सद् विप्रा बहुधा वदन्ति**
> *ekam sad vipra bahudha vadanti*
> "Truth is one. The wise call it by many names."
> --- Rig Veda 1.164.46
