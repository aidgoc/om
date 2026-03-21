#!/usr/bin/env python3
"""
demo_yaksha.py — The Yaksha Protocol in action

    "The Yaksha asked: What is heavier than the earth?
     Yudhishthira said: A mother.
     The Yaksha asked: What is taller than the sky?
     Yudhishthira said: A father.
     The Yaksha asked: What is faster than the wind?
     Yudhishthira said: The mind."

        — Mahabharata, Vana Parva (Yaksha Prashna)

This demo runs three scenarios through the Yaksha Protocol, showing
how multiple darshanas analyze the same question in parallel and how
Vedanta synthesizes their perspectives into a unified response.

All three demos run WITHOUT an API key — using the template-based
reasoning engine built into the POC.

Run:
    cd /Users/harsh/om/src && python3 demo_yaksha.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from yaksha import YakshaProtocol, YakshaResult

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

HEAVY = "=" * 76
LIGHT = "-" * 76
THIN = "-" * 40


def banner(title: str) -> None:
    print(f"\n{HEAVY}")
    print(f"  {title}")
    print(HEAVY)


def section(title: str) -> None:
    print(f"\n  {title}")
    print(f"  {LIGHT[:len(title) + 4]}")


def subsection(title: str) -> None:
    print(f"\n    {title}")
    print(f"    {THIN[:len(title) + 4]}")


def indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line for line in text.split("\n"))


def print_result(result: YakshaResult) -> None:
    """Print a YakshaResult in a structured, readable format."""

    section(f"BUDDHI ROUTING  |  {len(result.perspectives)} darshana(s) activated  |  guna: {result.guna}  |  {result.duration_ms:.0f}ms")

    # Individual perspectives
    for name, analysis in result.perspectives.items():
        subsection(f"{name.upper()} (confidence: {analysis.confidence}, pramana: {analysis.pramana})")
        print()
        print(f"    Approach: {analysis.approach[:120]}...")
        print()
        print(indent(analysis.reasoning, "      "))
        print()
        print(f"    >> Conclusion: {analysis.conclusion}")

    # Consensus
    section("CONSENSUS (where darshanas agree)")
    if result.consensus:
        for i, point in enumerate(result.consensus, 1):
            print(f"    {i}. {point}")
    else:
        print("    No consensus points — all perspectives diverge.")

    # Tensions
    section("TENSIONS (where darshanas disagree — this is VALUABLE)")
    if result.tensions:
        for i, tension in enumerate(result.tensions, 1):
            print(f"    {i}. {tension}")
    else:
        print("    No tensions detected.")

    # Synthesis
    section("VEDANTA SYNTHESIS")
    print(indent(result.synthesis, "    "))

    # Action items
    section("ACTION ITEMS (Mimamsa)")
    if result.action_items:
        for i, action in enumerate(result.action_items, 1):
            print(f"    {i}. {action}")
    else:
        print("    No action items extracted.")

    # Debate log (if present)
    if result.debate_log:
        section(f"DEBATE LOG ({len(result.debate_log)} rounds)")
        for dr in result.debate_log:
            subsection(f"Round {dr.round_number}")
            for dname, response in dr.responses.items():
                print(indent(response, "      "))
                print()


# ---------------------------------------------------------------------------
# Demo 1: Business Decision
# ---------------------------------------------------------------------------

def demo_business_decision(yaksha: YakshaProtocol) -> None:
    banner(
        "DEMO 1: BUSINESS DECISION\n"
        "  \"Should we pivot from B2B to B2C?\""
    )
    print()
    print("  Context: A SaaS startup with 50 B2B customers is considering")
    print("  a pivot to B2C. The team is split. Revenue is stable but growth")
    print("  has plateaued. The CEO wants multiple perspectives before deciding.")
    print()

    query = (
        "Should we pivot our SaaS product from B2B to B2C? "
        "We have 50 enterprise customers generating stable revenue but growth has "
        "plateaued. Our product has consumer appeal and the B2C market is 100x larger, "
        "but we'd need to rebuild our sales motion, redesign the UX, and hire differently. "
        "The team is split — engineers want the technical challenge, sales fears losing "
        "existing revenue, and the board wants faster growth. "
        "What should we do?"
    )

    # Use 4 specific darshanas for a focused analysis
    result = yaksha.inquire(
        query,
        darshanas=["nyaya", "samkhya", "yoga", "mimamsa"],
    )

    print(f"\n  Query: \"{query[:100]}...\"")
    print_result(result)


# ---------------------------------------------------------------------------
# Demo 2: Technical Architecture (with tensions highlighted)
# ---------------------------------------------------------------------------

def demo_technical_architecture(yaksha: YakshaProtocol) -> None:
    banner(
        "DEMO 2: TECHNICAL ARCHITECTURE\n"
        "  \"Should we rewrite our backend in Rust?\""
    )
    print()
    print("  Context: A Python backend serving 10M requests/day is hitting")
    print("  performance limits. Some engineers advocate for a Rust rewrite.")
    print("  Others say optimize the Python. The tensions are the point.")
    print()

    query = (
        "Should we rewrite our Python backend in Rust? The system handles 10 million "
        "requests per day and we're hitting CPU and memory limits. P99 latency is 800ms "
        "but the SLA requires 200ms. Half the team says rewrite in Rust for 10x performance; "
        "half says optimize the Python (caching, async, algorithmic improvements) for 3x "
        "at a fraction of the cost and risk. Both sides have valid evidence. "
        "This is a high-stakes technical architecture decision that affects the next 3 years."
    )

    # Use 5 darshanas — this is a rich technical decision that benefits
    # from structural (samkhya), atomic (vaisheshika), logical (nyaya),
    # synthesis (vedanta), and action (mimamsa) perspectives
    result = yaksha.inquire(
        query,
        darshanas=["nyaya", "samkhya", "vaisheshika", "vedanta", "mimamsa"],
    )

    print(f"\n  Query: \"{query[:100]}...\"")
    print_result(result)

    # Highlight tensions specifically
    print()
    section("TENSIONS DEEP DIVE (the most valuable output)")
    print()
    print(indent(result.tensions_only(), "    "))
    print()


# ---------------------------------------------------------------------------
# Demo 3: Ethical Dilemma (with debate)
# ---------------------------------------------------------------------------

def demo_ethical_dilemma(yaksha: YakshaProtocol) -> None:
    banner(
        "DEMO 3: ETHICAL DILEMMA (with multi-round debate)\n"
        "  \"Should we deploy AI that replaces 200 jobs?\""
    )
    print()
    print("  Context: An AI system can automate work currently done by 200")
    print("  employees. It will save the company $15M/year and improve quality.")
    print("  But those 200 people will lose their livelihoods. The darshanas")
    print("  genuinely disagree on this — and that disagreement is the point.")
    print()

    query = (
        "Should we deploy an AI system that automates work currently done by 200 "
        "employees? The system will save $15M per year and reduce error rates by 80%. "
        "But 200 people will lose their jobs in a region with limited alternatives. "
        "Some can be retrained, but not all. The board says deploy, the ethics committee "
        "says pause, the employees are terrified, and competitors will deploy if we don't. "
        "This is both a business decision and a moral one. What is the right thing to do?"
    )

    # Use all 6 darshanas with 3 rounds of debate
    result = yaksha.debate(
        query,
        rounds=3,
        darshanas=["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"],
    )

    print(f"\n  Query: \"{query[:100]}...\"")
    print_result(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print(HEAVY)
    print("  THE YAKSHA PROTOCOL")
    print("  Multi-Darshana Parallel Reasoning with Vedanta Synthesis")
    print()
    print("    \"The Yaksha asked: What is the greatest wonder?")
    print("     Yudhishthira said: Every day, people see others die,")
    print("     yet they live as though they are immortal.\"")
    print()
    print("        -- Mahabharata, Vana Parva")
    print(HEAVY)
    print()
    print("  This demo runs three scenarios through the Yaksha Protocol,")
    print("  showing how Hindu philosophy's six schools of thought analyze")
    print("  the same query in parallel and reveal both consensus and tension.")
    print()
    print("  No API key required. Template-based reasoning for the POC.")
    print()

    yaksha = YakshaProtocol()

    demo_business_decision(yaksha)
    demo_technical_architecture(yaksha)
    demo_ethical_dilemma(yaksha)

    # Final reflection
    banner("THE YAKSHA'S TEACHING")
    print()
    print("  The Yaksha Protocol is what makes the Darshana Architecture")
    print("  genuinely different from 'just use multiple prompts.'")
    print()
    print("  Three things set it apart:")
    print()
    print("  1. PHILOSOPHICAL GROUNDING. The six darshanas are not arbitrary")
    print("     viewpoints -- they are complementary cognitive faculties refined")
    print("     over 5,000 years. Each sees a dimension of reality the others miss.")
    print()
    print("  2. TENSIONS AS SIGNAL. When darshanas disagree, the protocol")
    print("     preserves the disagreement as valuable information. The places")
    print("     where perspectives conflict are exactly where the real complexity")
    print("     lives. Suppressing disagreement is suppressing signal.")
    print()
    print("  3. SYNTHESIS, NOT AVERAGING. Vedanta does not average the perspectives")
    print("     or vote. It finds the deeper pattern that EXPLAINS why they")
    print("     disagree -- then derives a unified understanding that holds all")
    print("     the partial truths simultaneously.")
    print()
    print("  This is how Yudhishthira answered the Yaksha: not by being")
    print("  smarter than his brothers, but by being able to hold multiple")
    print("  truths at once without flinching.")
    print()
    print("  See THESIS.md for the full architecture.")
    print("  See yaksha.py for the implementation.")
    print()


if __name__ == "__main__":
    main()
