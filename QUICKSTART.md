# Darshana Architecture — Quick Start

Get from zero to running in under 2 minutes.

---

## Install (3 commands)

```bash
git clone https://github.com/aidgoc/om.git
cd om
pip install -e .
```

That's it. All local features (routing, filtering, classification) work immediately.

For LLM features, set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Your First Query

Route a question through the six darshana reasoning engines:

```bash
darshana "Is this argument valid: All birds can fly. Penguins are birds. Therefore penguins can fly."
```

The Buddhi layer classifies the query, selects the right engine (Nyaya for logic), sets the processing mode (Sattva for precision), and returns structured reasoning — all without any API calls.

Try multi-engine mode for complex questions:

```bash
darshana --multi "Should our startup pivot from B2B to B2C?"
```

This activates up to 3 complementary engines (e.g., Samkhya for decomposition, Nyaya for logical evaluation, Vedanta for synthesis).

---

## Teaching the System

With LLM mode, the system uses real Anthropic API calls with darshana-specific system prompts:

```bash
darshana --llm "What is the relationship between entropy and information?"
```

The response includes metadata: which engine reasoned, which pramana (epistemic source) applies, the vritti (output quality) classification, and exact token/cost information.

As a Python library:

```python
from darshana import Antahkarana

mind = Antahkarana(api_key="sk-ant-...")
response = mind.think("Explain monads in terms a Python developer would understand")

print(response.text)
print(f"Engine: {response.darshana}")
print(f"Quality: {response.vritti}")
print(f"Cost: ${response.cost:.4f}")
```

---

## Checking Your Budget

The Shakti module tracks every API call and enforces daily/monthly limits:

```python
from src.shakti import ShaktiManager

shakti = ShaktiManager(budget_daily=10.0)
summary = shakti.today_summary()
print(f"Spent today: ${summary['total_cost']:.2f}")
print(f"Remaining: ${shakti.remaining_budget():.2f}")
```

Set budget limits in `~/.darshana/config.json`:

```json
{
    "shakti": {
        "budget_daily_usd": 10.0,
        "budget_monthly_usd": 100.0
    }
}
```

---

## Next Steps

| Want to... | Do this |
|---|---|
| Run all demos | `darshana --demo` or `make demo` |
| Run tests | `make test` |
| See the architecture | Read [THESIS.md](THESIS.md) |
| Understand the pipeline | Read `src/antahkarana.py` |
| Add a new reasoning engine | Subclass in `src/darshana_router.py` |
| Customize system prompts | Edit `src/prompts.py` |
| Check cost history | Query `~/.darshana/db/shakti_ledger.db` |
| Browse past memories | Query `~/.darshana/db/smriti.db` |
| Full setup with venv + DBs | `bash setup.sh` |
| Read the full README | [README.md](README.md) |

---

> anubhuta-vishayasampramoshah smritih
> "Memory is the non-stealing of an experienced object."
> — Yoga Sutra 1.11
