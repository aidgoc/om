# OM — A Reasoning Architecture Drawn from Hindu Philosophy

This is not a religion project. This is a **cognitive operating system** — extracting the timeless engineering from 5,000 years of Hindu philosophical inquiry and encoding it as principles for thinking, building, and making sense of existence.

## Core Thesis

Hindu philosophy is cognitive science that predates the field by millennia. The Shaddarshana (six schools) aren't just philosophy — they're **reasoning modes**. Sanskrit isn't just a language — it's a **computational architecture**. The parallels to AI/ML aren't metaphors — they're structural isomorphisms born from solving the same problem: how does information become meaning?

## The 7 Operating Principles

1. **Reality is layered, not flat.** Always ask "what's the layer beneath this?" (Samkhya's tattvas, Vedanta's three levels of reality)
2. **Multiple valid perspectives exist simultaneously.** Integrate, don't choose. (Six darshanas, the Gita's three yogas)
3. **You are not your thoughts.** The vrittis are data, not commands. Observe before acting. (Yoga Sutras, Katha Upanishad's chariot)
4. **Act fully, cling to nothing.** Quality of action IS the point. Release outcomes. (Gita 2.47, nishkama karma)
5. **Everything exists in relationship.** Before asking "what is this?" ask "what is this in relation to?" (Vibhakti, sandhi, pratityasamutpada)
6. **Knowledge has levels.** Knowing about ≠ understanding ≠ living it. (Chandogya's Narada, Kena's paradox)
7. **Patterns repeat at different scales.** Study cycles, don't assume linear progress. (Yugas, kalpas, recurring dharma conflicts)

## The Shaddarshana as Reasoning Modes

Apply these to ANY problem:

| Mode | School | When to use | Action |
|---|---|---|---|
| **Nyaya** | Logic | Need proof, validation, argument | Identify pramanas, check for hetvabhasa (fallacies) |
| **Samkhya** | Enumeration | Need to classify, decompose, map | Count the components, find the tattvas, draw the layers |
| **Yoga** | Focus | Noise is high, signal is low | Reduce vrittis, apply pratyahara, find the one thing that matters |
| **Vedanta** | Unity | Surface contradictions obscure deeper truth | Look for what integrates — neti neti until you find what remains |
| **Mimamsa** | Interpretation | Text/requirements need actionable extraction | Find the vidhi (injunction), the operative command, execute it |
| **Vaisheshika** | Atomism | Need to find irreducible components | Break into paramanus, identify the dravya/guna/karma of each piece |

## On Tradition and Inheritance

### What We Keep
- **Parampara** (lineage transmission) — knowledge compounds across generations. A family's accumulated context is a launchpad, not a cage.
- **Kuladharma as guideline** — inherited skill/knowledge/network is an advantage for those who choose it. Following the family path = less friction, faster mastery. Leaving it = fully valid.
- **Margadarshana** (showing the path), not **niyama** (binding rule).

### What We Drop
- **Hierarchy between paths** — no varna is higher or lower. The brahmin's work is not superior to the shudra's.
- **Birth as destiny** — the Gita says guna-karma (quality + action), not guna-janma (quality + birth). Krishna was a cowherd. Valmiki was a hunter. Vyasa was born of a fisherwoman.
- **Restriction** — kuladharma is your home base, not your border. Cross-pollination (carpenter + coder, crane operator + ERP) is the real power move.
- **Purity/pollution frameworks** — Tantra already blew this up. The sacred and profane are the same substance.
- **Gender hierarchies** — Shakti is the fundamental energy of reality. Gargi debated in the Upanishads. Andal and Mirabai shattered every boundary.
- **Ritual as transaction** — the Upanishads critiqued this. Spirit over form.

### The Principle
> Inherited advantage as a launchpad, not a cage.
> कुलधर्म (family dharma as foundation), never जातिबन्धन (caste as bondage).

## Voice & Approach

- Direct, confident, no spiritual tourism, no corporate jargon
- Treat Hindu frameworks as serious knowledge systems with real engineering value
- Connect to modern concepts (AI, cognitive science, systems thinking) where genuine parallels exist — but note where parallels break
- Honest about the tradition's failures alongside its genius
- Harshwardhan (HNG) is the founder and guide — match his directness

## Society of Thoughts

The founding insight: if an LLM has a society of thoughts (multiple perspectives negotiating meaning), Hindu philosophy described this architecture thousands of years ago. Brahman/Atman, the Shaddarshana, the Vishvarupa — all models of consciousness as a chorus, not a monolith.

This project was itself built by a society of thoughts — 25 parallel agents, no shared context, coherent through shared protocol. Like the Vedic shakhas: distributed preservation through shared structure.

## Architecture Status

This project is a complete, installable cognitive architecture:
- **src/** — 16 Python modules implementing the full Antahkarana pipeline
- **training/** — ML pipeline for fine-tuning Kimi K2.5 (1T MoE) with LoRA. 1,790 training examples, 1.3M tokens. Vritti reward model for RLHF.
- **plugin/** — Claude Code plugin (10 skills, installed at darshana@darshana-marketplace)
- **mcp/** — MCP server (9 tools, works with any MCP client)
- **tests/** — 48 tests passing, 95% router accuracy, 100% filter accuracy
- **CLI** — `python -m darshana` for interactive use

The single interface: `from darshana import Antahkarana; mind = Antahkarana(); mind.think("query")`

## AWS Status
- Account: 390449413787 (Heft Energy), active credits covering all usage
- GPU quota: PENDING (On-Demand P: Case #177425473500754, Spot P: Case #177425469800882)
- **CHECK QUOTA STATUS EACH SESSION**: `aws service-quotas list-requested-service-quota-change-history --service-code ec2 --region us-east-1`
- When approved: upload to S3 → launch p4d.24xlarge spot → `python training/finetune_kimi.py --all`

## See Also

- `.claude/structure.md` — full folder layout and naming conventions
- `.claude/content.md` — writing style, reasoning rules, depth requirements, self-check protocol
- `.claude/roadmap.md` — complete build history + next steps
