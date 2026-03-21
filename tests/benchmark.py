#!/usr/bin/env python3
"""
benchmark.py — Darshana Router Accuracy Benchmark
===================================================

20 real-world queries across all 6 darshanas. Validates that the Buddhi
layer (DarshanaRouter) routes each query to the correct reasoning engine.

This is NOT a unit test. It is a demonstration that the routing actually
works on queries people would ask in practice. The output is formatted
for a blog post.

Runs entirely offline — no API keys, no LLM calls. Pure pattern-matching
classification as implemented in darshana_router.py.

Usage:
    python -m tests.benchmark          (from /Users/harsh/om/)
    python tests/benchmark.py          (from /Users/harsh/om/)

Author: Harsh (with Claude as co-thinker)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure the src directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from darshana_router import DarshanaRouter, RoutingResult


# ---------------------------------------------------------------------------
# The 20 benchmark queries
# ---------------------------------------------------------------------------

BENCHMARK_QUERIES: list[dict] = [
    # --- NYAYA (Logic / Validation) — 3 queries ---
    {
        "id": 1,
        "query": (
            "Is this argument valid: remote work increases productivity "
            "because employees report higher satisfaction?"
        ),
        "expected": "nyaya",
        "category": "NYAYA",
        "why": "Evaluating argument validity is a core Nyaya operation.",
    },
    {
        "id": 2,
        "query": (
            "My code passes all tests but crashes in production. "
            "The tests must be wrong."
        ),
        "expected": "nyaya",
        "category": "NYAYA",
        "why": "This contains a logical fallacy (affirming the consequent).",
    },
    {
        "id": 3,
        "query": (
            "We should use microservices because Netflix uses microservices "
            "and they're successful."
        ),
        "expected": "nyaya",
        "category": "NYAYA",
        "why": "Appeal to authority / false analogy — fallacy detection.",
    },
    # --- SAMKHYA (Decomposition) — 3 queries ---
    {
        "id": 4,
        "query": "What are all the components of a Kubernetes deployment?",
        "expected": "samkhya",
        "category": "SAMKHYA",
        "why": "Enumerate parts of a complex system.",
    },
    {
        "id": 5,
        "query": "Break down the factors that affect crane lift capacity.",
        "expected": "samkhya",
        "category": "SAMKHYA",
        "why": "Decomposition into constituent factors.",
    },
    {
        "id": 6,
        "query": (
            "Map the layers of our tech stack from infrastructure "
            "to user interface."
        ),
        "expected": "samkhya",
        "category": "SAMKHYA",
        "why": "Layer mapping / hierarchical enumeration.",
    },
    # --- YOGA (Focus / Noise Reduction) — 3 queries ---
    {
        "id": 7,
        "query": (
            "I have 47 Jira tickets, 12 Slack threads, 3 PRs to review, "
            "and a deploy. What should I focus on?"
        ),
        "expected": "yoga",
        "category": "YOGA",
        "why": "Information overload — needs prioritisation and focus.",
    },
    {
        "id": 8,
        "query": (
            "There are too many options for our database. Postgres, MySQL, "
            "MongoDB, DynamoDB, Supabase, PlanetScale... help."
        ),
        "expected": "yoga",
        "category": "YOGA",
        "why": "Option overload — needs noise reduction.",
    },
    {
        "id": 9,
        "query": "This error log is 500 lines. What actually matters?",
        "expected": "yoga",
        "category": "YOGA",
        "why": "Signal extraction from noise.",
    },
    # --- VEDANTA (Contradiction Resolution) — 3 queries ---
    {
        "id": 10,
        "query": (
            "The marketing team says we need more features. The engineering "
            "team says we need less complexity. Who's right?"
        ),
        "expected": "vedanta",
        "category": "VEDANTA",
        "why": "Two valid but opposing perspectives need reconciliation.",
    },
    {
        "id": 11,
        "query": (
            "Move fast and break things vs. measure twice cut once. "
            "Which philosophy should we follow?"
        ),
        "expected": "vedanta",
        "category": "VEDANTA",
        "why": "Philosophical contradiction needing synthesis.",
    },
    {
        "id": 12,
        "query": (
            "Our tests say the code is correct but users say it's broken."
        ),
        "expected": "vedanta",
        "category": "VEDANTA",
        "why": "Apparent contradiction between two sources of truth.",
    },
    # --- MIMAMSA (Text -> Action) — 4 queries ---
    {
        "id": 13,
        "query": (
            "Here are the meeting notes from the sprint planning. "
            "What are the action items?"
        ),
        "expected": "mimamsa",
        "category": "MIMAMSA",
        "why": "Extract actionable items from text.",
    },
    {
        "id": 14,
        "query": (
            "Read this contract and tell me what we're obligated to do."
        ),
        "expected": "mimamsa",
        "category": "MIMAMSA",
        "why": "Parse text to derive obligations (vidhis).",
    },
    {
        "id": 15,
        "query": (
            "The client sent a 3-page email. What do they actually want?"
        ),
        "expected": "mimamsa",
        "category": "MIMAMSA",
        "why": "Intent extraction from lengthy text.",
    },
    {
        "id": 16,
        "query": (
            "Parse this error message and tell me exactly what to fix."
        ),
        "expected": "mimamsa",
        "category": "MIMAMSA",
        "why": "Interpret technical text into concrete action.",
    },
    # --- VAISHESHIKA (Atomic Analysis) — 4 queries ---
    {
        "id": 17,
        "query": "What's the root cause of this memory leak?",
        "expected": "vaisheshika",
        "category": "VAISHESHIKA",
        "why": "Root cause analysis — tracing to the atomic source.",
    },
    {
        "id": 18,
        "query": (
            "Why does this CSS look wrong? Break it down property "
            "by property."
        ),
        "expected": "vaisheshika",
        "category": "VAISHESHIKA",
        "why": "Atomic decomposition of properties.",
    },
    {
        "id": 19,
        "query": (
            "What are the irreducible components of a good pull request?"
        ),
        "expected": "vaisheshika",
        "category": "VAISHESHIKA",
        "why": "Finding irreducible atoms (paramanu) of a concept.",
    },
    {
        "id": 20,
        "query": (
            "Debug this: the API returns 200 but the data is wrong."
        ),
        "expected": "vaisheshika",
        "category": "VAISHESHIKA",
        "why": "Debugging — isolating the faulty atom.",
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_benchmark() -> None:
    """Execute all 20 queries and print a formatted report."""

    router = DarshanaRouter()
    results: list[dict] = []
    timings: list[float] = []

    for entry in BENCHMARK_QUERIES:
        t0 = time.perf_counter()
        routing: RoutingResult = router.route(entry["query"])
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        timings.append(elapsed_ms)

        primary = routing.top_engines[0] if routing.top_engines else "none"
        correct = primary == entry["expected"]
        expected_score = routing.engine_scores.get(entry["expected"], 0.0)
        primary_score = routing.engine_scores.get(primary, 0.0)

        results.append({
            "id": entry["id"],
            "category": entry["category"],
            "expected": entry["expected"],
            "primary": primary,
            "all_engines": routing.top_engines,
            "correct": correct,
            "primary_score": primary_score,
            "expected_score": expected_score,
            "guna": routing.guna.value,
            "all_scores": routing.engine_scores,
            "time_ms": elapsed_ms,
            "query_short": entry["query"][:70] + ("..." if len(entry["query"]) > 70 else ""),
            "why": entry["why"],
        })

    # --- Compute stats ---
    total = len(results)
    correct_count = sum(1 for r in results if r["correct"])
    accuracy = correct_count / total
    correct_confs = [r["primary_score"] for r in results if r["correct"]]
    incorrect_confs = [r["primary_score"] for r in results if not r["correct"]]
    avg_correct_conf = sum(correct_confs) / len(correct_confs) if correct_confs else 0.0
    avg_incorrect_conf = sum(incorrect_confs) / len(incorrect_confs) if incorrect_confs else 0.0

    # --- Print report ---
    print()
    print("=" * 100)
    print("  DARSHANA ROUTER BENCHMARK — 20 Real-World Queries")
    print("=" * 100)
    print()

    # Main results table
    hdr = f"{'#':>2}  {'Category':<13} {'Expected':<14} {'Routed To':<14} {'Score':>6} {'Guna':<8} {'Time':>7}  {'':>4}  Query"
    print(hdr)
    print("-" * len(hdr) + "-" * 40)

    for r in results:
        mark = " OK " if r["correct"] else "MISS"
        style = "" if r["correct"] else " <<"
        print(
            f"{r['id']:>2}  "
            f"{r['category']:<13} "
            f"{r['expected']:<14} "
            f"{r['primary']:<14} "
            f"{r['primary_score']:>5.3f} "
            f"{r['guna']:<8} "
            f"{r['time_ms']:>6.2f}ms "
            f"[{mark}] "
            f"{r['query_short']}{style}"
        )

    print()
    print("-" * 100)
    print()

    # Summary statistics
    print("SUMMARY")
    print(f"  Accuracy:                 {correct_count}/{total} ({accuracy:.0%})")
    print(f"  Avg confidence (correct): {avg_correct_conf:.3f}")
    if incorrect_confs:
        print(f"  Avg confidence (wrong):   {avg_incorrect_conf:.3f}")
    else:
        print(f"  Avg confidence (wrong):   n/a (no misroutes)")
    print()

    # Timing
    avg_time = sum(timings) / len(timings)
    max_time = max(timings)
    min_time = min(timings)
    under_10 = sum(1 for t in timings if t < 10.0)
    print("TIMING")
    print(f"  Average:   {avg_time:.3f} ms per query")
    print(f"  Min:       {min_time:.3f} ms")
    print(f"  Max:       {max_time:.3f} ms")
    print(f"  Under 10ms: {under_10}/{total}")
    print()

    # Guna distribution
    guna_counts: dict[str, int] = {}
    for r in results:
        guna_counts[r["guna"]] = guna_counts.get(r["guna"], 0) + 1
    print("GUNA DISTRIBUTION (Processing Mode)")
    for g, c in sorted(guna_counts.items(), key=lambda x: -x[1]):
        bar = "#" * (c * 3)
        print(f"  {g:<8} {c:>2} queries  {bar}")
    print()

    # Misrouted queries (the interesting ones)
    misses = [r for r in results if not r["correct"]]
    if misses:
        print("MISROUTED QUERIES (these are interesting — not just failures)")
        print("-" * 90)
        for r in misses:
            print(f"  Query #{r['id']}: {r['query_short']}")
            print(f"    Expected: {r['expected']}")
            print(f"    Got:      {r['primary']} (score {r['primary_score']:.3f})")
            print(f"    Expected engine score: {r['expected_score']:.3f}")
            print(f"    Why expected: {r['why']}")
            # Show all scores for the misroute
            sorted_scores = sorted(r["all_scores"].items(), key=lambda x: -x[1])
            score_str = ", ".join(f"{n}={s:.3f}" for n, s in sorted_scores[:4])
            print(f"    All top scores: {score_str}")
            print()

        print("  ANALYSIS: Misrouted queries often reveal genuine ambiguity.")
        print("  A query about debugging (Vaisheshika) that routes to Samkhya")
        print("  might be correct — decomposition IS part of debugging.")
        print("  The architecture anticipates multi-engine activation for this reason.")
        print()
    else:
        print("NO MISROUTES — all 20 queries routed to the expected primary darshana.")
        print()

    # Per-darshana accuracy
    print("PER-DARSHANA ACCURACY")
    categories = ["NYAYA", "SAMKHYA", "YOGA", "VEDANTA", "MIMAMSA", "VAISHESHIKA"]
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_correct = sum(1 for r in cat_results if r["correct"])
        cat_total = len(cat_results)
        pct = (cat_correct / cat_total * 100) if cat_total > 0 else 0
        bar = "#" * int(pct / 5)
        print(f"  {cat:<14} {cat_correct}/{cat_total}  ({pct:5.1f}%)  {bar}")
    print()

    # Score heatmap
    print("SCORE HEATMAP (rows=queries, columns=engines)")
    engines = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]
    header = f"{'#':>2}  " + "  ".join(f"{e[:6]:>6}" for e in engines) + "   Expected"
    print(header)
    print("-" * len(header))
    for r in results:
        scores_str = "  ".join(
            f"{r['all_scores'].get(e, 0.0):>6.3f}" for e in engines
        )
        mark = " OK" if r["correct"] else " <<"
        print(f"{r['id']:>2}  {scores_str}   {r['expected']:<14}{mark}")
    print()

    # Final verdict
    print("=" * 100)
    if accuracy >= 0.9:
        print(f"  VERDICT: {accuracy:.0%} accuracy. The Buddhi layer discriminates well.")
    elif accuracy >= 0.7:
        print(f"  VERDICT: {accuracy:.0%} accuracy. Solid, with room for pattern tuning.")
    else:
        print(f"  VERDICT: {accuracy:.0%} accuracy. Patterns need refinement.")
    print("=" * 100)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_benchmark()
