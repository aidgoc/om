#!/usr/bin/env python3
"""
serve_kimi.py — Kimi K2.5 Darshana Inference Server
=====================================================

HTTP API for serving Kimi K2.5 with fine-tuned darshana LoRA adapters.
Uses KTransformers for efficient MoE inference — expert layers stay on
CPU/RAM while attention layers (with LoRA adapters) run on GPU.

Usage:
    # Serve all darshanas with auto-routing
    python training/serve_kimi.py --all --port 8000

    # Serve a single darshana
    python training/serve_kimi.py --darshana nyaya --port 8000

    # Custom adapter path
    python training/serve_kimi.py --darshana nyaya \
        --adapter training/adapters/kimi-k2.5/nyaya/ --port 8000

API:
    POST /think     {"query": "...", "darshana": "nyaya"}  -> reasoning response
    POST /route     {"query": "..."}                        -> routing decision
    POST /classify  {"text": "..."}                         -> vritti classification
    GET  /health                                            -> status + memory usage

Architecture:
    KTransformers handles the MoE offloading automatically:
    - Expert layers: CPU/RAM (INT4, ~200GB RAM usage)
    - Attention layers: GPU VRAM (BF16 + LoRA adapters)
    - Router: GPU (for fast expert selection)

    This means we can serve a 1T-parameter model on 2x RTX 4090 + 256GB RAM.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import torch
import yaml
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Add parent to path for imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.darshana_router import DarshanaRouter  # noqa: E402
from src.vritti_filter import VrittiFilter       # noqa: E402
from src.prompts import DARSHANA_PROMPTS         # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config_kimi.yaml"
ADAPTERS_DIR = SCRIPT_DIR / "adapters" / "kimi-k2.5"
DARSHANAS = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]

BASE_MODEL = "moonshotai/Kimi-K2.5-Instruct"


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """Load Kimi K2.5 YAML configuration."""
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {"base_model": BASE_MODEL}


# ---------------------------------------------------------------------------
# KTransformers Model Manager
# ---------------------------------------------------------------------------

class KimiModelManager:
    """
    Manages Kimi K2.5 with KTransformers offloading and LoRA adapter swapping.

    Architecture mapping:
        - Base model MoE   = Prakriti (undifferentiated potential, 384 experts)
        - LoRA adapter      = darshana specialization (shapes attention patterns)
        - Expert routing    = inherent MoE routing (which experts activate)
        - Adapter swap      = Buddhi routing (which reasoning method to apply)

    The two-level routing is key:
        1. Buddhi selects the darshana (which LoRA adapter to activate)
        2. MoE routing selects which experts to activate for each token
        Together they create a deeply specialized reasoning pipeline.
    """

    def __init__(self, base_model_name: str, adapter_paths: dict[str, Path]):
        self.base_model_name = base_model_name
        self.adapter_paths = adapter_paths
        self.model = None
        self.tokenizer = None
        self.loaded_adapters: set[str] = set()
        self.active_adapter: Optional[str] = None
        self.load_time: float = 0
        self.memory_usage: dict = {}

    def load(self) -> None:
        """
        Load Kimi K2.5 via KTransformers with MoE offloading.

        KTransformers automatically:
        - Keeps attention layers (LoRA targets) on GPU in BF16
        - Offloads MoE expert layers to CPU/RAM in INT4
        - Handles the routing between GPU and CPU layers
        """
        start = time.time()

        print(f"\nLoading Kimi K2.5 via KTransformers...")
        print(f"  Model: {self.base_model_name}")
        print(f"  This will take several minutes (loading 1T parameters)...")
        print()

        try:
            # Try KTransformers-accelerated loading
            from ktransformers import AutoModel as KTAutoModel
            from transformers import AutoTokenizer

            self.model = KTAutoModel.from_pretrained(
                self.base_model_name,
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_name,
                trust_remote_code=True,
            )

            print("  Loaded via KTransformers (MoE offloading active)")

        except ImportError:
            print("  WARNING: KTransformers not available. Falling back to standard loading.")
            print("  This will require significantly more VRAM.")
            print("  Install KTransformers: pip install ktransformers")
            print()

            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_name,
                trust_remote_code=True,
            )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load LoRA adapters
        if self.adapter_paths:
            from peft import PeftModel

            adapter_items = list(self.adapter_paths.items())
            first_name, first_path = adapter_items[0]
            print(f"  Loading adapter: {first_name} from {first_path}")
            self.model = PeftModel.from_pretrained(
                self.model, str(first_path), adapter_name=first_name
            )
            self.loaded_adapters.add(first_name)
            self.active_adapter = first_name

            for name, path in adapter_items[1:]:
                print(f"  Loading adapter: {name} from {path}")
                self.model.load_adapter(str(path), adapter_name=name)
                self.loaded_adapters.add(name)

        self.load_time = time.time() - start
        self._update_memory_usage()

        print(f"\n  Load time:        {self.load_time:.1f}s")
        print(f"  Adapters loaded:  {len(self.loaded_adapters)} ({', '.join(sorted(self.loaded_adapters))})")
        self._print_memory_usage()

    def _update_memory_usage(self) -> None:
        """Capture current memory usage."""
        self.memory_usage = {
            "gpu_allocated_gb": 0,
            "gpu_reserved_gb": 0,
            "ram_used_gb": 0,
        }

        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                allocated = torch.cuda.memory_allocated(i) / (1024 ** 3)
                reserved = torch.cuda.memory_reserved(i) / (1024 ** 3)
                self.memory_usage["gpu_allocated_gb"] += allocated
                self.memory_usage["gpu_reserved_gb"] += reserved
            self.memory_usage["gpu_allocated_gb"] = round(
                self.memory_usage["gpu_allocated_gb"], 2
            )
            self.memory_usage["gpu_reserved_gb"] = round(
                self.memory_usage["gpu_reserved_gb"], 2
            )

        try:
            import psutil
            process = psutil.Process(os.getpid())
            self.memory_usage["ram_used_gb"] = round(
                process.memory_info().rss / (1024 ** 3), 2
            )
        except ImportError:
            pass

    def _print_memory_usage(self) -> None:
        """Print memory usage summary."""
        self._update_memory_usage()
        print(f"  GPU allocated:    {self.memory_usage['gpu_allocated_gb']} GB")
        print(f"  GPU reserved:     {self.memory_usage['gpu_reserved_gb']} GB")
        print(f"  RAM used:         {self.memory_usage['ram_used_gb']} GB")

    def generate(
        self,
        prompt: str,
        darshana: Optional[str] = None,
        system_prompt: str = "",
        max_new_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Generate a response, optionally switching to a specific LoRA adapter.

        The two-level routing:
        1. We select the LoRA adapter (darshana specialization)
        2. The MoE layer internally routes to the best experts per token

        Args:
            prompt: User query.
            darshana: Which adapter to use (None = base model).
            system_prompt: System prompt to prepend.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling threshold.

        Returns:
            Generated text.
        """
        # Switch adapter if needed
        if darshana and darshana in self.loaded_adapters:
            if self.active_adapter != darshana:
                self.model.set_adapter(darshana)
                self.active_adapter = darshana
        elif darshana and darshana not in self.loaded_adapters:
            if hasattr(self.model, "disable_adapter_layers"):
                self.model.disable_adapter_layers()
                self.active_adapter = None

        # Build chat messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            text = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True,
            max_length=4096,
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        # Re-enable adapter if we disabled it
        if self.active_adapter is None and self.loaded_adapters:
            if hasattr(self.model, "enable_adapter_layers"):
                self.model.enable_adapter_layers()

        return response.strip()


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

def create_app(
    model_manager: KimiModelManager,
    router: DarshanaRouter,
    vritti_filter: VrittiFilter,
) -> Flask:
    """Create the Flask application with all endpoints."""

    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        model_manager._update_memory_usage()
        return jsonify({
            "status": "ok",
            "model": "Kimi K2.5",
            "base_model": model_manager.base_model_name,
            "architecture": "MoE (1T total, 32B active, 384 experts, top-8)",
            "loaded_adapters": sorted(model_manager.loaded_adapters),
            "active_adapter": model_manager.active_adapter,
            "load_time_seconds": round(model_manager.load_time, 1),
            "memory": model_manager.memory_usage,
            "device": str(next(model_manager.model.parameters()).device)
                     if model_manager.model else "not loaded",
        })

    @app.route("/think", methods=["POST"])
    def think():
        """
        Main reasoning endpoint with Kimi K2.5 + darshana LoRA.

        The full pipeline:
        1. Buddhi router selects the darshana
        2. LoRA adapter activates for that darshana
        3. Kimi K2.5 MoE generates with specialized attention patterns
        4. Vritti filter classifies the output quality

        Request:
            {"query": "...", "darshana": "nyaya"}  (darshana optional)

        Response:
            {"darshana": "...", "response": "...", "routing": {...}, "vritti": {...}}
        """
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        query = data["query"]
        darshana = data.get("darshana")

        start = time.time()

        # Route if no darshana specified
        routing_info = {}
        if not darshana:
            routing_result = router.route(query)
            darshana = routing_result.top_engines[0] if routing_result.top_engines else "nyaya"
            routing_info = {
                "selected": darshana,
                "scores": routing_result.engine_scores,
                "guna": routing_result.guna.value,
                "all_engines": routing_result.top_engines,
            }

        # Get system prompt
        system_prompt = DARSHANA_PROMPTS.get(darshana, "")

        # Generate
        response_text = model_manager.generate(
            prompt=query,
            darshana=darshana,
            system_prompt=system_prompt,
            max_new_tokens=data.get("max_tokens", 2048),
            temperature=data.get("temperature", 0.7),
        )

        # Classify output
        vritti_result = vritti_filter.classify(response_text, context=query)

        elapsed = time.time() - start

        return jsonify({
            "model": "kimi-k2.5",
            "darshana": darshana,
            "response": response_text,
            "routing": routing_info,
            "vritti": {
                "classification": vritti_result.vritti.value,
                "confidence": vritti_result.confidence,
                "explanation": vritti_result.explanation,
            },
            "elapsed_seconds": round(elapsed, 2),
            "tokens_generated": len(model_manager.tokenizer.encode(response_text)),
        })

    @app.route("/route", methods=["POST"])
    def route():
        """Routing-only endpoint (Buddhi layer)."""
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        result = router.route(data["query"])
        return jsonify({
            "engines": result.top_engines,
            "scores": result.engine_scores,
            "guna": result.guna.value,
        })

    @app.route("/classify", methods=["POST"])
    def classify():
        """Vritti classification endpoint."""
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        result = vritti_filter.classify(
            data["text"], context=data.get("context")
        )
        depth = vritti_filter.depth_test(
            data["text"], data.get("context", "")
        )
        novelty = vritti_filter.novelty_score(data["text"])

        return jsonify({
            "vritti": result.vritti.value,
            "confidence": result.confidence,
            "explanation": result.explanation,
            "depth_score": depth.score if hasattr(depth, "score") else int(depth),
            "novelty_score": novelty,
        })

    return app


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve Kimi K2.5 with darshana LoRA adapters via HTTP",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--darshana", type=str, choices=DARSHANAS,
                       help="Serve a single darshana")
    group.add_argument("--all", action="store_true",
                       help="Serve all available darshanas")

    parser.add_argument("--adapter", type=str, default=None,
                        help="Path to adapter (for single darshana mode)")
    parser.add_argument("--base-model", type=str, default=None,
                        help="Override base model name")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to serve on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--config", type=str, default=str(CONFIG_PATH),
                        help="Path to Kimi K2.5 config YAML")

    return parser.parse_args()


def main():
    args = parse_args()

    # Load config
    config = load_config(Path(args.config))
    base_model = args.base_model or config.get("base_model", BASE_MODEL)

    # Determine which adapters to load
    adapter_paths: dict[str, Path] = {}

    if args.all:
        for darshana in DARSHANAS:
            adapter_dir = ADAPTERS_DIR / darshana
            if adapter_dir.exists() and (adapter_dir / "adapter_config.json").exists():
                adapter_paths[darshana] = adapter_dir
            else:
                print(f"No adapter found for {darshana} at {adapter_dir}, skipping")

        for special in ["router", "vritti"]:
            adapter_dir = ADAPTERS_DIR / special
            if adapter_dir.exists() and (adapter_dir / "adapter_config.json").exists():
                adapter_paths[special] = adapter_dir

    elif args.darshana:
        adapter_dir = Path(args.adapter) if args.adapter else ADAPTERS_DIR / args.darshana
        if adapter_dir.exists():
            adapter_paths[args.darshana] = adapter_dir
        else:
            print(f"WARNING: No adapter at {adapter_dir}. Serving base Kimi K2.5 only.")

    if not adapter_paths:
        print("WARNING: No adapters found. Serving base Kimi K2.5 without specialization.")

    # Detect base model from adapter metadata
    for path in adapter_paths.values():
        meta = path / "training_metadata.json"
        if meta.exists():
            with open(meta) as f:
                base_model = json.load(f).get("base_model", base_model)
            break

    # Initialize
    model_manager = KimiModelManager(base_model, adapter_paths)
    model_manager.load()

    router_instance = DarshanaRouter()
    vritti_instance = VrittiFilter()

    app = create_app(model_manager, router_instance, vritti_instance)

    print(f"\nKimi K2.5 Darshana Inference Server")
    print(f"{'=' * 60}")
    print(f"  Model:       {base_model}")
    print(f"  Architecture: MoE (1T total, 32B active, 384 experts)")
    print(f"  Offloading:  KTransformers (experts on CPU, attention on GPU)")
    print(f"  Adapters:    {', '.join(adapter_paths.keys()) or 'none'}")
    print(f"  Load time:   {model_manager.load_time:.1f}s")
    print(f"  Endpoints:")
    print(f"    POST /think     - reasoning with auto-routing")
    print(f"    POST /route     - routing decision only")
    print(f"    POST /classify  - vritti classification")
    print(f"    GET  /health    - server status + memory usage")
    print(f"\n  Listening on http://{args.host}:{args.port}")
    print("=" * 60 + "\n")

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
