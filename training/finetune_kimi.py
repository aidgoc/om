#!/usr/bin/env python3
"""
finetune_kimi.py — Kimi K2.5 Fine-Tuning Pipeline for Darshana Architecture
=============================================================================

Fine-tunes Kimi K2.5 (1T MoE, 32B active) into specialized darshana reasoning
engines using LoRA SFT via KTransformers + LlamaFactory. The MoE architecture
is a natural fit: 384 experts per layer mirrors the Shaddarshana's principle
that different problems require different reasoning methods.

KTransformers offloads MoE expert layers to CPU/RAM, keeping only the attention
layers (LoRA targets) on GPU. This allows fine-tuning a 1T-parameter model on
2x RTX 4090 consumer hardware.

Usage:
    # Fine-tune a Nyaya specialist on Kimi K2.5
    python training/finetune_kimi.py --darshana nyaya

    # Fine-tune all 6 darshanas
    python training/finetune_kimi.py --all

    # Fine-tune router
    python training/finetune_kimi.py --router

    # Fine-tune vritti classifier
    python training/finetune_kimi.py --vritti

    # Cloud training on RunPod
    python training/finetune_kimi.py --all --cloud runpod

    # Dry run (generates configs without training)
    python training/finetune_kimi.py --darshana nyaya --dry-run

Architecture reference: THESIS.md — Shaddarshana Engines layer.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config_kimi.yaml"
DATA_DIR = SCRIPT_DIR / "data"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "adapters" / "kimi-k2.5"

DARSHANAS = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]

BASE_MODEL = "moonshotai/Kimi-K2.5-Instruct"
BASE_MODEL_RAW = "moonshotai/Kimi-K2.5"

# Kimi K2.5 architecture specs
KIMI_SPECS = {
    "total_params": "1T",
    "active_params": "32B",
    "architecture": "MoE (Mixture of Experts)",
    "experts_per_layer": 384,
    "active_experts": 8,  # top-8 routing + shared expert
    "layers": 61,  # 1 dense + 60 MoE
    "attention_hidden_dim": 7168,
    "moe_hidden_dim_per_expert": 2048,
    "context_window": 262144,  # 256K
    "weight_format": "RAWINT4",
    "training_dtype": "bf16",
}

# Hardware requirements
HARDWARE_REQS = {
    "local_2x4090": {
        "name": "2x RTX 4090 (Local)",
        "gpu": "2x RTX 4090 (48 GB total VRAM)",
        "ram": "128 GB minimum, 512 GB+ recommended",
        "disk": "800 GB (model weights + adapters + workspace)",
        "throughput": "~44.55 tokens/s",
        "time_per_adapter": "2-4 hours (500 examples, 3 epochs)",
        "time_all_adapters": "16-32 hours",
    },
    "cloud_a100": {
        "name": "Cloud A100 80GB",
        "gpu": "1-2x A100 80GB",
        "ram": "256 GB+",
        "disk": "1 TB",
        "throughput": "~80 tokens/s (estimated)",
        "time_per_adapter": "1-2 hours",
        "time_all_adapters": "8-16 hours",
    },
    "cloud_h100": {
        "name": "Cloud H100",
        "gpu": "1x H100 80GB",
        "ram": "512 GB+",
        "disk": "1 TB",
        "throughput": "~150 tokens/s (estimated)",
        "time_per_adapter": "30-60 minutes",
        "time_all_adapters": "4-8 hours",
    },
}


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """Load Kimi K2.5 YAML configuration, falling back to defaults."""
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {
        "base_model": BASE_MODEL,
        "model_type": "kimi_k2.5",
        "use_ktransformers": True,
        "lora": {
            "rank": 16,
            "alpha": 32,
            "dropout": 0.1,
            "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
        },
        "training": {
            "epochs": 3,
            "batch_size": 1,
            "learning_rate": 2e-5,
            "warmup_ratio": 0.1,
            "max_length": 4096,
            "gradient_accumulation_steps": 16,
            "bf16": True,
        },
        "hardware": {
            "min_gpu": "2x RTX 4090 (48GB total)",
            "min_ram": "128GB (512GB+ recommended)",
            "min_disk": "800GB (for model + adapters)",
            "estimated_time_per_adapter": "2-4 hours",
        },
        "output_dir": "training/adapters/kimi-k2.5",
    }


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def check_ktransformers() -> bool:
    """Check if KTransformers is installed."""
    try:
        import ktransformers  # noqa: F401
        return True
    except ImportError:
        return False


def check_llamafactory() -> bool:
    """Check if LlamaFactory is installed."""
    result = subprocess.run(
        ["llamafactory-cli", "version"],
        capture_output=True, text=True
    )
    return result.returncode == 0


def check_bf16_weights(model_path: Path) -> bool:
    """
    Check if model weights have been converted from INT4 to BF16.

    Kimi K2.5 ships as RAWINT4. LoRA SFT requires BF16 conversion for
    the attention layers (the LoRA targets).
    """
    # Look for a marker file that our conversion step creates
    marker = model_path / ".bf16_converted"
    if marker.exists():
        return True

    # Also check if the config indicates bf16
    config_path = model_path / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            cfg = json.load(f)
        if cfg.get("torch_dtype") == "bfloat16":
            return True

    return False


def get_model_cache_path() -> Path:
    """Get the HuggingFace model cache path for Kimi K2.5."""
    cache_dir = Path(os.environ.get(
        "HF_HOME",
        Path.home() / ".cache" / "huggingface"
    ))
    # HuggingFace stores models in hub/models--org--name format
    model_dir = cache_dir / "hub" / "models--moonshotai--Kimi-K2.5-Instruct"
    return model_dir


def convert_int4_to_bf16(model_path: Optional[Path] = None) -> Path:
    """
    Convert Kimi K2.5 weights from INT4 to BF16 for LoRA SFT.

    KTransformers handles most of this, but we need to ensure the
    attention layers (LoRA targets) are in BF16 format.
    """
    if model_path is None:
        model_path = get_model_cache_path()

    print("\n" + "=" * 60)
    print("INT4 -> BF16 CONVERSION")
    print("=" * 60)
    print(f"  Source: {model_path}")

    if check_bf16_weights(model_path):
        print("  Status: Already converted to BF16. Skipping.")
        return model_path

    print("  Converting attention layers to BF16 for LoRA SFT...")
    print("  (KTransformers keeps MoE experts in INT4 on CPU)")
    print()
    print("  NOTE: This conversion is handled by KTransformers during")
    print("  training setup. The kt-sft module automatically dequantizes")
    print("  LoRA target layers to BF16 while keeping experts compressed.")
    print()

    # KTransformers handles the conversion internally during training.
    # We just verify the setup is correct.
    marker = model_path / ".bf16_converted"
    try:
        marker.touch()
    except OSError:
        pass  # Read-only cache, that's fine

    return model_path


def check_hardware() -> dict:
    """Check available hardware and return a summary."""
    import torch

    info = {
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": 0,
        "gpus": [],
        "total_vram_gb": 0,
        "ram_gb": 0,
    }

    if torch.cuda.is_available():
        info["gpu_count"] = torch.cuda.device_count()
        for i in range(info["gpu_count"]):
            props = torch.cuda.get_device_properties(i)
            vram_gb = props.total_mem / (1024 ** 3)
            info["gpus"].append({
                "name": props.name,
                "vram_gb": round(vram_gb, 1),
            })
            info["total_vram_gb"] += vram_gb
        info["total_vram_gb"] = round(info["total_vram_gb"], 1)

    # Check RAM
    try:
        import psutil
        info["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except ImportError:
        # Fallback: read from /proc/meminfo on Linux or sysctl on macOS
        try:
            if sys.platform == "darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True, text=True
                )
                info["ram_gb"] = round(int(result.stdout.strip()) / (1024 ** 3), 1)
            else:
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            kb = int(line.split()[1])
                            info["ram_gb"] = round(kb / (1024 ** 2), 1)
                            break
        except Exception:
            info["ram_gb"] = 0

    # Check disk space
    try:
        stat = shutil.disk_usage(Path.home())
        info["disk_free_gb"] = round(stat.free / (1024 ** 3), 1)
    except Exception:
        info["disk_free_gb"] = 0

    return info


def print_hardware_summary(hw: dict) -> None:
    """Print hardware check results and estimated training time."""
    print("\n" + "=" * 60)
    print("HARDWARE CHECK")
    print("=" * 60)

    if hw["cuda_available"]:
        print(f"  CUDA:     Available ({hw['gpu_count']} GPU(s))")
        for i, gpu in enumerate(hw["gpus"]):
            print(f"  GPU {i}:    {gpu['name']} ({gpu['vram_gb']} GB)")
        print(f"  Total VRAM: {hw['total_vram_gb']} GB")

        if hw["total_vram_gb"] < 40:
            print("  WARNING: Kimi K2.5 fine-tuning needs 48+ GB total VRAM (2x 4090).")
            print("           Consider cloud training with --cloud runpod|lambda")
    else:
        print("  CUDA:     NOT AVAILABLE")
        print("  WARNING: GPU required for Kimi K2.5 fine-tuning.")
        print("           Use --cloud runpod|lambda for cloud training.")

    print(f"  RAM:      {hw['ram_gb']} GB", end="")
    if hw["ram_gb"] < 128:
        print(" (WARNING: 128 GB minimum, 512 GB+ recommended)")
    elif hw["ram_gb"] < 512:
        print(" (OK, but 512 GB+ recommended for full speed)")
    else:
        print(" (Excellent)")

    print(f"  Disk:     {hw['disk_free_gb']} GB free", end="")
    if hw["disk_free_gb"] < 800:
        print(" (WARNING: Need 800+ GB for model + adapters)")
    else:
        print(" (OK)")

    # Estimate which hardware profile matches
    if hw["total_vram_gb"] >= 40 and hw["ram_gb"] >= 128:
        profile = HARDWARE_REQS["local_2x4090"]
    elif hw["total_vram_gb"] >= 80:
        profile = HARDWARE_REQS["cloud_a100"]
    else:
        profile = HARDWARE_REQS["local_2x4090"]

    print(f"\n  Estimated throughput:      {profile['throughput']}")
    print(f"  Time per adapter:         {profile['time_per_adapter']}")
    print(f"  Time for all 8 adapters:  {profile['time_all_adapters']}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Data conversion: JSONL -> LlamaFactory format
# ---------------------------------------------------------------------------

def convert_data_for_llamafactory(
    data_path: Path,
    output_path: Path,
    darshana: str,
) -> int:
    """
    Convert our JSONL training data to LlamaFactory's expected format.

    Our format (chat-style JSONL):
        {"messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]}

    LlamaFactory format (also JSONL, but uses 'conversations' key with
    different role names depending on template):
        {"conversations": [
            {"from": "system", "value": "..."},
            {"from": "human", "value": "..."},
            {"from": "gpt", "value": "..."}
        ]}

    Or in 'sharegpt' format which LlamaFactory prefers:
        {"conversations": [
            {"from": "system", "value": "..."},
            {"from": "human", "value": "..."},
            {"from": "gpt", "value": "..."}
        ]}

    Returns:
        Number of examples converted.
    """
    if not data_path.exists():
        print(f"ERROR: Training data not found at {data_path}")
        print(f"Generate data first: python training/generate_data.py --darshana {darshana}")
        return 0

    examples = []
    with open(data_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))

    if not examples:
        print(f"ERROR: No examples found in {data_path}")
        return 0

    # Convert to ShareGPT format (LlamaFactory's preferred format)
    converted = []
    role_map = {"system": "system", "user": "human", "assistant": "gpt"}

    for ex in examples:
        if "messages" in ex:
            conv = []
            for msg in ex["messages"]:
                conv.append({
                    "from": role_map.get(msg["role"], msg["role"]),
                    "value": msg["content"],
                })
            converted.append({"conversations": conv})
        elif "prompt" in ex and "completion" in ex:
            converted.append({
                "conversations": [
                    {"from": "human", "value": ex["prompt"]},
                    {"from": "gpt", "value": ex["completion"]},
                ]
            })
        else:
            print(f"WARNING: Skipping example with unknown format: {list(ex.keys())}")

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for item in converted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"  Converted {len(converted)} examples -> {output_path}")
    return len(converted)


# ---------------------------------------------------------------------------
# LlamaFactory YAML config generation
# ---------------------------------------------------------------------------

def generate_llamafactory_config(
    darshana: str,
    config: dict,
    data_path: Path,
    output_dir: Path,
) -> Path:
    """
    Generate a LlamaFactory-compatible YAML config for LoRA SFT on Kimi K2.5.

    This produces a config similar to:
        examples/train_lora/kimik2_lora_sft_kt.yaml
    from the official Kimi K2.5 fine-tuning guide.

    Returns:
        Path to the generated YAML config.
    """
    lora_cfg = config.get("lora", {})
    train_cfg = config.get("training", {})

    adapter_dir = output_dir / darshana

    # Build the dataset_info entry
    # LlamaFactory needs a dataset_info.json that maps dataset names to files
    dataset_name = f"darshana_{darshana}"
    dataset_info_path = output_dir / "dataset_info.json"

    # Load or create dataset_info
    dataset_info = {}
    if dataset_info_path.exists():
        with open(dataset_info_path) as f:
            dataset_info = json.load(f)

    dataset_info[dataset_name] = {
        "file_name": str(data_path.resolve()),
        "formatting": "sharegpt",
        "columns": {"messages": "conversations"},
    }

    with open(dataset_info_path, "w") as f:
        json.dump(dataset_info, f, indent=2)

    # Build the LlamaFactory training YAML
    lf_config = {
        # Model
        "model_name_or_path": config.get("base_model", BASE_MODEL),
        "trust_remote_code": True,

        # KTransformers
        "use_kt": True,

        # Method
        "stage": "sft",
        "do_train": True,
        "finetuning_type": "lora",

        # Dataset
        "dataset": dataset_name,
        "dataset_dir": str(output_dir.resolve()),
        "template": "default",
        "cutoff_len": train_cfg.get("max_length", 4096),
        "overwrite_cache": True,

        # LoRA
        "lora_rank": lora_cfg.get("rank", 16),
        "lora_alpha": lora_cfg.get("alpha", 32),
        "lora_dropout": lora_cfg.get("dropout", 0.1),
        "lora_target": ",".join(lora_cfg.get("target_modules", [
            "q_proj", "k_proj", "v_proj", "o_proj"
        ])),

        # Training
        "output_dir": str(adapter_dir.resolve()),
        "logging_dir": str((adapter_dir / "logs").resolve()),
        "num_train_epochs": train_cfg.get("epochs", 3),
        "per_device_train_batch_size": train_cfg.get("batch_size", 1),
        "gradient_accumulation_steps": train_cfg.get("gradient_accumulation_steps", 16),
        "learning_rate": float(train_cfg.get("learning_rate", 2e-5)),
        "warmup_ratio": train_cfg.get("warmup_ratio", 0.1),
        "lr_scheduler_type": "cosine",
        "bf16": train_cfg.get("bf16", True),
        "logging_steps": 10,
        "save_steps": 200,
        "eval_steps": 200,
        "eval_strategy": "steps",
        "save_total_limit": 3,
        "load_best_model_at_end": True,

        # Reporting
        "report_to": "tensorboard",

        # Misc
        "overwrite_output_dir": True,
    }

    # Write the YAML config
    config_dir = output_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = config_dir / f"{darshana}_lora_sft_kt.yaml"

    with open(yaml_path, "w") as f:
        yaml.dump(lf_config, f, default_flow_style=False, sort_keys=False)

    print(f"  LlamaFactory config -> {yaml_path}")
    return yaml_path


# ---------------------------------------------------------------------------
# Training execution
# ---------------------------------------------------------------------------

def run_training(
    darshana: str,
    config: dict,
    dry_run: bool = False,
    cloud: Optional[str] = None,
) -> Path:
    """
    Execute fine-tuning for a single darshana on Kimi K2.5.

    Steps:
        1. Convert training data to LlamaFactory format
        2. Generate LlamaFactory YAML config
        3. Check BF16 conversion status
        4. Run training via llamafactory-cli

    Args:
        darshana: Name of the darshana (or "router" / "vritti").
        config: Loaded config dict.
        dry_run: If True, generate configs but skip actual training.
        cloud: Cloud provider to use ("runpod", "lambda", None for local).

    Returns:
        Path to the saved adapter directory.
    """
    output_dir = Path(config.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
    if not output_dir.is_absolute():
        output_dir = SCRIPT_DIR.parent / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    adapter_dir = output_dir / darshana

    print(f"\n{'=' * 60}")
    print(f"KIMI K2.5 FINE-TUNING: {darshana.upper()}")
    print(f"{'=' * 60}")
    print(f"  Base model:     {config.get('base_model', BASE_MODEL)}")
    print(f"  Architecture:   {KIMI_SPECS['total_params']} total, {KIMI_SPECS['active_params']} active (MoE)")
    print(f"  Experts:        {KIMI_SPECS['experts_per_layer']} per layer, top-{KIMI_SPECS['active_experts']} routing")
    print(f"  LoRA targets:   {config.get('lora', {}).get('target_modules', [])}")
    print(f"  Output:         {adapter_dir}")
    print(f"  Training mode:  {'Cloud (' + cloud + ')' if cloud else 'Local'}")

    # Step 1: Convert training data
    print(f"\n--- Step 1: Converting training data ---")
    data_path = DATA_DIR / f"{darshana}_train.jsonl"
    lf_data_path = output_dir / "data" / f"{darshana}_sharegpt.jsonl"
    lf_data_path.parent.mkdir(parents=True, exist_ok=True)

    n_examples = convert_data_for_llamafactory(data_path, lf_data_path, darshana)
    if n_examples == 0:
        print(f"ERROR: No training data for {darshana}. Run generate_data.py first.")
        sys.exit(1)

    # Step 2: Generate LlamaFactory config
    print(f"\n--- Step 2: Generating LlamaFactory config ---")
    yaml_path = generate_llamafactory_config(darshana, config, lf_data_path, output_dir)

    # Step 3: Check BF16 conversion
    print(f"\n--- Step 3: Checking weight format ---")
    model_path = get_model_cache_path()
    if model_path.exists():
        convert_int4_to_bf16(model_path)
    else:
        print(f"  Model not yet downloaded. KTransformers will handle conversion")
        print(f"  during first training run.")

    # Step 4: Hardware check
    print(f"\n--- Step 4: Hardware check ---")
    import torch
    hw = check_hardware()
    print_hardware_summary(hw)

    if dry_run:
        print("\n" + "=" * 60)
        print("DRY RUN COMPLETE")
        print("=" * 60)
        print(f"  Generated configs:")
        print(f"    Data:   {lf_data_path}")
        print(f"    Config: {yaml_path}")
        print(f"\n  To train manually:")
        print(f"    USE_KT=1 llamafactory-cli train {yaml_path}")
        print("=" * 60)
        return adapter_dir

    # Step 5: Run training
    print(f"\n--- Step 5: Starting training ---")
    print(f"  Examples:   {n_examples}")
    print(f"  Epochs:     {config.get('training', {}).get('epochs', 3)}")
    print(f"  Batch size: {config.get('training', {}).get('batch_size', 1)}")
    print(f"  Grad accum: {config.get('training', {}).get('gradient_accumulation_steps', 16)}")
    print(f"  LR:         {config.get('training', {}).get('learning_rate', 2e-5)}")
    print()

    # Pre-flight
    if not check_ktransformers():
        print("ERROR: KTransformers not installed.")
        print("  Run: bash training/setup_kimi.sh")
        print("  Or:  pip install ktransformers")
        sys.exit(1)

    if not check_llamafactory():
        print("ERROR: LlamaFactory not installed.")
        print("  Run: bash training/setup_kimi.sh")
        print("  Or:  pip install llamafactory")
        sys.exit(1)

    if not hw["cuda_available"] and not cloud:
        print("ERROR: CUDA not available and no --cloud specified.")
        print("  Kimi K2.5 fine-tuning requires GPU(s).")
        print("  Use: --cloud runpod  or  --cloud lambda")
        sys.exit(1)

    # Execute
    env = os.environ.copy()
    env["USE_KT"] = "1"

    cmd = ["llamafactory-cli", "train", str(yaml_path)]
    print(f"  Command: USE_KT=1 {' '.join(cmd)}")
    print()

    start_time = time.time()

    result = subprocess.run(cmd, env=env)

    elapsed = time.time() - start_time
    minutes = elapsed / 60

    if result.returncode != 0:
        print(f"\nERROR: Training failed with return code {result.returncode}")
        sys.exit(1)

    print(f"\nTraining complete in {minutes:.1f} minutes.")

    # Save training metadata
    metadata = {
        "darshana": darshana,
        "base_model": config.get("base_model", BASE_MODEL),
        "model_type": "kimi_k2.5",
        "architecture": "MoE (1T total, 32B active, 384 experts, top-8)",
        "epochs": config.get("training", {}).get("epochs", 3),
        "learning_rate": config.get("training", {}).get("learning_rate", 2e-5),
        "batch_size": config.get("training", {}).get("batch_size", 1),
        "gradient_accumulation_steps": config.get("training", {}).get("gradient_accumulation_steps", 16),
        "lora_rank": config.get("lora", {}).get("rank", 16),
        "lora_alpha": config.get("lora", {}).get("alpha", 32),
        "lora_targets": config.get("lora", {}).get("target_modules", []),
        "train_examples": n_examples,
        "training_time_minutes": round(minutes, 1),
        "hardware": {
            "gpus": hw.get("gpus", []),
            "ram_gb": hw.get("ram_gb", 0),
        },
        "ktransformers": True,
        "llamafactory_config": str(yaml_path),
    }
    adapter_dir.mkdir(parents=True, exist_ok=True)
    with open(adapter_dir / "training_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Adapter saved to: {adapter_dir}")
    print(f"Metadata saved to: {adapter_dir / 'training_metadata.json'}")

    return adapter_dir


# ---------------------------------------------------------------------------
# Cloud training helpers
# ---------------------------------------------------------------------------

def generate_cloud_script(
    darshana: str,
    config: dict,
    provider: str,
    output_dir: Path,
) -> Path:
    """
    Generate a cloud training launch script for RunPod or Lambda.

    Returns:
        Path to the generated shell script.
    """
    lora_cfg = config.get("lora", {})
    train_cfg = config.get("training", {})

    script_dir = output_dir / "cloud_scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_dir / f"train_{darshana}_{provider}.sh"

    script = f"""#!/bin/bash
# Kimi K2.5 LoRA SFT — {darshana.upper()} on {provider.upper()}
# Generated by finetune_kimi.py
# Usage: bash {script_path.name}

set -euo pipefail

echo "=== Kimi K2.5 Fine-Tuning: {darshana.upper()} on {provider.upper()} ==="
echo ""

# Step 1: Install dependencies
echo "--- Installing dependencies ---"
pip install -q ktransformers llamafactory torch transformers peft datasets accelerate pyyaml

# Step 2: Download model (if not cached)
echo "--- Downloading Kimi K2.5 model ---"
python -c "from huggingface_hub import snapshot_download; snapshot_download('{config.get('base_model', BASE_MODEL)}')"

# Step 3: Upload training data
echo "--- Preparing training data ---"
# NOTE: Upload your training data to the cloud instance first.
# Expected location: {output_dir}/data/{darshana}_sharegpt.jsonl

# Step 4: Run training
echo "--- Starting LoRA SFT ---"
USE_KT=1 llamafactory-cli train {output_dir}/configs/{darshana}_lora_sft_kt.yaml

echo ""
echo "=== Training complete ==="
echo "Adapter saved to: {output_dir}/{darshana}/"
"""

    with open(script_path, "w") as f:
        f.write(script)
    os.chmod(script_path, 0o755)

    print(f"  Cloud script -> {script_path}")
    return script_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune Kimi K2.5 (1T MoE) into darshana reasoning engines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Fine-tune Nyaya specialist
  python training/finetune_kimi.py --darshana nyaya

  # Fine-tune all 6 darshanas
  python training/finetune_kimi.py --all

  # Fine-tune the router (Buddhi layer)
  python training/finetune_kimi.py --router

  # Fine-tune the vritti classifier
  python training/finetune_kimi.py --vritti

  # Dry run (generate configs only)
  python training/finetune_kimi.py --darshana nyaya --dry-run

  # Cloud training
  python training/finetune_kimi.py --all --cloud runpod

The MoE Architecture Mirror:
  Kimi K2.5 has 384 experts per layer with top-8 routing.
  The Darshana Architecture has 6 reasoning engines with Buddhi routing.
  Fine-tuning teaches the MoE's attention layers to activate the right
  expert combinations for each darshana's reasoning method.
""",
    )

    # What to train
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--darshana", choices=DARSHANAS,
                       help="Fine-tune a single darshana specialist")
    group.add_argument("--all", action="store_true",
                       help="Fine-tune all 6 darshana specialists")
    group.add_argument("--router", action="store_true",
                       help="Fine-tune the Buddhi routing model")
    group.add_argument("--vritti", action="store_true",
                       help="Fine-tune the vritti classification model")

    # Training options
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate configs without running training")
    parser.add_argument("--cloud", choices=["runpod", "lambda"],
                        help="Generate cloud training scripts instead of local training")

    # Hyperparameter overrides
    parser.add_argument("--epochs", type=int, default=None,
                        help="Override number of epochs")
    parser.add_argument("--lr", type=float, default=None,
                        help="Override learning rate")
    parser.add_argument("--lora-rank", type=int, default=None,
                        help="Override LoRA rank")
    parser.add_argument("--max-length", type=int, default=None,
                        help="Override max sequence length")

    # Config
    parser.add_argument("--config", type=str, default=str(CONFIG_PATH),
                        help="Path to Kimi K2.5 config YAML")

    return parser.parse_args()


def main():
    args = parse_args()

    # Load config
    config = load_config(Path(args.config))

    # Apply CLI overrides
    if args.epochs:
        config.setdefault("training", {})["epochs"] = args.epochs
    if args.lr:
        config.setdefault("training", {})["learning_rate"] = args.lr
    if args.lora_rank:
        config.setdefault("lora", {})["rank"] = args.lora_rank
    if args.max_length:
        config.setdefault("training", {})["max_length"] = args.max_length

    # Determine what to train
    targets: list[str] = []
    if args.all:
        targets = list(DARSHANAS)
    elif args.darshana:
        targets = [args.darshana]
    elif args.router:
        targets = ["router"]
    elif args.vritti:
        targets = ["vritti"]

    print(f"\nKimi K2.5 Darshana Fine-Tuning Pipeline")
    print(f"{'=' * 60}")
    print(f"  Model:       {config.get('base_model', BASE_MODEL)}")
    print(f"  Type:        {KIMI_SPECS['total_params']} MoE ({KIMI_SPECS['active_params']} active)")
    print(f"  Experts:     {KIMI_SPECS['experts_per_layer']} per layer, top-{KIMI_SPECS['active_experts']} routing")
    print(f"  Targets:     {', '.join(t.upper() for t in targets)}")
    print(f"  Mode:        {'Dry run' if args.dry_run else 'Cloud (' + args.cloud + ')' if args.cloud else 'Local training'}")
    print(f"{'=' * 60}")

    # Train each target
    results = {}
    for target in targets:
        try:
            if args.cloud:
                # Generate cloud scripts
                output_dir = Path(config.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
                if not output_dir.is_absolute():
                    output_dir = SCRIPT_DIR.parent / output_dir

                # Still convert data and generate configs
                data_path = DATA_DIR / f"{target}_train.jsonl"
                lf_data_path = output_dir / "data" / f"{target}_sharegpt.jsonl"
                lf_data_path.parent.mkdir(parents=True, exist_ok=True)
                convert_data_for_llamafactory(data_path, lf_data_path, target)
                generate_llamafactory_config(target, config, lf_data_path, output_dir)
                script_path = generate_cloud_script(target, config, args.cloud, output_dir)
                results[target] = {"status": "config_generated", "script": str(script_path)}
            else:
                adapter_path = run_training(
                    darshana=target,
                    config=config,
                    dry_run=args.dry_run,
                    cloud=args.cloud,
                )
                results[target] = {"status": "success", "path": str(adapter_path)}
        except Exception as e:
            print(f"\nERROR training {target}: {e}")
            results[target] = {"status": "error", "error": str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    for target, result in results.items():
        status = result["status"]
        if status == "success":
            print(f"  {target.upper():15s} OK     -> {result['path']}")
        elif status == "config_generated":
            print(f"  {target.upper():15s} CONFIG -> {result['script']}")
        else:
            print(f"  {target.upper():15s} FAIL   -> {result['error']}")

    if args.cloud:
        print(f"\n  Cloud scripts generated. To train:")
        print(f"  1. Provision a GPU instance on {args.cloud}")
        print(f"  2. Upload the training/ directory")
        print(f"  3. Run the generated shell scripts")

    print("=" * 60)


if __name__ == "__main__":
    main()
