#!/usr/bin/env python3
"""
demo_ahamkara.py — Demonstrating the Self-Model Layer
======================================================

This demo shows what no current AI system has: structured self-awareness.
Not consciousness — functional self-reference. The system tracks what it
knows, what it has tried, what biases it carries, and uses all of that
to strategize before answering new queries.

Run: python3 demo_ahamkara.py

No API key needed. No external dependencies. Pure self-model.
"""

import json
import os
import sys
import time

# Ensure we can import from src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ahamkara import Ahamkara


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def banner(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def section(title: str) -> None:
    print(f"\n--- {title} ---\n")


def pp(obj, indent: int = 2) -> None:
    """Pretty-print dicts/lists."""
    if isinstance(obj, (dict, list)):
        print(json.dumps(obj, indent=indent, default=str))
    else:
        print(obj)


# ---------------------------------------------------------------------------
# DEMO 1: Building up knowledge over interactions
# ---------------------------------------------------------------------------

def demo_knowledge():
    banner("DEMO 1: KnowledgeMap — What Do I Know?")

    aham = Ahamkara()

    print("Registering knowledge from different pramanas (epistemic sources)...\n")

    # Knowledge from training data (shabda = testimony)
    aham.register_knowledge(
        "Python 3.12 introduced PEP 695 type parameter syntax",
        pramana="shabda", confidence=0.9,
        source="training", date="2023-10",
    )
    aham.register_knowledge(
        "Rust's ownership model prevents data races at compile time",
        pramana="shabda", confidence=0.95,
        source="training", date="2024-01",
    )

    # Knowledge from direct observation (pratyaksha)
    aham.register_knowledge(
        "User prefers direct communication without filler",
        pramana="pratyaksha", confidence=0.95,
        source="interaction",
    )
    aham.register_knowledge(
        "The auth module uses JWT tokens with 1-hour expiry",
        pramana="pratyaksha", confidence=0.99,
        source="code_reading",
    )

    # Knowledge from inference (anumana)
    aham.register_knowledge(
        "Auth failures are likely caused by token expiry based on timing pattern",
        pramana="anumana", confidence=0.7,
        source="log_analysis",
    )

    # Knowledge from analogy (upamana)
    aham.register_knowledge(
        "This microservice architecture resembles the Netflix Zuul pattern",
        pramana="upamana", confidence=0.5,
        source="pattern_matching",
    )

    print(f"Total knowledge claims: {len(aham.knowledge.all_claims())}\n")

    section("Querying knowledge about 'auth'")
    results = aham.query_knowledge("auth token JWT")
    for kc in results:
        print(f"  [{kc.pramana}] (conf: {kc.confidence:.2f}) {kc.claim}")

    section("Knowledge gaps for 'auth security'")
    gaps = aham.knowledge.knowledge_gaps("auth security vulnerabilities")
    for gap in gaps:
        print(f"  - {gap}")

    section("Knowledge gaps for 'database performance'")
    gaps = aham.knowledge.knowledge_gaps("database performance tuning")
    for gap in gaps:
        print(f"  - {gap}")

    print("\n[This is novel: the system knows what it DOESN'T know,")
    print(" structured by epistemic source, not just 'low confidence'.]")


# ---------------------------------------------------------------------------
# DEMO 2: Learning from failed attempts
# ---------------------------------------------------------------------------

def demo_attempts():
    banner("DEMO 2: AttemptLog — Learning From Failure")

    aham = Ahamkara()

    print("Recording a sequence of reasoning attempts...\n")

    # First attempt: try Nyaya (logic) for a debugging problem
    aham.record_attempt(
        query="debug the auth flow — users getting 401 after token refresh",
        darshana="nyaya",
        success=False,
        reason="formal logic alone couldn't identify the root cause; "
               "needed to decompose the auth pipeline first",
    )
    print("Attempt 1: nyaya on auth debugging -> FAILED")
    print("  Reason: needed decomposition, not formal logic\n")

    # Second attempt: try Samkhya (decomposition)
    aham.record_attempt(
        query="debug the auth flow — users getting 401 after token refresh",
        darshana="samkhya",
        success=True,
    )
    print("Attempt 2: samkhya on auth debugging -> SUCCESS\n")

    # More attempts to build history
    aham.record_attempt(
        query="is this caching strategy correct for high-traffic endpoints",
        darshana="nyaya",
        success=True,
    )
    aham.record_attempt(
        query="design a new notification system",
        darshana="vedanta",
        success=False,
        reason="too abstract — needed concrete action steps from mimamsa",
    )
    aham.record_attempt(
        query="design a new notification system",
        darshana="mimamsa",
        success=True,
    )
    aham.record_attempt(
        query="resolve conflict between REST and GraphQL approaches",
        darshana="vedanta",
        success=True,
    )

    section("Success rates by darshana")
    rates = aham.attempts.all_success_rates()
    for name, stats in rates.items():
        bar = "#" * int(stats["rate"] * 20) if stats["rate"] > 0 else ""
        print(f"  {name:<14} {stats['rate']:>5.0%}  ({stats['successes']}/{stats['total']})  {bar}")
        if stats["failure_reasons"]:
            for r in stats["failure_reasons"]:
                print(f"                 ^ failed: {r[:60]}...")

    section("Failed approaches (recent)")
    failed = aham.attempts.failed_approaches()
    for f in failed:
        print(f"  [{f['darshana']}] {f['query'][:50]}...")
        if f.get("reason"):
            print(f"    Reason: {f['reason'][:60]}...")

    print("\n[This is novel: the system remembers what reasoning STYLE failed,")
    print(" not just what question was asked. It learns which darshana to avoid.]")


# ---------------------------------------------------------------------------
# DEMO 3: Guna state shifting
# ---------------------------------------------------------------------------

def demo_guna():
    banner("DEMO 3: GunaState — Dynamic Processing Mode")

    aham = Ahamkara()

    print("The three gunas control HOW the system processes:\n")
    print("  sattva = precision, validation, low temperature")
    print("  rajas  = exploration, creativity, high temperature")
    print("  tamas  = retrieval, efficiency, cached patterns\n")

    # Start in balanced state
    aham.set_guna_state(sattva=0.33, rajas=0.34, tamas=0.33)
    print(f"Initial state: {aham.guna.current().to_dict()}\n")

    # Debugging task: shift to sattva
    section("Task: debugging -> recommending sattva shift")
    rec = aham.guna.recommend_shift("debugging")
    print(f"  Recommendation: {rec['recommendation']}")
    if rec["shifts"]:
        for guna, details in rec["shifts"].items():
            print(f"    {guna}: {details['current']:.2f} -> {details['recommended']:.2f} ({details['direction']})")

    aham.set_guna_state(sattva=0.7, rajas=0.15, tamas=0.15)
    print(f"\n  New state: {aham.guna.current().to_dict()}")

    # Creative task: shift to rajas
    section("Task: creative design -> recommending rajas shift")
    rec = aham.guna.recommend_shift("creative")
    print(f"  Recommendation: {rec['recommendation']}")
    if rec["shifts"]:
        for guna, details in rec["shifts"].items():
            print(f"    {guna}: {details['current']:.2f} -> {details['recommended']:.2f} ({details['direction']})")

    aham.set_guna_state(sattva=0.15, rajas=0.7, tamas=0.15)
    print(f"\n  New state: {aham.guna.current().to_dict()}")

    # FAQ lookup: shift to tamas
    section("Task: retrieval/FAQ -> recommending tamas shift")
    rec = aham.guna.recommend_shift("retrieval")
    print(f"  Recommendation: {rec['recommendation']}")

    print("\n[This is novel: the system explicitly manages its reasoning mode,")
    print(" rather than using one-size-fits-all generation for every task.]")


# ---------------------------------------------------------------------------
# DEMO 4: Vasana detection — "Am I biased?"
# ---------------------------------------------------------------------------

def demo_vasanas():
    banner("DEMO 4: VasanaTracker — Detecting My Own Biases")

    aham = Ahamkara()

    print("Building up vasanas through repeated experiences...\n")

    # Simulate a history of recommending Rust
    for _ in range(5):
        aham.vasanas.record(
            action="recommended Rust for systems task",
            outcome="success — user was satisfied",
            domain="language_recommendation",
        )
    aham.vasanas.record(
        action="recommended Rust for scripting task",
        outcome="failure — too complex, Python would have been better",
        domain="language_recommendation",
    )
    aham.vasanas.record(
        action="recommended Rust for web backend",
        outcome="success — but user said Go would have been simpler",
        domain="language_recommendation",
    )

    # Simulate preferring samkhya
    for _ in range(4):
        aham.vasanas.record(
            action="used samkhya for decomposition",
            outcome="success",
            domain="darshana_selection",
        )

    section("Active vasanas (accumulated biases)")
    active = aham.vasanas.active_vasanas()
    for v in active:
        strength_bar = "#" * int(abs(v["strength"]) * 20)
        print(f"  [{v['domain']}] '{v['tendency']}'")
        print(f"    Strength: {v['strength']:.3f} {strength_bar}")
        print(f"    Based on: {v['action_count']} experiences\n")

    section("Bias detection: checking a response")
    query = "What language should we use for this data pipeline?"
    response = ("I recommend using Rust for this data pipeline. Rust's ownership "
                "model and zero-cost abstractions make it ideal for high-throughput "
                "data processing. The type system will catch errors at compile time.")

    print(f"  Query:    {query}")
    print(f"  Response: {response[:70]}...")
    print()

    biases = aham.vasanas.detect_bias(query, response)
    if biases:
        for b in biases:
            print(f"  BIAS DETECTED (severity: {b['severity']:.2f}):")
            print(f"    {b['concern']}")
    else:
        print("  No biases detected.")

    section("Burning outdated vasanas (jnana-agni)")
    print("  Before burn:")
    pp(aham.vasanas.summary())

    result = aham.vasanas.jnana_agni(domain="language_recommendation")
    print(f"\n  Burned {result['burned']} samskaras from 'language_recommendation'")
    print("\n  After burn:")
    pp(aham.vasanas.summary())

    print("\n[This is novel: the system can detect when its own accumulated")
    print(" experience is creating a bias, and deliberately clear it.]")


# ---------------------------------------------------------------------------
# DEMO 5: Strategize — putting it all together
# ---------------------------------------------------------------------------

def demo_strategize():
    banner("DEMO 5: strategize() — Meta-Cognition Before Answering")

    # Build up a rich self-model
    aham = Ahamkara()

    # Knowledge
    aham.register_knowledge(
        "JWT tokens in our auth service expire after 1 hour",
        pramana="pratyaksha", confidence=0.99, source="code_reading",
    )
    aham.register_knowledge(
        "The refresh token endpoint has a race condition under load",
        pramana="anumana", confidence=0.65, source="log_analysis",
    )
    aham.register_knowledge(
        "OAuth2 PKCE flow prevents authorization code interception",
        pramana="shabda", confidence=0.85, source="training",
    )
    aham.register_knowledge(
        "User prefers pragmatic solutions over architecturally pure ones",
        pramana="pratyaksha", confidence=0.9, source="interaction",
    )

    # Attempt history
    aham.record_attempt(
        query="debug the auth flow",
        darshana="nyaya", success=False,
        reason="needed samkhya decomposition first",
    )
    aham.record_attempt(
        query="debug the auth flow",
        darshana="samkhya", success=True,
    )
    aham.record_attempt(
        query="fix token refresh race condition",
        darshana="vaisheshika", success=True,
    )
    aham.record_attempt(
        query="design new auth architecture",
        darshana="vedanta", success=False,
        reason="too abstract — user wanted concrete steps",
    )
    aham.record_attempt(
        query="design new auth architecture",
        darshana="mimamsa", success=True,
    )

    # Guna state: currently precision-oriented
    aham.set_guna_state(sattva=0.6, rajas=0.25, tamas=0.15)

    # Now strategize for a new query
    query = "How should we handle auth for the new mobile app?"

    section(f"Query: '{query}'")
    print("Consulting the self-model before reasoning...\n")

    strategy = aham.strategize(query)

    print("RELEVANT KNOWLEDGE:")
    if strategy.relevant_knowledge:
        for k in strategy.relevant_knowledge:
            print(f"  [{k['pramana']}] (conf: {k['confidence']:.2f}) {k['claim']}")
    else:
        print("  None found.")

    print("\nPAST ATTEMPTS ON SIMILAR QUERIES:")
    if strategy.past_attempts:
        for a in strategy.past_attempts:
            status = "SUCCESS" if a["success"] else "FAILED"
            print(f"  [{a['darshana']}] {status} — {a['query']}")
            if a.get("reason"):
                print(f"    Reason: {a['reason']}")
    else:
        print("  No similar attempts found.")

    print(f"\nSUGGESTED DARSHANA: {strategy.suggested_darshana}")
    print(f"  (Based on what worked for similar queries in the past)")

    print(f"\nSUGGESTED GUNA SHIFT:")
    rec = strategy.suggested_guna.get("recommendation", "")
    print(f"  {rec}")

    print(f"\nWARNINGS:")
    if strategy.warnings:
        for w in strategy.warnings:
            print(f"  ! {w}")
    else:
        print("  None.")

    print(f"\nSTRATEGY CONFIDENCE: {strategy.confidence:.1%}")

    print("\n[This is the breakthrough: BEFORE answering, the system consults")
    print(" its own history of knowledge, attempts, and biases to determine")
    print(" HOW to reason — not just WHAT to say.]")


# ---------------------------------------------------------------------------
# DEMO 6: Full introspection
# ---------------------------------------------------------------------------

def demo_introspect():
    banner("DEMO 6: introspect() — Full Self-Report")

    # Build a rich model
    aham = Ahamkara()

    # Register varied knowledge
    aham.register_knowledge("Python asyncio uses cooperative multitasking",
                            pramana="shabda", confidence=0.9, source="training")
    aham.register_knowledge("The database connection pool is set to 20",
                            pramana="pratyaksha", confidence=0.95, source="config_reading")
    aham.register_knowledge("Users report slowness during peak hours",
                            pramana="pratyaksha", confidence=0.8, source="user_report")
    aham.register_knowledge("Connection pool exhaustion may cause timeout errors",
                            pramana="anumana", confidence=0.6, source="hypothesis")

    # Record attempts
    aham.record_attempt("optimize database queries", "samkhya", True)
    aham.record_attempt("optimize database queries", "vaisheshika", True)
    aham.record_attempt("scale the API horizontally", "vedanta", False,
                        "too abstract for concrete scaling decisions")
    aham.record_attempt("scale the API horizontally", "mimamsa", True)
    aham.record_attempt("resolve ORM vs raw SQL debate", "vedanta", True)

    # Set guna
    aham.set_guna_state(sattva=0.5, rajas=0.3, tamas=0.2)

    # Build some vasanas
    for _ in range(3):
        aham.vasanas.record("used samkhya for decomposition", "success",
                            "darshana_preference")

    # Introspect
    report = aham.introspect()

    print(f"Knowledge claims:  {report.knowledge_count}")
    print(f"Total attempts:    {report.total_attempts}")
    print(f"Guna balance:      {report.guna_balance}")

    section("Knowledge Gaps")
    if report.knowledge_gaps:
        for gap in report.knowledge_gaps:
            print(f"  - {gap}")
    else:
        print("  None detected.")

    section("Success Rate by Darshana")
    for name, stats in report.success_rate_by_darshana.items():
        rate = stats.get("rate", 0)
        total = stats.get("total", 0)
        bar = "#" * int(rate * 20)
        print(f"  {name:<14} {rate:>5.0%} ({total} attempts) {bar}")

    section("Failed Approaches")
    for f in report.failed_approaches:
        print(f"  [{f['darshana']}] {f['query'][:50]}...")
        if f.get("reason"):
            print(f"    ^ {f['reason'][:60]}")

    section("Active Vasanas (Biases)")
    if report.active_vasanas:
        for v in report.active_vasanas:
            print(f"  '{v['tendency']}' (strength: {v['strength']:.3f})")
    else:
        print("  No strong biases detected.")

    section("Recommendation")
    print(f"  {report.recommendation}")

    print()
    print(f"  {aham}")

    print("\n[This is the Ahamkara: a complete self-portrait of the system's")
    print(" cognitive state, produced BEFORE it generates a single word of output.]")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  AHAMKARA (अहंकार) — The Self-Model Layer")
    print("  The Darshana Architecture for AGI")
    print()
    print("  अहम् (aham) = I  +  कार (kāra) = maker")
    print("  'The faculty that creates self-reference.'")
    print()
    print("  This is not ego. This is not consciousness.")
    print("  This is structured self-awareness — the system knowing")
    print("  what it knows, what it has tried, and what biases it carries.")
    print()

    demo_knowledge()
    demo_attempts()
    demo_guna()
    demo_vasanas()
    demo_strategize()
    demo_introspect()

    banner("What Makes This Novel")
    print("""  Current AI systems have:
    - Context windows (ephemeral, unstructured)
    - Fine-tuning (expensive, global, irreversible)
    - RAG (retrieval, but no self-model)

  The Ahamkara adds:
    - Epistemic provenance (HOW do I know this?)
    - Confidence decay (old knowledge fades)
    - Experiential memory (what reasoning worked before?)
    - Bias detection (am I being influenced by past tendencies?)
    - Meta-strategy (how should I THINK about this, before thinking?)

  No other AI system has a structured self-model.
  This is the Ahamkara. This is what was missing.
""")


if __name__ == "__main__":
    main()
