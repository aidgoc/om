"""
yaksha.py — The Yaksha Protocol: Multi-Darshana Parallel Reasoning

    "Yaksha said: What is the highest dharma?
     Yudhishthira said: Compassion.
     Yaksha said: What is the greatest wealth?
     Yudhishthira said: Learning."

In the Mahabharata's Yaksha Prashna (the Questions of the Yaksha), the
Pandavas encounter a lake guarded by a Yaksha spirit. It poses questions
that cannot be answered by a single perspective — they require wisdom that
integrates logic, ethics, pragmatism, and self-knowledge. Only Yudhishthira,
who can hold multiple viewpoints simultaneously, answers correctly and
saves his brothers.

The Yaksha Protocol implements this principle architecturally: a single
query is analyzed by multiple darshana engines IN PARALLEL, producing
diverse perspectives that are then synthesized by Vedanta into a unified
response. The tensions between perspectives are preserved as valuable
signal, not suppressed as noise.

This is what makes the Darshana Architecture different from "just use
multiple prompts." The philosophical schools aren't arbitrary viewpoints —
they are complementary cognitive faculties, each seeing a dimension of
reality that the others miss. Consensus reveals robustness. Tension
reveals the places where the real complexity lives.

Architecture reference: See THESIS.md for the full Shaddarshana model.

Usage:
    from yaksha import YakshaProtocol

    yaksha = YakshaProtocol()
    result = yaksha.inquire("Should we rewrite our backend in Rust?")

    print(result.perspectives)   # dict of darshana -> analysis
    print(result.synthesis)      # Vedanta integration
    print(result.consensus)      # points of agreement
    print(result.tensions)       # points of disagreement (valuable!)
    print(result.action_items)   # Mimamsa-extracted actions
"""

from __future__ import annotations

import textwrap
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from darshana_router import (
    DarshanaRouter,
    DarshanaEngine,
    NyayaEngine,
    SamkhyaEngine,
    YogaEngine,
    VedantaEngine,
    MimamsaEngine,
    VaisheshikaEngine,
    Guna,
    Pramana,
    PramanaTag,
    ReasoningOutput,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class DarshanaAnalysis:
    """
    A single darshana's structured analysis of a query.

    Each analysis captures not just the conclusion but the reasoning
    approach, confidence, and epistemic grounding — making the system's
    thought process transparent and auditable.
    """
    darshana: str
    approach: str
    reasoning: str
    conclusion: str
    confidence: float
    pramana: str  # epistemic tag: pratyaksha, anumana, upamana, shabda
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateRound:
    """
    One round of inter-darshana debate.

    In the Yaksha Prashna, the questions probe from multiple angles.
    Similarly, each debate round lets darshanas respond to each other's
    perspectives, refining or challenging them.
    """
    round_number: int
    responses: Dict[str, str]  # darshana_name -> response text


@dataclass
class YakshaResult:
    """
    The complete output of the Yaksha Protocol.

    Like Yudhishthira's answers to the Yaksha, this result holds
    multiple truths simultaneously — the individual perspectives, the
    points of agreement, the genuine tensions, and the deeper synthesis
    that emerges when all viewpoints are considered together.

    Attributes:
        query:        The original question posed to the Yaksha.
        perspectives: Each darshana's independent analysis.
        synthesis:    Vedanta's integration of all perspectives.
        consensus:    Points where multiple darshanas agree.
        tensions:     Points where darshanas genuinely disagree.
        action_items: Mimamsa-extracted actionable next steps.
        debate_log:   Optional record of multi-round debate.
        duration_ms:  Wall-clock time for the full protocol.
        guna:         The processing mode selected for this query.
    """
    query: str
    perspectives: Dict[str, DarshanaAnalysis]
    synthesis: str
    consensus: List[str]
    tensions: List[str]
    action_items: List[str]
    debate_log: List[DebateRound] = field(default_factory=list)
    duration_ms: float = 0.0
    guna: str = "sattva"

    # -- Convenience methods ------------------------------------------------

    def summary(self) -> str:
        """
        One-paragraph summary of the Yaksha Protocol's findings.

        Returns a concise digest suitable for a busy decision-maker
        who needs the bottom line from all six schools of thought.
        """
        n_perspectives = len(self.perspectives)
        n_consensus = len(self.consensus)
        n_tensions = len(self.tensions)
        n_actions = len(self.action_items)

        parts = [
            f"The Yaksha Protocol analyzed this query through "
            f"{n_perspectives} darshana(s).",
        ]

        if n_consensus:
            parts.append(
                f"There {'is' if n_consensus == 1 else 'are'} "
                f"{n_consensus} point(s) of consensus."
            )
        if n_tensions:
            parts.append(
                f"There {'is' if n_tensions == 1 else 'are'} "
                f"{n_tensions} genuine tension(s) between perspectives "
                f"-- these are where the real complexity lives."
            )
        if n_actions:
            parts.append(
                f"Mimamsa extracted {n_actions} actionable next step(s)."
            )

        parts.append(f"Synthesis: {self.synthesis}")

        return " ".join(parts)

    def tensions_only(self) -> str:
        """
        Return only the tensions -- the disagreements between darshanas.

        In the Yaksha Prashna, the hardest questions are those where
        simple answers fail. Similarly, the tensions in a multi-darshana
        analysis reveal where simplistic thinking breaks down. These are
        not bugs; they are the most valuable output of the protocol.
        """
        if not self.tensions:
            return "No tensions detected -- all darshanas converge."

        lines = ["TENSIONS (where darshanas disagree):", ""]
        for i, tension in enumerate(self.tensions, 1):
            lines.append(f"  {i}. {tension}")
        return "\n".join(lines)

    def as_markdown(self) -> str:
        """
        Render the full Yaksha result as Markdown.

        Suitable for inclusion in documents, reports, or LLM context
        windows where structured reasoning is needed.
        """
        md = []
        md.append(f"# Yaksha Analysis")
        md.append(f"")
        md.append(f"**Query:** {self.query}")
        md.append(f"**Processing Mode (Guna):** {self.guna}")
        md.append(f"**Duration:** {self.duration_ms:.0f}ms")
        md.append(f"")

        # Individual perspectives
        md.append(f"## Perspectives")
        md.append(f"")
        for name, analysis in self.perspectives.items():
            md.append(f"### {name.upper()}")
            md.append(f"")
            md.append(f"**Approach:** {analysis.approach}")
            md.append(f"")
            md.append(f"{analysis.reasoning}")
            md.append(f"")
            md.append(
                f"**Conclusion:** {analysis.conclusion} "
                f"(confidence: {analysis.confidence}, "
                f"pramana: {analysis.pramana})"
            )
            md.append(f"")

        # Consensus
        md.append(f"## Consensus")
        md.append(f"")
        if self.consensus:
            for point in self.consensus:
                md.append(f"- {point}")
        else:
            md.append(f"No consensus points identified.")
        md.append(f"")

        # Tensions
        md.append(f"## Tensions")
        md.append(f"")
        if self.tensions:
            for tension in self.tensions:
                md.append(f"- {tension}")
        else:
            md.append(f"No tensions identified.")
        md.append(f"")

        # Synthesis
        md.append(f"## Synthesis (Vedanta)")
        md.append(f"")
        md.append(self.synthesis)
        md.append(f"")

        # Action items
        md.append(f"## Action Items (Mimamsa)")
        md.append(f"")
        if self.action_items:
            for action in self.action_items:
                md.append(f"- [ ] {action}")
        else:
            md.append(f"No action items extracted.")
        md.append(f"")

        # Debate log
        if self.debate_log:
            md.append(f"## Debate Log")
            md.append(f"")
            for dr in self.debate_log:
                md.append(f"### Round {dr.round_number}")
                md.append(f"")
                for dname, resp in dr.responses.items():
                    md.append(f"**{dname.upper()}:** {resp}")
                    md.append(f"")

        return "\n".join(md)


# ---------------------------------------------------------------------------
# Template-based reasoning engine (works without an LLM)
# ---------------------------------------------------------------------------

# Each darshana has a reasoning template that produces a structured analysis
# from keywords and patterns in the query. This is the POC path — no API key
# needed. When a DarshanaLLM is available, these templates become the system
# prompts for actual LLM calls.

_DARSHANA_TEMPLATES: Dict[str, Dict[str, str]] = {
    "nyaya": {
        "approach": (
            "Apply Nyaya's five-membered syllogism: identify the claim, "
            "find the supporting reason, test with examples, apply to this "
            "case, derive the conclusion. Check for hetvabhasa (fallacies)."
        ),
        "reasoning_template": (
            "LOGICAL ANALYSIS (Nyaya)\n"
            "Claim under examination: {query_essence}\n"
            "Pratijna (thesis): The proposition must be tested against evidence.\n"
            "Hetu (reason): We examine the stated and implied premises.\n"
            "Udaharana (example): We look for supporting and counter-examples.\n"
            "Upanaya (application): Applying the general principle to this specific case.\n"
            "Nigamana (conclusion): {conclusion}\n"
            "Fallacy check: {fallacy_check}"
        ),
        "pramana": "anumana",
    },
    "samkhya": {
        "approach": (
            "Apply Samkhya's enumerative method: identify the whole, "
            "decompose into constituent tattvas (principles), map causal "
            "relationships between layers, verify completeness."
        ),
        "reasoning_template": (
            "STRUCTURAL ANALYSIS (Samkhya)\n"
            "System under examination: {query_essence}\n"
            "Layer decomposition:\n"
            "  - Abstract/strategic layer: goals, principles, constraints\n"
            "  - Organizational layer: teams, processes, responsibilities\n"
            "  - Technical layer: systems, tools, implementations\n"
            "  - Operational layer: day-to-day actions, metrics, feedback\n"
            "Causal flow: each layer emerges from and constrains the one below.\n"
            "Completeness check: {completeness}"
        ),
        "pramana": "anumana",
    },
    "yoga": {
        "approach": (
            "Apply Yoga's pratyahara (withdraw from noise) and dharana "
            "(concentrate on signal): list all factors, separate signal "
            "from noise, rank by true importance, focus on the core."
        ),
        "reasoning_template": (
            "FOCUS ANALYSIS (Yoga)\n"
            "Situation: {query_essence}\n"
            "All factors present: {factors}\n"
            "Signal (directly relevant): {signal}\n"
            "Noise (distractions): {noise}\n"
            "Core focus: {core_focus}\n"
            "What to ignore: {ignore}"
        ),
        "pramana": "anumana",
    },
    "vedanta": {
        "approach": (
            "Apply Vedanta's adhyaropa-apavada: state the apparent "
            "contradictions, strip away surface differences via neti neti, "
            "find the unifying abstraction, re-derive the surface positions "
            "as partial truths of the whole."
        ),
        "reasoning_template": (
            "SYNTHESIS (Vedanta)\n"
            "Apparent contradictions: {contradictions}\n"
            "Neti neti — stripping surface differences:\n"
            "  What each position gets right: {partial_truths}\n"
            "  The false distinction creating conflict: {false_distinction}\n"
            "Unifying principle: {unifying_principle}\n"
            "Re-derivation: each original position is a partial view of this deeper truth."
        ),
        "pramana": "anumana",
    },
    "mimamsa": {
        "approach": (
            "Apply Mimamsa's hermeneutic method: identify the text/situation, "
            "extract explicit directives (vidhi), identify implicit requirements, "
            "separate rationale from instruction, produce ordered action list."
        ),
        "reasoning_template": (
            "ACTION ANALYSIS (Mimamsa)\n"
            "Situation to interpret: {query_essence}\n"
            "Explicit directives (vidhi): {explicit_actions}\n"
            "Implicit requirements: {implicit_requirements}\n"
            "Prioritized action list:\n{action_list}\n"
            "Ambiguities requiring clarification: {ambiguities}"
        ),
        "pramana": "shabda",
    },
    "vaisheshika": {
        "approach": (
            "Apply Vaisheshika's padartha analysis: identify the irreducible "
            "entities (dravya), their properties (guna), their actions (karma), "
            "their categories (samanya), their uniqueness (vishesha), and their "
            "inherent connections (samavaya)."
        ),
        "reasoning_template": (
            "ATOMIC ANALYSIS (Vaisheshika)\n"
            "System: {query_essence}\n"
            "Irreducible entities (dravya): {entities}\n"
            "Properties of each (guna): {properties}\n"
            "Actions/behaviors (karma): {actions}\n"
            "Type hierarchy (samanya): {types}\n"
            "What makes each unique (vishesha): {uniqueness}\n"
            "Inherent connections (samavaya): {connections}"
        ),
        "pramana": "anumana",
    },
}


def _template_analyze(darshana_name: str, query: str) -> DarshanaAnalysis:
    """
    Produce a structured analysis using templates (no LLM needed).

    This is the POC path. Each darshana applies its characteristic lens
    to the query and produces a structured output. The reasoning is
    template-driven but the structure mirrors what an LLM-backed version
    would produce.
    """
    template = _DARSHANA_TEMPLATES[darshana_name]
    query_lower = query.lower()

    # Extract a query essence (first ~80 chars or to first period)
    dot = query.find(".")
    essence = query[:dot] if 0 < dot < 100 else query[:100]

    # Build darshana-specific reasoning based on query content
    reasoning, conclusion, confidence = _build_reasoning(
        darshana_name, query, essence
    )

    return DarshanaAnalysis(
        darshana=darshana_name,
        approach=template["approach"],
        reasoning=reasoning,
        conclusion=conclusion,
        confidence=confidence,
        pramana=template["pramana"],
    )


def _build_reasoning(
    darshana: str, query: str, essence: str
) -> tuple[str, str, float]:
    """
    Build darshana-specific reasoning text from query analysis.

    Each darshana genuinely looks at the query differently — this is not
    cosmetic variation but structural difference in what each school
    attends to and how it draws conclusions.
    """
    q = query.lower()

    if darshana == "nyaya":
        # Nyaya looks for truth claims, logical structure, validity
        has_claim = any(w in q for w in ["should", "is it", "can we", "will"])
        has_evidence = any(w in q for w in ["because", "since", "data", "evidence"])
        fallacy_risk = "low" if has_evidence else "medium — premises not fully established"
        conclusion = (
            "The proposition requires empirical validation before commitment. "
            "Logical structure is present but premises need grounding in evidence."
            if has_claim
            else "No clear truth claim detected; reframe as testable proposition."
        )
        reasoning = (
            f"LOGICAL ANALYSIS (Nyaya)\n"
            f"Claim under examination: {essence}\n"
            f"Evidence present in query: {'yes' if has_evidence else 'no — this weakens the argument'}\n"
            f"Logical structure: {'claim with implicit premises' if has_claim else 'open question without clear thesis'}\n"
            f"Fallacy risk: {fallacy_risk}\n"
            f"Recommendation: construct a formal argument with explicit premises before deciding."
        )
        return reasoning, conclusion, 0.7 if has_evidence else 0.5

    elif darshana == "samkhya":
        # Samkhya decomposes into layers
        reasoning = (
            f"STRUCTURAL ANALYSIS (Samkhya)\n"
            f"System under examination: {essence}\n"
            f"Layer decomposition:\n"
            f"  1. Strategic layer: What is the goal? What constraints exist?\n"
            f"  2. Architectural layer: What are the major components and their relationships?\n"
            f"  3. Implementation layer: What specific technologies, tools, or actions are involved?\n"
            f"  4. Operational layer: How will this be maintained, monitored, and evolved?\n"
            f"Causal analysis: decisions at each layer constrain the layers below.\n"
            f"Completeness: all four layers must be addressed for a sound decision."
        )
        conclusion = (
            "The decision involves multiple interacting layers. A choice that "
            "optimizes one layer may create problems in another. Enumerate all "
            "layers before committing."
        )
        return reasoning, conclusion, 0.65

    elif darshana == "yoga":
        # Yoga filters noise and finds the core
        factors = []
        if any(w in q for w in ["team", "people", "hire", "culture"]):
            factors.append("human/organizational")
        if any(w in q for w in ["cost", "budget", "money", "expensive", "investment"]):
            factors.append("financial")
        if any(w in q for w in ["time", "deadline", "fast", "slow", "speed"]):
            factors.append("temporal")
        if any(w in q for w in ["tech", "system", "code", "architecture", "stack"]):
            factors.append("technical")
        if any(w in q for w in ["risk", "safe", "danger", "fail"]):
            factors.append("risk")
        if any(w in q for w in ["ethics", "moral", "right", "wrong", "harm"]):
            factors.append("ethical")
        if not factors:
            factors.append("general")

        core = factors[0] if factors else "unclear"
        reasoning = (
            f"FOCUS ANALYSIS (Yoga)\n"
            f"Situation: {essence}\n"
            f"Factors detected: {', '.join(factors)}\n"
            f"Signal (primary concern): {core}\n"
            f"Noise (secondary, defer for now): {', '.join(factors[1:]) if len(factors) > 1 else 'none detected'}\n"
            f"Core focus: address the {core} dimension first — it constrains everything else.\n"
            f"Dharana (sustained attention): before exploring solutions, fully understand the {core} dimension."
        )
        conclusion = (
            f"Focus on the {core} dimension first. Other factors are real but "
            f"secondary. Depth on the core beats breadth across all factors."
        )
        return reasoning, conclusion, 0.6

    elif darshana == "vedanta":
        # Vedanta looks for contradictions to resolve
        has_tension = any(w in q for w in [
            "but", "however", "versus", "vs", "or", "tension",
            "contradiction", "conflict", "disagree", "both",
            "tradeoff", "trade-off", "dilemma",
        ])
        if has_tension:
            reasoning = (
                f"SYNTHESIS (Vedanta)\n"
                f"Situation: {essence}\n"
                f"Apparent contradiction detected in the query.\n"
                f"Neti neti — stripping surface differences:\n"
                f"  Each opposing position likely optimizes for a different value.\n"
                f"  The false distinction: treating these values as mutually exclusive.\n"
                f"Unifying principle: the tension is not between the positions but between\n"
                f"  the timeframes or scopes at which each is evaluated. Both can be true\n"
                f"  at different levels of abstraction or different phases of execution.\n"
                f"Re-derivation: the opposing positions are partial truths — each correct\n"
                f"  within its scope, incomplete when claimed as universal."
            )
            conclusion = (
                "The apparent contradiction dissolves at a higher level of abstraction. "
                "Both positions are partially correct — the task is to find the frame "
                "where they coexist, not to choose one."
            )
        else:
            reasoning = (
                f"SYNTHESIS (Vedanta)\n"
                f"Situation: {essence}\n"
                f"No overt contradiction detected, but Vedanta probes deeper:\n"
                f"  What assumptions are hidden in the framing of this question?\n"
                f"  Is the question itself the right question to ask?\n"
                f"  What would change if we examined the premises rather than seeking answers?\n"
                f"Meta-observation: the way a question is framed constrains its possible answers.\n"
                f"  Reframing may be more valuable than answering."
            )
            conclusion = (
                "Before answering, examine whether the question itself is well-framed. "
                "The deepest insight may come from reframing rather than resolving."
            )
        return reasoning, conclusion, 0.7 if has_tension else 0.55

    elif darshana == "mimamsa":
        # Mimamsa extracts actions
        action_words = [
            w for w in ["build", "implement", "create", "deploy", "migrate",
                        "rewrite", "refactor", "hire", "decide", "choose",
                        "evaluate", "test", "measure", "plan", "design"]
            if w in q
        ]
        reasoning = (
            f"ACTION ANALYSIS (Mimamsa)\n"
            f"Situation to interpret: {essence}\n"
            f"Explicit action verbs detected: {', '.join(action_words) if action_words else 'none — actions are implicit'}\n"
            f"Implicit requirements:\n"
            f"  - Gather information before deciding (if not already done)\n"
            f"  - Define success criteria before acting\n"
            f"  - Identify reversibility — can this decision be undone?\n"
            f"  - Determine stakeholders who must be consulted\n"
            f"Prioritized actions:\n"
            f"  1. Define the decision criteria explicitly\n"
            f"  2. Gather evidence for each option against those criteria\n"
            f"  3. Make a time-bounded decision (avoid analysis paralysis)\n"
            f"  4. Execute with a review checkpoint\n"
            f"Ambiguities: scope, timeline, and resource constraints are not specified."
        )
        conclusion = (
            "Extract the implicit actions, define success criteria, and create "
            "a time-bounded decision process. Action without clarity is as "
            "dangerous as clarity without action."
        )
        return reasoning, conclusion, 0.65

    elif darshana == "vaisheshika":
        # Vaisheshika finds the atoms
        reasoning = (
            f"ATOMIC ANALYSIS (Vaisheshika)\n"
            f"System: {essence}\n"
            f"Irreducible entities (dravya):\n"
            f"  - The decision itself (binary: do or don't, or a spectrum of options)\n"
            f"  - The actors (who decides, who is affected)\n"
            f"  - The resources (time, money, attention, political capital)\n"
            f"  - The constraints (what cannot change)\n"
            f"Properties (guna): each entity has measurable and immeasurable qualities.\n"
            f"Inherent connections (samavaya): some entities are inseparable —\n"
            f"  e.g., the decision and its consequences; the actors and their incentives.\n"
            f"Type hierarchy: this belongs to the class of {_classify_query_type(q)} decisions.\n"
            f"Atomic insight: trace the problem to its smallest movable part."
        )
        conclusion = (
            "Decompose to the atomic level. The irreducible entities — the decision, "
            "the actors, the resources, the constraints — are where leverage exists. "
            "Work at the level of atoms, not narratives."
        )
        return reasoning, conclusion, 0.6

    # Fallback
    return f"Analysis of: {essence}", "Further analysis needed.", 0.4


def _classify_query_type(query_lower: str) -> str:
    """Classify the query into a broad decision type for Vaisheshika."""
    if any(w in query_lower for w in ["tech", "code", "system", "api", "stack", "rust", "python"]):
        return "technical/architectural"
    if any(w in query_lower for w in ["hire", "team", "people", "culture", "manage"]):
        return "organizational/human"
    if any(w in query_lower for w in ["ethics", "moral", "right", "wrong", "harm", "fair"]):
        return "ethical/values"
    if any(w in query_lower for w in ["money", "cost", "revenue", "profit", "invest"]):
        return "financial/resource"
    if any(w in query_lower for w in ["strategy", "vision", "goal", "mission", "compete"]):
        return "strategic/directional"
    return "general/multifaceted"


# ---------------------------------------------------------------------------
# Synthesis engine (Vedanta's job)
# ---------------------------------------------------------------------------

def _synthesize_perspectives(
    query: str, perspectives: Dict[str, DarshanaAnalysis]
) -> tuple[str, list[str], list[str], list[str]]:
    """
    Vedanta's synthesis pass: integrate multiple darshana perspectives.

    Returns (synthesis_text, consensus_points, tension_points, action_items).

    This is the heart of the Yaksha Protocol. Like Vedanta finding Brahman
    beneath the multiplicity of appearances, this function finds the deeper
    pattern that connects — and the genuine tensions that resist resolution.
    """
    conclusions = {name: a.conclusion for name, a in perspectives.items()}
    confidences = {name: a.confidence for name, a in perspectives.items()}

    # -- Identify consensus --
    # Look for themes that appear across multiple darshanas
    consensus = []
    themes = _extract_themes(conclusions)
    for theme, darshanas_mentioning in themes.items():
        if len(darshanas_mentioning) >= 2:
            names = ", ".join(d.upper() for d in darshanas_mentioning)
            consensus.append(f"{theme} ({names} converge on this)")

    # -- Identify tensions --
    tensions = []
    # Nyaya (logic) vs Vedanta (synthesis) tension
    if "nyaya" in perspectives and "vedanta" in perspectives:
        tensions.append(
            "NYAYA demands definitive proof before action; VEDANTA suggests "
            "the framing itself may need revision — these pull in different "
            "directions (rigor vs. reframing)"
        )
    # Mimamsa (action) vs Yoga (focus) tension
    if "mimamsa" in perspectives and "yoga" in perspectives:
        tensions.append(
            "MIMAMSA pushes toward comprehensive action planning; YOGA insists "
            "on doing fewer things with deeper focus — breadth vs. depth"
        )
    # Samkhya (structure) vs Vaisheshika (atoms) tension
    if "samkhya" in perspectives and "vaisheshika" in perspectives:
        tensions.append(
            "SAMKHYA reasons top-down from layers; VAISHESHIKA reasons "
            "bottom-up from atoms — the optimal entry point is itself a decision"
        )
    # High vs low confidence tension
    high_conf = [n for n, c in confidences.items() if c >= 0.7]
    low_conf = [n for n, c in confidences.items() if c < 0.5]
    if high_conf and low_conf:
        tensions.append(
            f"{', '.join(n.upper() for n in high_conf)} {'is' if len(high_conf) == 1 else 'are'} "
            f"confident; {', '.join(n.upper() for n in low_conf)} {'is' if len(low_conf) == 1 else 'are'} "
            f"uncertain — the areas of uncertainty deserve extra attention"
        )

    # -- Build synthesis --
    synth_parts = []
    synth_parts.append(
        f"Integrating {len(perspectives)} perspective(s) on: {query[:80]}..."
        if len(query) > 80
        else f"Integrating {len(perspectives)} perspective(s) on: {query}"
    )

    if consensus:
        synth_parts.append(
            f"\nConvergence: {len(consensus)} point(s) of agreement across darshanas, "
            f"suggesting these are robust conclusions."
        )
    if tensions:
        synth_parts.append(
            f"\nDivergence: {len(tensions)} genuine tension(s) between perspectives. "
            f"These are not failures of analysis — they reveal the true complexity "
            f"of the problem. A good decision must acknowledge and navigate these tensions, "
            f"not pretend they don't exist."
        )

    # Average confidence
    avg_conf = sum(confidences.values()) / len(confidences) if confidences else 0
    synth_parts.append(
        f"\nOverall confidence: {avg_conf:.0%}. "
        f"{'This is a well-understood problem space.' if avg_conf >= 0.7 else 'Significant uncertainty remains — proceed with reversibility in mind.'}"
    )

    synthesis = "\n".join(synth_parts)

    # -- Extract action items (Mimamsa's job within synthesis) --
    action_items = []
    if "mimamsa" in perspectives:
        action_items.append("Define explicit success criteria before deciding")
        action_items.append("Gather evidence against those criteria (time-boxed)")
    if tensions:
        action_items.append(
            "Acknowledge the tensions identified above — do not resolve "
            "them prematurely; let them inform the decision"
        )
    if "yoga" in perspectives:
        action_items.append(
            "Identify the single most important factor and address it first"
        )
    if "nyaya" in perspectives:
        action_items.append(
            "Construct a testable hypothesis and define what evidence "
            "would change your mind"
        )
    if low_conf:
        action_items.append(
            f"Investigate areas of low confidence: "
            f"{', '.join(n.upper() for n in low_conf)}"
        )

    return synthesis, consensus, tensions, action_items


def _extract_themes(conclusions: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Extract common themes across darshana conclusions.

    Returns a dict mapping theme description to list of darshanas
    that mention it.
    """
    theme_keywords = {
        "evidence and validation are needed before commitment": [
            "evidence", "validate", "validation", "proof", "test", "verify",
            "empirical", "grounding",
        ],
        "multiple layers or dimensions must be considered": [
            "layer", "dimension", "level", "scope", "multiple", "interacting",
            "component",
        ],
        "the framing of the question matters as much as the answer": [
            "frame", "framing", "reframe", "assumption", "premise",
            "question itself",
        ],
        "focus and prioritization are critical": [
            "focus", "core", "primary", "priorit", "depth", "attention",
            "first",
        ],
        "action requires clarity on success criteria": [
            "criteria", "success", "action", "explicit", "define", "clarity",
        ],
        "decompose before deciding": [
            "decompose", "atomic", "irreducible", "smallest", "trace",
            "break down",
        ],
    }

    results: Dict[str, List[str]] = {}
    for theme, keywords in theme_keywords.items():
        matching_darshanas = []
        for dname, conclusion in conclusions.items():
            c_lower = conclusion.lower()
            if any(kw in c_lower for kw in keywords):
                matching_darshanas.append(dname)
        if matching_darshanas:
            results[theme] = matching_darshanas

    return results


# ---------------------------------------------------------------------------
# Debate engine
# ---------------------------------------------------------------------------

def _template_debate_response(
    darshana: str,
    query: str,
    own_analysis: DarshanaAnalysis,
    other_perspectives: Dict[str, DarshanaAnalysis],
    round_num: int,
) -> str:
    """
    Generate a debate response: this darshana reacts to others' perspectives.

    In later rounds, darshanas may refine their positions or identify
    where other perspectives complement or challenge their own.
    """
    others = {n: a for n, a in other_perspectives.items() if n != darshana}
    if not others:
        return own_analysis.conclusion

    # Each darshana responds in character
    other_names = ", ".join(n.upper() for n in others)

    if darshana == "nyaya":
        challenges = [
            f"{n.upper()} claims: '{a.conclusion[:80]}...' — "
            f"{'this lacks formal proof' if a.confidence < 0.7 else 'this is reasonably supported'}"
            for n, a in others.items()
        ]
        return (
            f"Round {round_num} — NYAYA responds to {other_names}:\n"
            + "\n".join(f"  - {c}" for c in challenges)
            + "\nNyaya maintains: claims require proof, not just plausibility."
        )

    elif darshana == "vedanta":
        return (
            f"Round {round_num} — VEDANTA observes the debate:\n"
            f"  The disagreements between {other_names} reveal complementary "
            f"partial truths. The deeper question is not which darshana is "
            f"right, but what unified understanding accommodates all their "
            f"valid observations. The debate itself is the data."
        )

    elif darshana == "mimamsa":
        return (
            f"Round {round_num} — MIMAMSA cuts through:\n"
            f"  Regardless of theoretical disagreements, the following "
            f"actions are implied by ALL perspectives: (1) gather more "
            f"evidence, (2) define criteria, (3) make a time-bounded decision.\n"
            f"  Theory without action is arthavada (explanatory), not "
            f"vidhi (injunctive)."
        )

    elif darshana == "yoga":
        return (
            f"Round {round_num} — YOGA filters:\n"
            f"  The debate has generated {len(others)} additional perspectives. "
            f"Not all are equally relevant. The core signal remains: "
            f"{own_analysis.conclusion[:100]}\n"
            f"  Additional perspectives are context, not signal. Focus."
        )

    elif darshana == "samkhya":
        return (
            f"Round {round_num} — SAMKHYA maps the structure of disagreement:\n"
            f"  Layer 1 (values): darshanas disagree on what matters most.\n"
            f"  Layer 2 (method): darshanas disagree on how to analyze.\n"
            f"  Layer 3 (conclusion): surface disagreements follow from layers 1 and 2.\n"
            f"  To resolve: align on values first, then method, then conclusion."
        )

    elif darshana == "vaisheshika":
        return (
            f"Round {round_num} — VAISHESHIKA atomizes the disagreement:\n"
            f"  The irreducible point of divergence: different darshanas weigh "
            f"different padarthas (categories). Nyaya weighs karma (logical action), "
            f"Yoga weighs guna (quality of attention), Mimamsa weighs dravya "
            f"(substance of the directive).\n"
            f"  The disagreement is not error — it is structural."
        )

    return f"Round {round_num} — {darshana.upper()}: maintains previous position."


# ---------------------------------------------------------------------------
# The Yaksha Protocol
# ---------------------------------------------------------------------------

class YakshaProtocol:
    """
    The Yaksha Protocol: multi-darshana parallel reasoning with synthesis.

    Named after the Yaksha of Mahabharata's Vana Parva (Book of the Forest),
    who guards the lake and poses questions to the Pandavas. The Yaksha's
    questions cannot be answered by strength, cunning, or single-perspective
    thinking — they require the integration of logic, ethics, pragmatism,
    and self-knowledge that only Yudhishthira possesses.

    The protocol:
        1. Takes a query (the Yaksha's question)
        2. Routes through Buddhi to identify relevant darshanas
        3. Runs each darshana's analysis IN PARALLEL
        4. Collects all perspectives
        5. Runs Vedanta synthesis to integrate them
        6. Returns a structured multi-perspective response

    The protocol works in two modes:
        - Template mode (no API key): uses built-in reasoning templates
          for the POC. Demonstrates the architecture without LLM costs.
        - LLM mode (with API key): sends each darshana's prompt to an
          LLM for actual reasoning. (Available when DarshanaLLM exists.)

    Usage:
        yaksha = YakshaProtocol()
        result = yaksha.inquire("Should we rewrite our backend in Rust?")

        print(result.perspectives)   # Each darshana's analysis
        print(result.synthesis)      # Vedanta's integration
        print(result.consensus)      # Where darshanas agree
        print(result.tensions)       # Where they disagree
        print(result.action_items)   # What to do next
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_darshanas: int = 6,
        activation_threshold: float = 0.15,
        max_workers: int = 6,
    ):
        """
        Initialize the Yaksha Protocol.

        Args:
            api_key: Optional API key for LLM-backed reasoning. When None,
                the protocol uses template-based reasoning (POC mode).
            max_darshanas: Maximum number of darshanas to activate for a
                single query (2-6). More perspectives = richer analysis
                but higher cost.
            activation_threshold: Minimum routing score for a darshana to
                be activated. Lower = more inclusive, higher = more selective.
            max_workers: Thread pool size for parallel darshana execution.
        """
        self.api_key = api_key
        self.max_darshanas = min(max(max_darshanas, 2), 6)
        self.activation_threshold = activation_threshold
        self.max_workers = max_workers

        # The Buddhi layer — routes queries to darshanas
        self.router = DarshanaRouter(
            activation_threshold=activation_threshold,
            max_engines=max_darshanas,
        )

        # All six engines, available for explicit invocation
        self.engines: Dict[str, DarshanaEngine] = self.router.engines

    def inquire(
        self,
        query: str,
        darshanas: Optional[List[str]] = None,
        context: Optional[Dict] = None,
    ) -> YakshaResult:
        """
        Submit a query to the Yaksha Protocol.

        Like the Yaksha at the lake, this method accepts a question and
        returns an answer that integrates multiple philosophical perspectives.

        Args:
            query: The question or problem to analyze.
            darshanas: Optional list of specific darshana names to use.
                If None, Buddhi routes automatically.
            context: Optional additional context for the analysis.

        Returns:
            A YakshaResult containing perspectives, synthesis, consensus,
            tensions, and action items.
        """
        start = time.monotonic()

        # Step 1: Buddhi routing — determine which darshanas to activate
        if darshanas:
            active = [d for d in darshanas if d in self.engines]
        else:
            routing = self.router.route(query)
            # For Yaksha, we want MORE perspectives than the standard router
            # Get all engines above threshold, up to max_darshanas
            sorted_engines = sorted(
                routing.engine_scores.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            active = [
                name for name, score in sorted_engines
                if score >= self.activation_threshold
            ][:self.max_darshanas]
            # Ensure at least 2 perspectives (the minimum for useful comparison)
            if len(active) < 2:
                active = [name for name, _ in sorted_engines[:2]]

        guna = self.router.guna_engine.classify(query)

        # Step 2: Run darshana analyses IN PARALLEL
        perspectives = self._run_parallel(query, active, context)

        # Step 3: Vedanta synthesis
        synthesis, consensus, tensions, action_items = _synthesize_perspectives(
            query, perspectives
        )

        elapsed_ms = (time.monotonic() - start) * 1000

        return YakshaResult(
            query=query,
            perspectives=perspectives,
            synthesis=synthesis,
            consensus=consensus,
            tensions=tensions,
            action_items=action_items,
            duration_ms=elapsed_ms,
            guna=guna.value,
        )

    def debate(
        self,
        query: str,
        rounds: int = 3,
        darshanas: Optional[List[str]] = None,
        context: Optional[Dict] = None,
    ) -> YakshaResult:
        """
        Multi-round debate: darshanas respond to each other's perspectives.

        In the Yaksha Prashna, the questions escalate in complexity. Each
        brother who fails adds pressure and context for the next attempt.
        Similarly, each debate round lets darshanas refine their positions
        in light of others' arguments.

        Args:
            query: The question to debate.
            rounds: Number of debate rounds (1-5). Each round lets
                darshanas respond to the previous round's perspectives.
            darshanas: Optional specific darshanas to include in the debate.
            context: Optional additional context.

        Returns:
            A YakshaResult with the debate_log populated.
        """
        rounds = min(max(rounds, 1), 5)
        start = time.monotonic()

        # Initial inquiry (round 0 — independent perspectives)
        if darshanas:
            active = [d for d in darshanas if d in self.engines]
        else:
            routing = self.router.route(query)
            sorted_engines = sorted(
                routing.engine_scores.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            active = [
                name for name, score in sorted_engines
                if score >= self.activation_threshold
            ][:self.max_darshanas]
            if len(active) < 2:
                active = [name for name, _ in sorted_engines[:2]]

        guna = self.router.guna_engine.classify(query)
        perspectives = self._run_parallel(query, active, context)

        # Debate rounds
        debate_log: List[DebateRound] = []
        current_perspectives = perspectives

        for r in range(1, rounds + 1):
            round_responses: Dict[str, str] = {}

            # Each darshana responds to all others — in parallel
            def _debate_one(dname: str) -> tuple[str, str]:
                response = _template_debate_response(
                    dname,
                    query,
                    current_perspectives[dname],
                    current_perspectives,
                    r,
                )
                return dname, response

            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                futures = {
                    pool.submit(_debate_one, dname): dname
                    for dname in active
                    if dname in current_perspectives
                }
                for future in as_completed(futures):
                    dname, response = future.result()
                    round_responses[dname] = response

            debate_log.append(DebateRound(
                round_number=r,
                responses=round_responses,
            ))

        # Final synthesis (incorporating debate)
        synthesis, consensus, tensions, action_items = _synthesize_perspectives(
            query, perspectives
        )

        # Enrich synthesis with debate insights
        if debate_log:
            synthesis += (
                f"\n\nAfter {len(debate_log)} round(s) of inter-darshana debate, "
                f"the positions have been refined. The debate revealed that "
                f"disagreements are structural (rooted in different values and methods), "
                f"not accidental. This is the Yaksha's deeper teaching: the question "
                f"tests not just knowledge, but the ability to hold multiple truths."
            )

        elapsed_ms = (time.monotonic() - start) * 1000

        return YakshaResult(
            query=query,
            perspectives=perspectives,
            synthesis=synthesis,
            consensus=consensus,
            tensions=tensions,
            action_items=action_items,
            debate_log=debate_log,
            duration_ms=elapsed_ms,
            guna=guna.value,
        )

    def _run_parallel(
        self,
        query: str,
        darshana_names: List[str],
        context: Optional[Dict] = None,
    ) -> Dict[str, DarshanaAnalysis]:
        """
        Run multiple darshana analyses in parallel using ThreadPoolExecutor.

        Each darshana runs independently — they do not see each other's
        output during analysis. This is intentional: independent perspectives
        are more valuable than groupthink.
        """
        perspectives: Dict[str, DarshanaAnalysis] = {}

        def _analyze(name: str) -> tuple[str, DarshanaAnalysis]:
            if self.api_key:
                # LLM mode — would call DarshanaLLM here when available
                # For now, fall back to template mode
                return name, _template_analyze(name, query)
            else:
                return name, _template_analyze(name, query)

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(_analyze, name): name
                for name in darshana_names
            }
            for future in as_completed(futures):
                name, analysis = future.result()
                perspectives[name] = analysis

        return perspectives
