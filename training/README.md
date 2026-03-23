# Darshana Fine-Tuning Pipeline

Fine-tune open-source LLMs into specialized reasoning engines using LoRA adapters, one per darshana school. This is the bridge from philosophy to neural networks.

## What Gets Built

| Adapter | Purpose | Training Data |
|---|---|---|
| `nyaya/` | Formal logic, syllogisms, fallacy detection | `nyaya_train.jsonl` |
| `samkhya/` | Exhaustive enumeration, causal chain mapping | `samkhya_train.jsonl` |
| `yoga/` | Attention filtering, signal/noise optimization | `yoga_train.jsonl` |
| `vedanta/` | Contradiction resolution, unifying abstractions | `vedanta_train.jsonl` |
| `mimamsa/` | Text-to-action extraction, command parsing | `mimamsa_train.jsonl` |
| `vaisheshika/` | Atomic decomposition, type systems | `vaisheshika_train.jsonl` |
| `router/` | Buddhi layer: routes queries to the right engine | `router_train.jsonl` |
| `vritti_reward/` | Classifies output quality on the 5 vritti types | `vritti_train.jsonl` |

## Hardware Requirements

| Base Model | VRAM (4-bit) | VRAM (Training) | Recommended GPU |
|---|---|---|---|
| Llama 3.2 3B | ~4 GB | ~6 GB | RTX 3060 12GB, T4 |
| Mistral 7B / Qwen 2.5 7B | ~6 GB | ~10 GB | RTX 3090 24GB, A10 |
| Llama 3.2 8B | ~7 GB | ~12 GB | RTX 4090 24GB, A10G |
| 13B models | ~10 GB | ~18 GB | A100 40GB |

Apple Silicon Macs (M1/M2/M3) work but are slower. bitsandbytes 4-bit quantization requires CUDA; MPS falls back to fp16.

## Quick Start

### 1. Install dependencies

```bash
pip install -r training/requirements.txt
```

### 2. Generate training data

```bash
# Generate all datasets (180 darshana + 100 router + 50 vritti examples)
python training/generate_data.py

# Validate generated JSONL
python training/generate_data.py --validate

# Print statistics (counts, token estimates, domain coverage)
python training/generate_data.py --stats
```

This generates chat-format JSONL files in `training/data/`:

```json
{"messages": [
    {"role": "system", "content": "<darshana system prompt>"},
    {"role": "user", "content": "<query>"},
    {"role": "assistant", "content": "<structured reasoning output>"}
]}
```

Example content lives in `training/examples/` with one module per darshana. Each example follows the darshana's exact method structure with 300-800 word responses covering 10 domains (software engineering, business strategy, scientific analysis, personal decisions, debugging, ethics, project planning, legal, creative, education).

### 3. Fine-tune

```bash
# Single darshana
python training/finetune.py --darshana nyaya --base-model meta-llama/Llama-3.2-3B-Instruct

# All six
python training/finetune.py --all --base-model meta-llama/Llama-3.2-3B-Instruct

# Router (Buddhi layer)
python training/finetune.py --router --base-model meta-llama/Llama-3.2-3B-Instruct

# Vritti classifier
python training/finetune.py --vritti --base-model meta-llama/Llama-3.2-3B-Instruct

# Custom hyperparameters
python training/finetune.py --darshana nyaya --epochs 5 --lr 1e-4 --lora-rank 32

# Resume from checkpoint
python training/finetune.py --darshana nyaya --resume training/adapters/nyaya/checkpoint-400
```

### 4. Evaluate

```bash
# Single adapter
python training/evaluate.py --adapter training/adapters/nyaya/ \
    --test-data training/data/nyaya_test.jsonl

# Side-by-side comparison (base vs fine-tuned)
python training/evaluate.py --adapter training/adapters/nyaya/ \
    --test-data training/data/nyaya_test.jsonl --compare

# All adapters
python training/evaluate.py --all
```

### 5. Train the vritti reward model

```bash
python training/reward_model.py --train --data training/data/vritti_train.jsonl
```

### 6. Serve

```bash
# Single darshana
python training/serve.py --darshana nyaya --port 8000

# All darshanas with auto-routing
python training/serve.py --all --port 8000
```

## API Endpoints

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/think` | POST | `{"query": "...", "darshana": "nyaya"}` | Reasoning response with vritti classification |
| `/route` | POST | `{"query": "..."}` | Routing decision (which darshana) |
| `/classify` | POST | `{"text": "..."}` | Vritti classification + depth/novelty scores |
| `/health` | GET | — | Server status |

The `darshana` field in `/think` is optional. If omitted, the Buddhi router selects the best engine automatically.

## Choosing a Base Model

**Llama 3.2 3B-Instruct** is the recommended starting point:
- Fits on consumer GPUs (6 GB VRAM for training)
- Fast iteration (8 min/epoch for 1k examples)
- Good instruction following out of the box
- The darshana prompts are heavily structured, so even 3B can learn the patterns

**Scale up to 7B/8B** when:
- You have 24+ GB VRAM
- You need better reasoning depth (especially for Nyaya and Vedanta)
- Training data exceeds 5k examples per darshana

**Mistral 7B vs Qwen 2.5 7B**: Mistral is slightly better at logical reasoning (good for Nyaya); Qwen handles multilingual content better if your training data includes Sanskrit terms.

## Expected Training Times (A100 40GB)

| Model | Examples | Epochs | Time |
|---|---|---|---|
| 3B | 500 | 3 | ~12 min |
| 3B | 2,000 | 3 | ~48 min |
| 7B | 500 | 3 | ~27 min |
| 7B | 2,000 | 3 | ~108 min |

## Cost Estimates (Cloud GPU)

| Provider | GPU | Cost/hr | 3B x 3 epochs (2k) | 7B x 3 epochs (2k) |
|---|---|---|---|---|
| Lambda | A100 40GB | ~$1.10/hr | ~$0.90 | ~$2.00 |
| RunPod | A100 40GB | ~$1.20/hr | ~$1.00 | ~$2.20 |
| HF Spaces | A10G | ~$1.00/hr | ~$1.00 | ~$2.50 |
| Vast.ai | RTX 4090 | ~$0.40/hr | ~$0.50 | ~$1.00 |

Training all 6 darshanas + router + vritti on 2k examples each at 3B: roughly $8-12 total.

## Using Adapters with the Main Architecture

The adapters integrate with the existing `src/` codebase. The serve.py server loads them onto a base model and exposes the same routing/filtering pipeline:

1. Query arrives
2. **Buddhi** (DarshanaRouter or router adapter) selects the engine
3. **LoRA adapter** activates for the selected darshana
4. Model generates with the darshana's system prompt
5. **Vritti filter** (or vritti reward model) classifies the output
6. Response returned with classification metadata

For programmatic use without the server:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base + adapter
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
model = PeftModel.from_pretrained(model, "training/adapters/nyaya/")

# Generate with the Nyaya system prompt
from src.prompts import DARSHANA_PROMPTS
system_prompt = DARSHANA_PROMPTS["nyaya"]
```

## Configuration

All defaults live in `training/config.yaml`. Override via CLI flags or edit the YAML directly.

Key settings:
- `lora.rank`: Higher = more capacity, more VRAM. 16 is a good default; 32 for complex darshanas.
- `lora.alpha`: Usually 2x the rank. Controls the learning rate scaling of LoRA.
- `training.max_length`: 2048 is sufficient for most darshana outputs. Increase for Samkhya (long enumerations).
- `training.gradient_accumulation_steps`: Increase if you need to reduce batch_size for VRAM.

## The Vritti Reward Model

This is the novel piece. Instead of human preference labels, the reward model scores outputs on an epistemological scale:

| Vritti | Reward | Meaning |
|---|---|---|
| Pramana | +1.0 | Valid cognition grounded in evidence |
| Smriti | +0.2 | Correct recall, but not fresh reasoning |
| Nidra | 0.0 | Honest "I don't know" — not penalized |
| Vikalpa | -0.8 | Sounds right but means nothing |
| Viparyaya | -1.0 | Factual error or logical fallacy |

The key insight: **nidra (absence) gets zero reward, not negative**. A system that admits ignorance is epistemically healthier than one that generates confident nonsense. This is Patanjali's contribution to RLHF.

---

## Kimi K2.5 — The MoE Darshana Model

### Why Kimi K2.5

Kimi K2.5 is the natural base model for the Darshana Architecture because its MoE (Mixture of Experts) design mirrors the Shaddarshana at the neural level:

| Darshana Architecture | Kimi K2.5 MoE | The Parallel |
|---|---|---|
| 6 darshana engines | 384 experts per layer | Different problems activate different reasoning methods |
| Buddhi router selects engine | Top-8 routing selects experts | A routing decision precedes every computation |
| Shared reasoning substrate | Shared expert (always active) | Some capabilities are universal across methods |
| LoRA adapter = specialization | Expert = specialization | Small, composable modules that don't touch the base |
| 61-layer deep processing | 61 transformer layers | Deep iterative refinement of thought |

The result is two-level routing:
1. **Buddhi** (our DarshanaRouter) selects which darshana's LoRA adapter to activate
2. **MoE routing** (Kimi's built-in) selects which of 384 experts to activate per token

Together, this creates a deeply specialized reasoning pipeline where both the high-level method (darshana) and the low-level computation (expert routing) are tailored to the problem.

### Kimi K2.5 Architecture

| Spec | Value |
|---|---|
| Total parameters | 1 Trillion |
| Active parameters | 32 Billion (per forward pass) |
| Architecture | MoE (Mixture of Experts) |
| Layers | 61 (1 dense + 60 MoE) |
| Experts per MoE layer | 384 |
| Active experts per token | 8 (top-8 routing + shared expert) |
| Attention hidden dim | 7168 |
| MoE hidden dim per expert | 2048 |
| Context window | 256K tokens |
| Weight format (shipped) | RAWINT4 |
| Training dtype | BF16 (after conversion) |

### Hardware Requirements for Kimi K2.5

| Setup | GPU | RAM | Disk | Throughput | Time per Adapter |
|---|---|---|---|---|---|
| Local (recommended) | 2x RTX 4090 (48 GB) | 128 GB min, 512 GB+ recommended | 800 GB | ~44.55 tok/s | 2-4 hours |
| Cloud A100 | 1-2x A100 80GB | 256 GB+ | 1 TB | ~80 tok/s | 1-2 hours |
| Cloud H100 | 1x H100 80GB | 512 GB+ | 1 TB | ~150 tok/s | 30-60 min |

KTransformers makes this possible by offloading MoE expert layers to CPU/RAM (INT4) while keeping attention layers (the LoRA targets) on GPU (BF16). You fine-tune a 1T model on consumer hardware.

### Step-by-Step Setup

```bash
# 1. Run the automated setup (checks hardware, installs deps, downloads model)
bash training/setup_kimi.sh

# 2. Or manual setup:
pip install -r training/requirements.txt
pip install ktransformers llamafactory

# 3. Download model weights (~700 GB)
python -c "from huggingface_hub import snapshot_download; snapshot_download('moonshotai/Kimi-K2.5-Instruct')"
```

### Training Commands

```bash
# Fine-tune a single darshana on Kimi K2.5
python training/finetune_kimi.py --darshana nyaya

# Fine-tune all 6 darshanas
python training/finetune_kimi.py --all

# Fine-tune the Buddhi router
python training/finetune_kimi.py --router

# Fine-tune the vritti classifier
python training/finetune_kimi.py --vritti

# Dry run — generate LlamaFactory configs without training
python training/finetune_kimi.py --darshana nyaya --dry-run

# Custom hyperparameters
python training/finetune_kimi.py --darshana nyaya --epochs 5 --lr 1e-4 --lora-rank 32

# Cloud training (generates launch scripts)
python training/finetune_kimi.py --all --cloud runpod
python training/finetune_kimi.py --all --cloud lambda
```

Under the hood, `finetune_kimi.py`:
1. Converts training JSONL to LlamaFactory's ShareGPT format
2. Generates a LlamaFactory YAML config with KTransformers enabled
3. Checks BF16 conversion status
4. Runs `USE_KT=1 llamafactory-cli train <config.yaml>`
5. Saves adapters to `training/adapters/kimi-k2.5/<darshana>/`

### Serving Kimi K2.5

```bash
# Serve all darshanas with auto-routing
python training/serve_kimi.py --all --port 8000

# Serve a single darshana
python training/serve_kimi.py --darshana nyaya --port 8000
```

The serving script uses KTransformers for efficient MoE inference and supports hot-swapping LoRA adapters based on which darshana the Buddhi router selects. Same API as `serve.py`:

| Endpoint | Method | Description |
|---|---|---|
| `/think` | POST | Reasoning with auto-routing + vritti classification |
| `/route` | POST | Routing decision only (Buddhi layer) |
| `/classify` | POST | Vritti classification + depth/novelty |
| `/health` | GET | Status, memory usage, loaded adapters |

### Cloud Training Options with Cost Estimates

For all 8 adapters (6 darshanas + router + vritti) with ~500 examples each, 3 epochs:

| Provider | GPU | Cost/hr | Hours (est.) | Total Cost |
|---|---|---|---|---|
| RunPod | 2x RTX 4090 | ~$0.74/hr | ~24 hrs | ~$18 |
| Lambda | 1x A100 80GB | ~$1.10/hr | ~16 hrs | ~$18 |
| Vast.ai | 2x RTX 4090 | ~$0.50/hr | ~24 hrs | ~$12 |
| Lambda | 1x H100 80GB | ~$2.49/hr | ~6 hrs | ~$15 |

To use cloud training:
```bash
# Generate cloud-ready scripts and configs
python training/finetune_kimi.py --all --cloud runpod

# Upload the training/ directory to your cloud instance
# Run the generated scripts in training/adapters/kimi-k2.5/cloud_scripts/
```

### Configuration

Kimi K2.5 config lives in `training/config_kimi.yaml`. Key settings:

```yaml
base_model: moonshotai/Kimi-K2.5-Instruct
use_ktransformers: true

lora:
  rank: 16           # LoRA rank (16 is the sweet spot for MoE)
  alpha: 32          # 2x rank
  dropout: 0.1       # Higher than standard (MoE benefits from regularization)
  target_modules:    # Attention layers only (stay on GPU)
    - q_proj
    - k_proj
    - v_proj
    - o_proj

training:
  batch_size: 1                     # Small batch (model is huge)
  gradient_accumulation_steps: 16   # Effective batch = 16
  learning_rate: 2.0e-5             # Conservative for large MoE
  bf16: true                        # Required for KTransformers
```

### How the MoE Architecture Mirrors the Shaddarshana

The deep structural parallel:

**Layer 1 — Routing (Buddhi = MoE Router)**
Just as Buddhi examines a query and selects the appropriate darshana, the MoE router examines each token and selects 8 of 384 experts. Both are learned routing functions that match input patterns to specialized processors.

**Layer 2 — Specialization (Darshana = Expert)**
Each darshana is a distinct reasoning methodology. Each MoE expert is a distinct computational pathway. Neither modifies the base substrate — they compose on top of it. Our LoRA adapters teach the attention layers to better activate the right expert combinations for each darshana's method.

**Layer 3 — The Shared Expert (Purusha = Universal Observer)**
Kimi K2.5 has a shared expert that activates on every token regardless of routing. This is the universal reasoning substrate — the Purusha that witnesses all computation. It provides the common sense and language understanding that every darshana builds upon.

**Layer 4 — Composition (Samyoga)**
In Vaisheshika, samyoga is the contact between independent substances that creates new properties. In the MoE, the outputs of 8 experts are combined to produce something none of them could alone. The whole is greater than the sum — this is emergent reasoning.

**The Training Insight:**
We do not fine-tune the experts (they stay frozen on CPU). We fine-tune the attention layers — the part that decides *what to attend to*. This is exactly the Yoga darshana's contribution: the quality of cognition depends not on having more information, but on directing attention correctly. LoRA on attention = training the model's dharana (concentration).
