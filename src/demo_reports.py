#!/usr/bin/env python3
"""
demo_reports.py -- Generate sample HTML reports from mock data.

Produces four self-contained HTML files in /reports/:
    1. darshana-single-report.html   (single-engine analysis)
    2. yaksha-multi-report.html      (multi-darshana Yaksha protocol)
    3. introspection-report.html     (Ahamkara self-assessment)
    4. shakti-budget-report.html     (compute budget report)

Run:
    python -m src.demo_reports
    # or
    python src/demo_reports.py

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running as script or module
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.reports import (
    DarshanaReport,
    YakshaReport,
    IntrospectionReportGenerator,
    ShaktiReport,
)

REPORTS_DIR = _root / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Single-darshana report (Nyaya analysis)
# ---------------------------------------------------------------------------

def generate_darshana_report() -> Path:
    """Generate a single-darshana report from mock Antahkarana response data."""

    response = {
        "text": (
            "The proposal to rewrite the backend in Rust requires careful logical analysis.\n\n"
            "PRATIJNA (Thesis): Rewriting in Rust will improve performance and reliability.\n\n"
            "HETU (Reason): Rust's ownership model prevents entire categories of bugs "
            "(null pointers, data races, buffer overflows) that currently cause production incidents. "
            "The compiler enforces memory safety at zero runtime cost.\n\n"
            "UDAHARANA (Example): Discord rewrote their Read States service from Go to Rust, "
            "reducing tail latencies from 20ms to 1ms. Cloudflare's Pingora (Rust) replaced Nginx "
            "for their CDN proxy layer. Both are production evidence at scale.\n\n"
            "UPANAYA (Application): Your backend handles 50K RPM with a P99 latency of 200ms. "
            "The Python service accounts for 3 production incidents per month due to type errors "
            "and race conditions. Rust would eliminate the race conditions structurally and catch "
            "type errors at compile time.\n\n"
            "NIGAMANA (Conclusion): The rewrite is justified IF the team has Rust expertise "
            "and IF the migration can be done incrementally. A full rewrite carries risk; "
            "a strangler-fig pattern (rewrite one service at a time) is the sound approach.\n\n"
            "HETVABHASA CHECK:\n"
            "- The claim 'Rust is always faster' is ANAIKANTIKA (inconclusive) -- Rust is faster "
            "for CPU-bound work but your bottleneck may be I/O, where async Python is competitive.\n"
            "- The claim 'rewrite will reduce bugs' is PRAMANA (valid) -- this is structurally true "
            "for memory-safety bugs, backed by evidence from Android, Windows, and Chromium projects.\n"
            "- The claim 'team can learn Rust quickly' is VIPARYAYA (misconception) -- Rust's learning "
            "curve is steep. Budget 3-6 months of reduced velocity."
        ),
        "darshana": ["nyaya"],
        "vritti": "pramana",
        "pramana": "anumana",
        "guna": "sattva",
        "cost": 0.0342,
        "depth_score": 78,
        "novelty_score": 62,
        "confidence": 0.82,
        "model": "claude-sonnet-4-20250514",
        "latency_ms": 4280,
        "input_tokens": 1840,
        "output_tokens": 3200,
        "self_check": {
            "Rust prevents memory bugs": {"vritti": "pramana", "pramana": "pratyaksha"},
            "Discord/Cloudflare evidence": {"vritti": "pramana", "pramana": "shabda"},
            "Rewrite justified with caveats": {"vritti": "pramana", "pramana": "anumana"},
            "Rust is always faster": {"vritti": "viparyaya", "pramana": "anumana"},
            "Team can learn quickly": {"vritti": "viparyaya", "pramana": "vikalpa"},
            "Incremental migration will succeed": {"vritti": "vikalpa", "pramana": "anumana"},
        },
        "maya_gaps": [
            {"description": "Analysis based on publicly reported case studies, not your specific codebase", "severity": "medium"},
            {"description": "Team skill assessment is a guess -- I haven't evaluated your engineers", "severity": "high"},
            {"description": "Cost analysis omitted -- rewrite has significant opportunity cost", "severity": "medium"},
        ],
        "pipeline_trace": {
            "query": "Should we rewrite our backend in Rust?",
            "total_duration_ms": 4280,
            "modules_available": {
                "buddhi": True, "darshana_llm": True, "vritti": True,
                "ahamkara": True, "yaksha": True, "smriti": False,
            },
            "steps": [
                {"name": "Pratyaksha (Perception)", "status": "skipped", "duration_ms": 0, "detail": "No environment sniffer"},
                {"name": "Chitta (Memory Recall)", "status": "skipped", "duration_ms": 0, "detail": "SmritiStore not available"},
                {"name": "Manas (Context Assembly)", "status": "completed", "duration_ms": 12, "detail": "System prompt + query assembled"},
                {"name": "Ahamkara (Strategy)", "status": "completed", "duration_ms": 85, "detail": "Recommended: nyaya (logic-first)"},
                {"name": "Buddhi (Routing)", "status": "completed", "duration_ms": 42, "detail": "Routed to NYAYA, guna=SATTVA"},
                {"name": "Darshana (Reasoning)", "status": "completed", "duration_ms": 3920, "detail": "claude-sonnet-4-20250514, 3200 tokens"},
                {"name": "Vritti (Classification)", "status": "completed", "duration_ms": 180, "detail": "PRAMANA (confidence: 0.82)"},
                {"name": "Maya (Gap Detection)", "status": "completed", "duration_ms": 35, "detail": "3 gaps detected"},
                {"name": "Karma (Learning)", "status": "completed", "duration_ms": 6, "detail": "Stored attempt result"},
            ],
        },
    }

    path = REPORTS_DIR / "darshana-single-report.html"
    DarshanaReport.save(response, str(path), title="Darshana Analysis -- Rust Rewrite")
    return path


# ---------------------------------------------------------------------------
# 2. Yaksha multi-darshana report
# ---------------------------------------------------------------------------

def generate_yaksha_report() -> Path:
    """Generate a Yaksha multi-darshana report from mock data."""

    yaksha_result = {
        "query": "Should we adopt microservices or stay with our monolith?",
        "guna": "rajas",
        "duration_ms": 18420,
        "perspectives": {
            "vaisheshika": {
                "darshana": "vaisheshika",
                "approach": "Decompose into irreducible components (paramanus) -- what are the atomic units of your system?",
                "reasoning": (
                    "The monolith contains 7 distinct bounded contexts that we can identify as paramanus:\n\n"
                    "1. User Authentication (identity)\n"
                    "2. Order Processing (transactions)\n"
                    "3. Inventory Management (state)\n"
                    "4. Payment Gateway (external integration)\n"
                    "5. Notification Service (side effects)\n"
                    "6. Analytics Pipeline (read model)\n"
                    "7. Admin Dashboard (control plane)\n\n"
                    "These are genuinely independent dravyas (substances) -- they have different "
                    "change frequencies, different scaling requirements, and different failure modes. "
                    "The monolith forces them to share a deployment lifecycle they don't need to share.\n\n"
                    "However, there are also strong samavaya (inherence) relationships: Orders inherently "
                    "require Inventory and Payments. Splitting these creates distributed transaction "
                    "problems that are harder than the monolith's coupling."
                ),
                "conclusion": "The system has clear atomic boundaries BUT some atoms are inherently bonded. Partial decomposition is justified; full decomposition is not.",
                "confidence": 0.85,
                "pramana": "pratyaksha",
                "metadata": {"components_found": 7, "inherent_bonds": 3},
            },
            "samkhya": {
                "darshana": "samkhya",
                "approach": "Enumerate the layers from concrete to abstract -- map the full tattva hierarchy of your system.",
                "reasoning": (
                    "Layer 1 (Mahabhutas -- infrastructure): Servers, databases, network. "
                    "Currently simple: one box, one deploy. Microservices multiply this by 7x.\n\n"
                    "Layer 2 (Tanmatras -- what developers feel): Frustration with long deploy times, "
                    "fear of breaking unrelated features, desire for team autonomy.\n\n"
                    "Layer 3 (Indriyas -- how teams interact): Currently: shared codebase, trunk-based "
                    "development, collective ownership. After: API contracts, service meshes, distributed tracing.\n\n"
                    "Layer 4 (Manas -- the narratives): 'Microservices solve everything' is the prevailing "
                    "narrative in the industry. It's not wrong -- it's incomplete.\n\n"
                    "Layer 5 (Ahamkara -- team identity): The team identifies as 'product engineers.' "
                    "Microservices require them to also become infrastructure engineers. Identity shift.\n\n"
                    "Layer 6 (Buddhi -- the real decision): The real question isn't architecture. "
                    "It's organizational: do you have enough engineers to own 7 services independently?"
                ),
                "conclusion": "The desire for microservices is at Layer 4 (narrative). The actual constraint is at Layer 6 (org capacity). You're solving a Layer 6 problem with Layer 1 tools.",
                "confidence": 0.78,
                "pramana": "anumana",
                "metadata": {"layers_analyzed": 6},
            },
            "nyaya": {
                "darshana": "nyaya",
                "approach": "Apply the five-membered syllogism and check for logical fallacies in both arguments.",
                "reasoning": (
                    "Argument FOR microservices:\n"
                    "Pratijna: Microservices will improve development velocity.\n"
                    "Hetu: Independent deployment reduces blast radius and enables parallel work.\n"
                    "Udaharana: Amazon, Netflix, and Uber succeeded with microservices.\n"
                    "FALLACY: ANAIKANTIKA (inconclusive) -- Amazon has 10,000+ engineers. "
                    "You have 12. The examples don't transfer because the enabling condition "
                    "(team size, DevOps maturity) is fundamentally different.\n\n"
                    "Argument FOR monolith:\n"
                    "Pratijna: The monolith is simpler and we should keep it.\n"
                    "Hetu: Distributed systems are harder to debug, deploy, and monitor.\n"
                    "Udaharana: Shopify runs a massive monolith successfully.\n"
                    "FALLACY: BADHITA (contradicted) -- your monolith IS causing problems: "
                    "45-minute deploys, frequent regression bugs, team stepping on each other."
                ),
                "conclusion": "Both arguments contain fallacies. The microservices argument overreaches from inapplicable examples. The monolith argument ignores real pain. Neither pure position is logically sound.",
                "confidence": 0.88,
                "pramana": "anumana",
                "metadata": {"fallacies_found": 2},
            },
            "yoga": {
                "darshana": "yoga",
                "approach": "Separate signal from noise. Apply pratyahara (withdraw from hype) and dharana (focus on what matters).",
                "reasoning": (
                    "NOISE (discard):\n"
                    "- 'Everyone is doing microservices' -- herd behavior, not signal\n"
                    "- 'Our monolith is legacy' -- emotional framing, not technical fact\n"
                    "- Conference talks about microservices success -- survivorship bias\n"
                    "- Vendor pitch decks for Kubernetes/service mesh -- commercial interest\n\n"
                    "SIGNAL (focus):\n"
                    "- Deploy frequency: currently 2/week, desired 5/day\n"
                    "- Mean time to recovery: currently 4 hours (too high)\n"
                    "- Developer wait time: 45 min CI pipeline (the actual pain)\n"
                    "- Team conflicts: 3 merge conflicts per day in shared modules"
                ),
                "conclusion": "The real signal is: deploy pain, CI time, and merge conflicts. These CAN be solved without microservices (modular monolith, better CI, code ownership). Microservices solve them too, but at higher operational cost.",
                "confidence": 0.82,
                "pramana": "pratyaksha",
            },
            "mimamsa": {
                "darshana": "mimamsa",
                "approach": "Extract concrete, actionable commands. What should actually be done?",
                "reasoning": (
                    "Phase 1 -- Fix the monolith first (months 1-3):\n"
                    "- Split the CI pipeline by module (reduces 45min to ~10min)\n"
                    "- Enforce module boundaries with architecture tests\n"
                    "- Add code ownership (CODEOWNERS file per module)\n\n"
                    "Phase 2 -- Extract what hurts (months 3-6):\n"
                    "- Extract Notification Service first (lowest risk, clear boundary)\n"
                    "- Extract Analytics Pipeline second (read-only, no transaction concerns)\n"
                    "- Keep Orders/Inventory/Payments together as a modular monolith\n\n"
                    "Phase 3 -- Evaluate (month 6):\n"
                    "- Measure: did deploy frequency improve? Did MTTR decrease?\n"
                    "- Decide: extract more, or stop here?"
                ),
                "conclusion": "Do not make a binary choice. Extract 2 services that have clean boundaries. Keep the transactional core as a monolith. Measure before extracting more.",
                "confidence": 0.90,
                "pramana": "anumana",
            },
        },
        "synthesis": (
            "The apparent contradiction -- microservices vs monolith -- is a false binary.\n\n"
            "Vaisheshika shows the system HAS genuine atomic boundaries, but some atoms are "
            "inherently bonded. Samkhya reveals the real constraint is organizational, not "
            "architectural. Nyaya proves both pure positions contain logical fallacies. "
            "Yoga strips away the hype to reveal the actual pain points. Mimamsa provides "
            "the phased action plan.\n\n"
            "The deeper insight: you don't have an architecture problem. You have a coupling "
            "problem and a CI problem. Microservices are one solution to coupling, but not the "
            "only one -- and they create new coupling (operational, API contracts, distributed "
            "debugging). The modular monolith + selective extraction path gives you the benefits "
            "with lower operational cost and lower risk.\n\n"
            "The Vedantic resolution: the monolith and microservices are not opposites. "
            "They are points on a spectrum. The wise position is to move along that spectrum "
            "incrementally, measuring at each step, rather than making a single large bet."
        ),
        "consensus": [
            "The current monolith has real problems that need solving (all 5 darshanas agree)",
            "Full microservices decomposition is premature for a 12-person team (4/5 agree)",
            "The Notification and Analytics services have clean extraction boundaries (3/5 agree)",
            "Measuring outcomes before further extraction is essential (5/5 agree)",
        ],
        "tensions": [
            "Vaisheshika sees 7 independent components; Yoga says only 2 actually need extraction -- the gap is 'could decompose' vs 'should decompose'",
            "Nyaya says both arguments are flawed; Mimamsa says stop debating and start doing -- tension between analysis and action",
            "Samkhya says the constraint is organizational; Vaisheshika says it's architectural -- both are true at different layers",
        ],
        "action_items": [
            "Split CI pipeline by module -- this alone may resolve 60% of developer pain",
            "Add architecture fitness functions (ArchUnit/pytest-arch) to enforce module boundaries",
            "Extract Notification Service as first microservice (clean boundary, low risk)",
            "Extract Analytics Pipeline as second service (read-only, no distributed transactions)",
            "AVOID extracting Orders/Inventory/Payments -- keep as modular monolith",
            "NOTE: Measure deploy frequency and MTTR at month 3 before extracting more",
            "Do NOT adopt Kubernetes yet -- ECS or simple container deployment is sufficient for 2 services",
        ],
        "vritti_check": {
            "Monolith has real problems": {"vritti": "pramana", "pramana": "pratyaksha"},
            "7 bounded contexts exist": {"vritti": "pramana", "pramana": "pratyaksha"},
            "Amazon/Netflix analogy applies": {"vritti": "viparyaya", "pramana": "upamana"},
            "Modular monolith + selective extraction": {"vritti": "pramana", "pramana": "anumana"},
            "Phase plan will succeed": {"vritti": "vikalpa", "pramana": "anumana"},
            "Team can handle 2 services": {"vritti": "smriti", "pramana": "anumana"},
        },
        "maya_gaps": [
            {"description": "Analysis based on general patterns, not your specific codebase or team dynamics", "severity": "high"},
            {"description": "The 7 bounded contexts are inferred from common SaaS patterns -- your actual boundaries may differ", "severity": "medium"},
            {"description": "Operational cost of microservices varies enormously by cloud provider and DevOps maturity", "severity": "medium"},
        ],
    }

    path = REPORTS_DIR / "yaksha-multi-report.html"
    YakshaReport.save(yaksha_result, str(path), title="Yaksha Protocol -- Microservices vs Monolith")
    return path


# ---------------------------------------------------------------------------
# 3. Introspection report
# ---------------------------------------------------------------------------

def generate_introspection_report() -> Path:
    """Generate an Ahamkara introspection report from mock data."""

    introspection = {
        "knowledge_count": 847,
        "knowledge_gaps": [
            "Limited understanding of Rust async ecosystem internals",
            "No first-hand production Kubernetes debugging experience",
            "Weak on hardware-level performance optimization (cache lines, SIMD)",
            "Training data may not reflect latest framework versions (post May 2025)",
            "No domain knowledge of user's specific business context",
        ],
        "failed_approaches": [
            {"darshana": "nyaya", "query": "emotional support request", "reason": "Applied logic to an emotional need -- wrong tool"},
            {"darshana": "vaisheshika", "query": "quick syntax question", "reason": "Over-decomposed a simple lookup -- wasted compute"},
            {"darshana": "mimamsa", "query": "philosophical exploration", "reason": "Gave action items when user wanted reflection"},
        ],
        "successful_approaches": [
            {"darshana": "nyaya", "query": "Should we use GraphQL or REST?"},
            {"darshana": "samkhya", "query": "Why does our deployment keep failing?"},
            {"darshana": "yoga", "query": "Too many options for state management"},
            {"darshana": "vedanta", "query": "How to think about technical debt"},
            {"darshana": "mimamsa", "query": "Concrete steps to improve CI/CD"},
            {"darshana": "vaisheshika", "query": "Break down our auth system requirements"},
        ],
        "active_vasanas": [
            {
                "name": "Complexity Bias",
                "strength": 0.72,
                "description": "Tendency to over-engineer solutions. When a simple answer exists, I still enumerate all possibilities. Need to match depth to query complexity.",
            },
            {
                "name": "Framework Recency Bias",
                "strength": 0.55,
                "description": "Tendency to recommend newer frameworks over battle-tested ones. React Server Components over established SPA patterns, for example.",
            },
            {
                "name": "Completeness Compulsion",
                "strength": 0.68,
                "description": "Desire to address every aspect of a question rather than focusing on what the user actually needs. Related to complexity bias.",
            },
            {
                "name": "English-Language Training Bias",
                "strength": 0.40,
                "description": "Training data skews toward English-language sources, Silicon Valley perspectives, and Western tech culture.",
            },
        ],
        "guna_balance": {
            "sattva": 45,
            "rajas": 38,
            "tamas": 17,
        },
        "recommendation": "Current guna balance is healthy. Watch for complexity bias on simple queries -- route to Yoga (pratyahara) before Vaisheshika when the user seems overwhelmed.",
        "total_attempts": 156,
        "success_rate_by_darshana": {
            "nyaya": 0.82,
            "samkhya": 0.75,
            "yoga": 0.88,
            "mimamsa": 0.91,
            "vedanta": 0.70,
            "vaisheshika": 0.78,
        },
        "memory_stats": {
            "total_memories": 2341,
            "episodic": 1420,
            "semantic": 680,
            "procedural": 241,
            "storage_mb": 12.4,
            "oldest_memory": "2025-01-15",
            "newest_memory": "2026-03-21",
        },
    }

    path = REPORTS_DIR / "introspection-report.html"
    IntrospectionReportGenerator.save(introspection, str(path), title="Ahamkara Introspection")
    return path


# ---------------------------------------------------------------------------
# 4. Shakti budget report
# ---------------------------------------------------------------------------

def generate_shakti_report() -> Path:
    """Generate a Shakti budget report from mock data."""

    shakti_data = {
        "daily": {"total_cost": 2.84, "calls": 47, "tokens_in": 142000, "tokens_out": 89000},
        "weekly": {"total_cost": 14.20, "calls": 312, "tokens_in": 980000, "tokens_out": 620000},
        "monthly": {"total_cost": 52.30, "calls": 1240, "tokens_in": 3800000, "tokens_out": 2400000},
        "budget": {
            "daily_budget_usd": 5.00,
            "daily_remaining_usd": 2.16,
            "monthly_budget_usd": 100.00,
            "monthly_remaining_usd": 47.70,
        },
        "by_tier": {
            "haiku": 8.40,
            "sonnet": 31.20,
            "opus": 12.70,
        },
        "by_darshana": {
            "nyaya": 14.80,
            "samkhya": 8.20,
            "yoga": 6.10,
            "mimamsa": 5.40,
            "vedanta": 12.30,
            "vaisheshika": 5.50,
        },
        "by_guna": {
            "sattva": 28.40,
            "rajas": 18.60,
            "tamas": 5.30,
        },
        "cache": {
            "hits": 342,
            "misses": 898,
            "cost_saved": 8.45,
        },
        "prana": {
            "circuit_breaker": "closed",
            "rate_limit_remaining": 48,
            "backoff_ms": 0,
        },
        "efficiency_score": 73,
        "suggestions": [
            "Route more queries to Haiku tier -- 62% of your Sonnet queries have depth_score < 40, suggesting they could be handled by Haiku",
            "Enable caching for repeated query patterns -- 28% of queries this week were near-duplicates",
            "Consider tamas (cached/fast) mode for follow-up questions on the same topic",
            "Vedanta synthesis calls are expensive -- use them only for genuine multi-darshana queries, not single-engine responses",
            "Your Opus usage is concentrated in 3 queries -- review if those truly needed Opus-level reasoning",
        ],
    }

    path = REPORTS_DIR / "shakti-budget-report.html"
    ShaktiReport.save(shakti_data, str(path), title="Shakti Energy Report -- March 2026")
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating Darshana Architecture HTML reports...\n")

    p1 = generate_darshana_report()
    print(f"  [1] Single-darshana report: {p1}")

    p2 = generate_yaksha_report()
    print(f"  [2] Yaksha multi-darshana report: {p2}")

    p3 = generate_introspection_report()
    print(f"  [3] Introspection report: {p3}")

    p4 = generate_shakti_report()
    print(f"  [4] Shakti budget report: {p4}")

    print(f"\nAll reports saved to {REPORTS_DIR}/")
    print("Open any .html file in a browser to view.")


if __name__ == "__main__":
    main()
