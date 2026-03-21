#!/usr/bin/env python3
"""
__main__.py — CLI entry point for the Darshana Architecture

Run the six darshana reasoning engines, vritti filter, and demos
from the command line. With --llm, routes through real Anthropic
Claude API calls with darshana-specific system prompts.

Usage:
    python -m src "Is this argument valid?"
    python -m src --llm "Should we rewrite our backend in Rust?"
    python -m src --llm --multi "What is consciousness?"
    python -m src --darshana nyaya "Prove that X implies Y"
    python -m src --filter "Check this text for errors"
    python -m src --explain "Debug this failing test"
    python -m src --demo
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional


def _route_single(query: str, darshana: Optional[str] = None) -> None:
    """Route a query through the Buddhi layer to a single darshana."""
    from .darshana_router import DarshanaRouter

    router = DarshanaRouter()

    if darshana:
        # Force a specific darshana
        if darshana not in router.engines:
            print(f"Error: unknown darshana '{darshana}'")
            print(f"Available: {', '.join(router.engines.keys())}")
            sys.exit(1)

        engine = router.engines[darshana]
        guna = router.guna_engine.classify(query)
        output = engine.reason(query)
        output.guna = guna

        print(f"\nDarshana: {darshana}")
        print(f"Guna:     {guna.value}")
        print(f"\nApproach:\n{output.approach}")
        print(f"\nPrompt template:\n{output.prompt_template}")
    else:
        result = router.route_and_reason(query)
        routing = result.routing

        print(f"\n{router.explain_routing(routing)}")
        for output in result.reasoning:
            print(f"\n--- {output.engine.upper()} ---")
            print(f"Approach:\n{output.approach}")
            print(f"\nPrompt template:\n{output.prompt_template}")


def _route_multi(query: str) -> None:
    """Route a query with multi-engine activation (up to 3 darshanas)."""
    from .darshana_router import DarshanaRouter

    router = DarshanaRouter(max_engines=3)
    result = router.route_and_reason(query)
    routing = result.routing

    print(f"\n{router.explain_routing(routing)}")
    print(f"\nActivated {len(result.reasoning)} engine(s):\n")
    for output in result.reasoning:
        print(f"=== {output.engine.upper()} ===")
        print(f"Approach:\n{output.approach}")
        print(f"\nPrompt template:\n{output.prompt_template}\n")


def _filter_text(text: str) -> None:
    """Run text through the Vritti Filter (five-vritti classification)."""
    from .vritti_filter import VrittiFilter

    vf = VrittiFilter()
    result = vf.classify(text)

    print(f"\nVritti:     {result.vritti.value}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Explanation: {result.explanation}")
    if result.fallacies:
        print(f"Fallacies:  {', '.join(f.value for f in result.fallacies)}")
    if result.suggestions:
        print("Suggestions:")
        for s in result.suggestions:
            print(f"  - {s}")

    print(f"\nFiltered output:")
    print(vf.filter(text))


def _run_llm(
    query: str,
    multi: bool = False,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> None:
    """Run a query through the DarshanaLLM with real Anthropic API calls."""
    from .darshana_llm import DarshanaLLM

    try:
        llm = DarshanaLLM(model=model, api_key=api_key)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if multi:
        print(f"Running multi-darshana analysis...\n")
        result = llm.think_multi(query)

        for resp in result.individual:
            engine = resp.darshana[0].upper()
            print(f"{'='*60}")
            print(f"  {engine} (vritti: {resp.vritti}, confidence: {resp.confidence:.2f})")
            print(f"{'='*60}")
            print(resp.raw_text)
            print()

        print(f"{'='*60}")
        print(f"  VEDANTA SYNTHESIS")
        print(f"{'='*60}")
        print(result.synthesis.text)
        print()
        print(f"Engines used: {', '.join(result.engines_used)}")
        print(f"Total latency: {result.total_latency_ms:.0f}ms")
    else:
        response = llm.think(query)

        print(f"Darshana:    {', '.join(response.darshana)}")
        print(f"Guna:        {response.guna}")
        print(f"Vritti:      {response.vritti}")
        print(f"Pramana:     {response.pramana}")
        print(f"Confidence:  {response.confidence:.2f}")
        print(f"Model:       {response.model}")
        print(f"Latency:     {response.latency_ms:.0f}ms")
        print(f"Tokens:      {response.input_tokens} in / {response.output_tokens} out")
        if response.maya_gaps:
            print(f"Maya gaps:   {len(response.maya_gaps)}")
            for gap in response.maya_gaps:
                print(f"  - [{gap['gap_type']}] {gap['description']}")
        print()
        print("--- RESPONSE ---")
        print(response.text)


def _run_demos() -> None:
    """Run the built-in router and filter demos."""
    from .demo import run_demo
    from .demo_filter import main as run_filter_demo

    run_demo()
    print("\n" + "=" * 72 + "\n")
    run_filter_demo()


def main() -> None:
    """CLI entry point for the Darshana Architecture."""
    parser = argparse.ArgumentParser(
        prog="darshana",
        description=(
            "The Darshana Architecture — Hindu philosophical reasoning "
            "framework for AI.\n\n"
            "Routes queries through six classical reasoning engines "
            "(Nyaya, Samkhya, Yoga, Vedanta, Mimamsa, Vaisheshika), "
            "classifies processing mode via the three Gunas, and tags "
            "knowledge claims with their Pramana (epistemic source)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "The six darshanas:\n"
            "  nyaya        Logic, proof chains, fallacy detection\n"
            "  samkhya      Decomposition, classification, enumeration\n"
            "  yoga         Noise filtering, focus, relevance ranking\n"
            "  vedanta      Contradiction resolution, synthesis\n"
            "  mimamsa      Text interpretation, action extraction\n"
            "  vaisheshika  Atomic analysis, root cause, ontology\n"
            "\n"
            "The three gunas (processing modes):\n"
            "  sattva       Precision — low temperature, strict validation\n"
            "  rajas        Exploration — high temperature, creative divergence\n"
            "  tamas        Retrieval — cached patterns, efficient lookup\n"
            "\n"
            "Examples:\n"
            '  darshana "Is this argument valid?"\n'
            '  darshana --multi "Should we rewrite in Rust?"\n'
            '  darshana --darshana nyaya "Prove that X implies Y"\n'
            '  darshana --filter "Check this text for errors"\n'
            "  darshana --demo\n"
        ),
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="The query or text to process through the Buddhi layer",
    )
    parser.add_argument(
        "--multi",
        action="store_true",
        help=(
            "Activate multiple darshana engines (up to 3). "
            "Complex queries benefit from complementary perspectives."
        ),
    )
    parser.add_argument(
        "--darshana",
        metavar="NAME",
        help=(
            "Force routing to a specific darshana engine. "
            "One of: nyaya, samkhya, yoga, vedanta, mimamsa, vaisheshika."
        ),
    )
    parser.add_argument(
        "--filter",
        action="store_true",
        help=(
            "Run the Vritti Filter instead of the router. "
            "Classifies text into the five vrittis from Yoga Sutra 1.5: "
            "pramana (valid), viparyaya (error), vikalpa (empty), "
            "nidra (absent), smriti (recalled)."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the built-in demos showcasing all six darshanas and the vritti filter.",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help=(
            "Use the DarshanaLLM wrapper to make real Anthropic API calls "
            "with darshana-specific system prompts. Requires ANTHROPIC_API_KEY."
        ),
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show routing classification only (no API call).",
    )
    parser.add_argument(
        "--model",
        metavar="MODEL",
        help="Anthropic model to use (default: claude-sonnet-4-20250514).",
    )
    parser.add_argument(
        "--api-key",
        metavar="KEY",
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var).",
    )

    args = parser.parse_args()

    if args.demo:
        _run_demos()
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    if args.explain:
        _route_single(args.query, darshana=args.darshana)
    elif args.llm:
        _run_llm(args.query, multi=args.multi, model=args.model, api_key=args.api_key)
    elif args.filter:
        _filter_text(args.query)
    elif args.multi:
        _route_multi(args.query)
    else:
        _route_single(args.query, darshana=args.darshana)


if __name__ == "__main__":
    main()
