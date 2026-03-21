"""
ahamkara.py — The Self-Model Layer of the Darshana Architecture
================================================================

In Samkhya philosophy, Ahamkara (अहंकार) = अहम् (aham, I) + कार (kāra, maker).
It is the faculty that creates self-reference — the capacity to say "I know",
"I tried", "I failed", "I am biased."

This is NOT ego in the Western psychological sense. It is a functional self-model:
a structured representation of the system's own cognitive state that enables
introspection, strategic reasoning, and honest self-assessment.

No current AI system has this. LLMs have context windows — ephemeral, unstructured,
and without any representation of their own epistemic state. The Ahamkara is
structured self-awareness: what do I know, what have I tried, what biases am I
carrying, and what should I try next?

The Ahamkara layer sits between Buddhi (fast discrimination) and the Shaddarshana
engines (specialized reasoners). It provides:

    KnowledgeMap   — what the system knows, tagged with pramana and confidence
    AttemptLog     — what reasoning has been tried and what worked
    GunaState      — current processing balance (sattva/rajas/tamas)
    VasanaTracker  — accumulated biases, inherited from KarmaStore
    introspect()   — full self-report across all subsystems
    strategize()   — pre-query analysis that uses history to recommend approach

Architecture reference: THESIS.md, Ahamkara Layer section.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import json
import math
import re
import time
from dataclasses import dataclass, field, asdict
from difflib import SequenceMatcher
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Import from siblings — KarmaStore is the foundation of VasanaTracker
# ---------------------------------------------------------------------------

try:
    from vritti_filter import KarmaStore, Samskara
except ImportError:
    from src.vritti_filter import KarmaStore, Samskara


# ---------------------------------------------------------------------------
# Enums (reuse Pramana from router if available, else define locally)
# ---------------------------------------------------------------------------

class Pramana(Enum):
    """The four valid means of knowledge from Nyaya epistemology."""
    PRATYAKSHA = "pratyaksha"   # direct perception / observation
    ANUMANA    = "anumana"      # inference
    UPAMANA    = "upamana"      # analogy
    SHABDA     = "shabda"       # testimony / authority


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeClaim:
    """
    A single thing the system knows (or believes it knows).

    Every claim is tagged with:
    - pramana: HOW it was derived (the epistemological source)
    - confidence: how certain the system is (0.0 to 1.0)
    - source: where it came from (training, interaction, tool, etc.)
    - registered_at: when it was recorded (epoch seconds)
    - date: optional human-readable date of the knowledge itself
    - domain: auto-extracted topic domain for retrieval
    """
    claim: str
    pramana: str
    confidence: float
    source: str
    registered_at: float = field(default_factory=time.time)
    date: Optional[str] = None
    domain: str = ""

    def age_days(self) -> float:
        """How many days since this knowledge was registered."""
        return (time.time() - self.registered_at) / 86400

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "pramana": self.pramana,
            "confidence": round(self.confidence, 4),
            "source": self.source,
            "registered_at": self.registered_at,
            "date": self.date,
            "domain": self.domain,
        }

    @classmethod
    def from_dict(cls, d: dict) -> KnowledgeClaim:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Attempt:
    """
    A record of the system trying a reasoning approach on a query.

    This is the experiential memory of the Ahamkara. Over time, the system
    builds a map of what works and what doesn't — not through retraining,
    but through structured reflection on its own attempts.
    """
    query: str
    darshana: str
    success: bool
    reason: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    query_type: str = ""  # auto-classified

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Attempt:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class GunaBalance:
    """
    The three gunas as a probability distribution over processing modes.

    sattva + rajas + tamas must equal 1.0 (within floating-point tolerance).

    This is not a metaphysical claim. It is a structured way to represent
    the system's current operational mode:
      - sattva-dominant: precision mode, careful validation
      - rajas-dominant: exploration mode, creative generation
      - tamas-dominant: retrieval mode, cached patterns
    """
    sattva: float = 0.33
    rajas: float = 0.34
    tamas: float = 0.33

    def dominant(self) -> str:
        vals = {"sattva": self.sattva, "rajas": self.rajas, "tamas": self.tamas}
        return max(vals, key=vals.get)  # type: ignore

    def to_dict(self) -> dict:
        return {"sattva": round(self.sattva, 3),
                "rajas": round(self.rajas, 3),
                "tamas": round(self.tamas, 3),
                "dominant": self.dominant()}


@dataclass
class IntrospectionReport:
    """
    The output of Ahamkara.introspect() — a full self-assessment.

    This is what makes the Ahamkara novel: no AI system produces a structured
    report of its own epistemic state, cognitive biases, and strategic
    recommendations before answering a query.
    """
    knowledge_count: int = 0
    knowledge_gaps: List[str] = field(default_factory=list)
    failed_approaches: List[dict] = field(default_factory=list)
    successful_approaches: List[dict] = field(default_factory=list)
    active_vasanas: List[dict] = field(default_factory=list)
    guna_balance: dict = field(default_factory=dict)
    recommendation: str = ""
    total_attempts: int = 0
    success_rate_by_darshana: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Strategy:
    """
    The output of Ahamkara.strategize(query) — a pre-query battle plan.

    Before the system even begins reasoning about a new query, the Ahamkara
    consults its knowledge map, attempt history, and vasana tracker to
    produce a strategy. This is meta-cognition: thinking about how to think.
    """
    query: str = ""
    relevant_knowledge: List[dict] = field(default_factory=list)
    past_attempts: List[dict] = field(default_factory=list)
    suggested_darshana: str = ""
    suggested_guna: dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# KnowledgeMap — what do I know?
# ---------------------------------------------------------------------------

class KnowledgeMap:
    """
    Tracks what the system knows, with epistemic provenance.

    Every piece of knowledge is tagged with its pramana (how it was derived),
    confidence level, source, and timestamp. Knowledge decays over time —
    old information from training data loses confidence, while recent
    observations maintain theirs.

    This is the Pramana Tagger from the architecture, but operating at the
    system level rather than the claim level: not "how was this sentence
    derived?" but "what does this system know, and how well does it know it?"
    """

    def __init__(self) -> None:
        self._claims: List[KnowledgeClaim] = []

    def register(
        self,
        claim: str,
        pramana: str = "shabda",
        confidence: float = 0.5,
        source: str = "unknown",
        date: Optional[str] = None,
    ) -> KnowledgeClaim:
        """
        Register a knowledge claim.

        Args:
            claim: The knowledge statement.
            pramana: One of pratyaksha, anumana, upamana, shabda.
            confidence: 0.0 to 1.0, how certain.
            source: Where this came from (training, interaction, tool, etc.).
            date: Optional date string for the knowledge itself.

        Returns:
            The created KnowledgeClaim.
        """
        domain = self._extract_domain(claim)
        kc = KnowledgeClaim(
            claim=claim,
            pramana=pramana,
            confidence=max(0.0, min(1.0, confidence)),
            source=source,
            date=date,
            domain=domain,
        )
        self._claims.append(kc)
        return kc

    def query_knowledge(self, topic: str, min_confidence: float = 0.1) -> List[KnowledgeClaim]:
        """
        Find knowledge claims relevant to a topic.

        Uses word overlap similarity to find relevant claims.
        Returns claims sorted by relevance * confidence (descending).
        """
        topic_lower = topic.lower()
        topic_words = set(re.findall(r'\w+', topic_lower))

        scored: List[Tuple[float, KnowledgeClaim]] = []
        for kc in self._claims:
            if kc.confidence < min_confidence:
                continue
            claim_words = set(re.findall(r'\w+', kc.claim.lower()))
            # Combine word overlap with sequence matching for better relevance
            overlap = len(topic_words & claim_words) / max(len(topic_words | claim_words), 1)
            seq_sim = SequenceMatcher(None, topic_lower, kc.claim.lower()).ratio()
            relevance = 0.6 * overlap + 0.4 * seq_sim
            if relevance > 0.1:
                scored.append((relevance * kc.confidence, kc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [kc for _, kc in scored]

    def knowledge_gaps(self, topic: str) -> List[str]:
        """
        Identify what is NOT known about a topic.

        This is the inverse of query_knowledge: given a topic, what aspects
        does the system have no knowledge about? Uses the topic's words to
        check for coverage gaps.

        Returns a list of gap descriptions.
        """
        relevant = self.query_knowledge(topic, min_confidence=0.0)
        if not relevant:
            return [f"No knowledge registered about '{topic}' at all."]

        # Check what aspects of the topic are covered
        topic_words = set(re.findall(r'\w+', topic.lower()))
        covered_words: set = set()
        for kc in relevant:
            covered_words.update(re.findall(r'\w+', kc.claim.lower()))

        # Stopwords to ignore
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "has", "have", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "can", "shall", "i", "we",
            "you", "it", "this", "that", "what", "how", "why", "when",
            "where", "which", "who", "with", "from", "to", "in", "on",
            "at", "for", "of", "by", "about", "not", "no", "and", "or",
        }
        uncovered = topic_words - covered_words - stopwords

        gaps = []
        if uncovered:
            gaps.append(f"No knowledge covering these aspects: {', '.join(sorted(uncovered))}")

        # Check for low-confidence areas
        low_conf = [kc for kc in relevant if kc.confidence < 0.5]
        if low_conf:
            gaps.append(
                f"{len(low_conf)} claim(s) with low confidence (<0.5) — "
                f"knowledge may be unreliable"
            )

        # Check for stale knowledge
        stale = [kc for kc in relevant if kc.age_days() > 30]
        if stale:
            gaps.append(
                f"{len(stale)} claim(s) older than 30 days — may be outdated"
            )

        # Check pramana distribution — over-reliance on shabda is a gap
        pramana_counts: Dict[str, int] = {}
        for kc in relevant:
            pramana_counts[kc.pramana] = pramana_counts.get(kc.pramana, 0) + 1
        total = sum(pramana_counts.values())
        shabda_ratio = pramana_counts.get("shabda", 0) / max(total, 1)
        if shabda_ratio > 0.8 and total > 1:
            gaps.append(
                f"{shabda_ratio:.0%} of knowledge is from testimony (shabda) — "
                f"no direct observation or inference to corroborate"
            )

        if not gaps:
            gaps.append(f"Topic '{topic}' appears well-covered, but verify recency.")
        return gaps

    def decay_confidence(self, half_life_days: float = 30.0) -> int:
        """
        Apply exponential decay to confidence based on age.

        Knowledge from pratyaksha (direct observation) decays slower than
        knowledge from shabda (testimony/training), because observations
        are more reliable than second-hand information.

        Args:
            half_life_days: Days for confidence to halve. Default 30.

        Returns:
            Number of claims whose confidence was reduced.
        """
        decay_multipliers = {
            "pratyaksha": 0.5,   # decays at half the rate (more durable)
            "anumana": 0.8,
            "upamana": 1.0,
            "shabda": 1.2,       # decays faster (less reliable over time)
        }
        affected = 0
        for kc in self._claims:
            age = kc.age_days()
            if age <= 0:
                continue
            multiplier = decay_multipliers.get(kc.pramana, 1.0)
            effective_half_life = half_life_days / max(multiplier, 0.01)
            decay_factor = math.pow(0.5, age / effective_half_life)
            new_conf = kc.confidence * decay_factor
            if abs(new_conf - kc.confidence) > 0.001:
                kc.confidence = max(new_conf, 0.01)  # never fully zero
                affected += 1
        return affected

    def all_claims(self) -> List[KnowledgeClaim]:
        """Return all registered claims."""
        return list(self._claims)

    @staticmethod
    def _extract_domain(claim: str) -> str:
        """Extract a rough domain/topic from a claim string."""
        # Take the first meaningful noun phrase as the domain
        words = re.findall(r'\b[A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+)?\b', claim)
        stopwords = {
            "the", "a", "an", "is", "are", "has", "have", "can", "will",
            "this", "that", "user", "prefers", "with", "for", "about",
        }
        for w in words:
            if w.lower() not in stopwords and len(w) > 2:
                return w.lower()
        return "general"

    def to_list(self) -> List[dict]:
        return [kc.to_dict() for kc in self._claims]

    def load_from_list(self, data: List[dict]) -> None:
        self._claims = [KnowledgeClaim.from_dict(d) for d in data]


# ---------------------------------------------------------------------------
# AttemptLog — what have I tried?
# ---------------------------------------------------------------------------

class AttemptLog:
    """
    Tracks what reasoning approaches have been tried, and what worked.

    This is experiential memory — not knowledge about the world, but
    knowledge about the system's own performance. Over time, the AttemptLog
    builds a map of which darshana engines work best for which types of
    problems, enabling the strategize() method to make informed recommendations.

    The query_type is auto-classified from the query text using simple
    heuristics (logic, decomposition, creative, interpretation, etc.).
    """

    # Heuristic patterns for classifying query types
    _TYPE_PATTERNS: List[Tuple[str, str]] = [
        (r"\b(debug|fix|error|bug|issue|broken|wrong)\b", "debugging"),
        (r"\b(prove|valid|logic|argument|fallacy|true|false)\b", "logic"),
        (r"\b(break down|decompose|components|layers|architecture|structure)\b", "decomposition"),
        (r"\b(create|design|build|new|novel|innovative|brainstorm)\b", "creative"),
        (r"\b(interpret|meaning|intent|extract|parse|understand)\b", "interpretation"),
        (r"\b(contradict|reconcile|unify|synthesize|paradox)\b", "synthesis"),
        (r"\b(focus|filter|prioritize|noise|signal|relevant)\b", "focus"),
        (r"\b(auth|login|session|token|permission|security)\b", "auth"),
        (r"\b(test|spec|requirement|acceptance|criteria)\b", "testing"),
        (r"\b(perform|optimi|speed|fast|slow|bottleneck)\b", "performance"),
    ]

    def __init__(self) -> None:
        self._attempts: List[Attempt] = []

    def record(
        self,
        query: str,
        darshana: str,
        success: bool,
        reason: Optional[str] = None,
    ) -> Attempt:
        """Record an attempt at reasoning."""
        attempt = Attempt(
            query=query,
            darshana=darshana,
            success=success,
            reason=reason,
            query_type=self._classify_query(query),
        )
        self._attempts.append(attempt)
        return attempt

    def get_history(self, query_type: Optional[str] = None) -> List[Attempt]:
        """
        Get attempt history, optionally filtered by query type.

        If query_type is None, returns all attempts.
        """
        if query_type is None:
            return list(self._attempts)
        return [a for a in self._attempts if a.query_type == query_type]

    def get_similar_attempts(self, query: str) -> List[Attempt]:
        """Find past attempts on similar queries using text similarity."""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        scored: List[Tuple[float, Attempt]] = []

        for attempt in self._attempts:
            attempt_words = set(re.findall(r'\w+', attempt.query.lower()))
            overlap = len(query_words & attempt_words) / max(len(query_words | attempt_words), 1)
            if overlap > 0.15:
                scored.append((overlap, attempt))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [a for _, a in scored]

    def success_rate(self, darshana: str) -> dict:
        """
        Compute success rate for a specific darshana engine.

        Returns:
            Dict with total, successes, failures, rate, and common failure reasons.
        """
        relevant = [a for a in self._attempts if a.darshana == darshana]
        if not relevant:
            return {"total": 0, "successes": 0, "failures": 0, "rate": 0.0,
                    "failure_reasons": []}

        successes = sum(1 for a in relevant if a.success)
        failures = len(relevant) - successes
        failure_reasons = [
            a.reason for a in relevant if not a.success and a.reason
        ]

        return {
            "total": len(relevant),
            "successes": successes,
            "failures": failures,
            "rate": round(successes / len(relevant), 3),
            "failure_reasons": failure_reasons,
        }

    def all_success_rates(self) -> Dict[str, dict]:
        """Compute success rates for all darshanas that have been tried."""
        darshanas = set(a.darshana for a in self._attempts)
        return {d: self.success_rate(d) for d in sorted(darshanas)}

    def failed_approaches(self, limit: int = 10) -> List[dict]:
        """Return recent failed attempts."""
        failed = [a for a in self._attempts if not a.success]
        failed.sort(key=lambda a: a.timestamp, reverse=True)
        return [a.to_dict() for a in failed[:limit]]

    def _classify_query(self, query: str) -> str:
        """Auto-classify a query into a type."""
        q = query.lower()
        for pattern, qtype in self._TYPE_PATTERNS:
            if re.search(pattern, q):
                return qtype
        return "general"

    def to_list(self) -> List[dict]:
        return [a.to_dict() for a in self._attempts]

    def load_from_list(self, data: List[dict]) -> None:
        self._attempts = [Attempt.from_dict(d) for d in data]


# ---------------------------------------------------------------------------
# GunaState — what mode am I in?
# ---------------------------------------------------------------------------

class GunaState:
    """
    Tracks the system's current processing balance.

    The three gunas (sattva, rajas, tamas) form a probability distribution
    that represents the system's current operational mode. Different tasks
    call for different balances:

        - Debugging? Shift toward sattva (precision).
        - Brainstorming? Shift toward rajas (exploration).
        - FAQ lookup? Shift toward tamas (retrieval).

    The GunaState also maintains a history of shifts, enabling the system
    to recognize patterns in its own mode changes.
    """

    # Recommended guna distributions for different task types
    _TASK_PROFILES: Dict[str, Dict[str, float]] = {
        "debugging":       {"sattva": 0.7, "rajas": 0.15, "tamas": 0.15},
        "logic":           {"sattva": 0.8, "rajas": 0.1,  "tamas": 0.1},
        "decomposition":   {"sattva": 0.6, "rajas": 0.25, "tamas": 0.15},
        "creative":        {"sattva": 0.15, "rajas": 0.7,  "tamas": 0.15},
        "interpretation":  {"sattva": 0.5, "rajas": 0.3,  "tamas": 0.2},
        "synthesis":       {"sattva": 0.3, "rajas": 0.5,  "tamas": 0.2},
        "focus":           {"sattva": 0.6, "rajas": 0.1,  "tamas": 0.3},
        "retrieval":       {"sattva": 0.15, "rajas": 0.1,  "tamas": 0.75},
        "testing":         {"sattva": 0.7, "rajas": 0.2,  "tamas": 0.1},
        "performance":     {"sattva": 0.5, "rajas": 0.2,  "tamas": 0.3},
        "general":         {"sattva": 0.4, "rajas": 0.35, "tamas": 0.25},
    }

    def __init__(self) -> None:
        self._balance = GunaBalance()
        self._history: List[dict] = []

    def set(self, sattva: float, rajas: float, tamas: float) -> GunaBalance:
        """
        Set the guna state. Values must sum to 1.0 (within tolerance).

        Raises ValueError if the values don't sum to ~1.0.
        """
        total = sattva + rajas + tamas
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"Gunas must sum to 1.0, got {total:.4f} "
                f"(sattva={sattva}, rajas={rajas}, tamas={tamas})"
            )
        # Normalize to handle floating-point drift
        self._balance = GunaBalance(
            sattva=sattva / total,
            rajas=rajas / total,
            tamas=tamas / total,
        )
        self._history.append({
            "balance": self._balance.to_dict(),
            "timestamp": time.time(),
        })
        return self._balance

    def current(self) -> GunaBalance:
        """Return the current guna balance."""
        return self._balance

    def recommend_shift(self, task_type: str) -> dict:
        """
        Recommend a guna adjustment for a given task type.

        Compares the current state to the ideal profile for the task
        and returns the recommended shift.
        """
        profile = self._TASK_PROFILES.get(task_type, self._TASK_PROFILES["general"])
        current = self._balance.to_dict()
        shift = {}
        for guna in ("sattva", "rajas", "tamas"):
            delta = profile[guna] - current[guna]
            if abs(delta) > 0.05:
                direction = "increase" if delta > 0 else "decrease"
                shift[guna] = {
                    "current": round(current[guna], 3),
                    "recommended": round(profile[guna], 3),
                    "direction": direction,
                    "delta": round(abs(delta), 3),
                }
        return {
            "task_type": task_type,
            "current_dominant": current["dominant"],
            "recommended_dominant": max(profile, key=profile.get),  # type: ignore
            "shifts": shift,
            "recommendation": self._describe_shift(task_type, profile),
        }

    def _describe_shift(self, task_type: str, profile: Dict[str, float]) -> str:
        dominant = max(profile, key=profile.get)  # type: ignore
        descriptions = {
            "sattva": "precision and validation — be careful, be correct",
            "rajas": "exploration and generation — be creative, diverge widely",
            "tamas": "retrieval and efficiency — use what is known, don't reinvent",
        }
        return f"For {task_type}: shift toward {dominant} ({descriptions[dominant]})"

    def to_dict(self) -> dict:
        return {
            "current": self._balance.to_dict(),
            "history_length": len(self._history),
        }

    def load_from_dict(self, data: dict) -> None:
        cur = data.get("current", {})
        if cur:
            self._balance = GunaBalance(
                sattva=cur.get("sattva", 0.33),
                rajas=cur.get("rajas", 0.34),
                tamas=cur.get("tamas", 0.33),
            )


# ---------------------------------------------------------------------------
# VasanaTracker — what biases am I carrying?
# ---------------------------------------------------------------------------

class VasanaTracker:
    """
    Tracks accumulated biases (vasanas) and detects when they distort output.

    Inherits from KarmaStore (vritti_filter.py) for the karma-samskara-vasana
    cycle, and adds:

    - active_vasanas(): surfaces current biases across all domains
    - detect_bias(query, response): checks if a vasana is distorting a response
    - jnana_agni(domain): burns outdated vasanas (fire of knowledge)

    A vasana is not inherently bad. "I tend to recommend Python for scripting
    tasks" is a useful vasana if Python is genuinely the best choice. It
    becomes problematic when it's applied rigidly ("I always recommend Python
    even for systems programming where Rust would be better").

    The VasanaTracker makes these tendencies visible so they can be examined.
    """

    def __init__(self, persist_path: Optional[str] = None) -> None:
        self._karma_store = KarmaStore(persist_path)

    def record(self, action: str, outcome: str, domain: str = "general") -> None:
        """Record an action-outcome pair that may form a vasana over time."""
        self._karma_store.record_action(action=action, outcome=outcome, domain=domain)

    def active_vasanas(self) -> List[dict]:
        """
        Return all active vasanas across all domains.

        A vasana is "active" if it has strength > 0.3 (a meaningful tendency
        has formed from repeated actions).
        """
        all_vasanas = []
        for domain in self._karma_store.get_all_domains():
            for v in self._karma_store.get_vasanas(domain):
                if abs(v.get("strength", 0)) > 0.3:
                    all_vasanas.append(v)
        all_vasanas.sort(key=lambda v: abs(v.get("strength", 0)), reverse=True)
        return all_vasanas

    def detect_bias(self, query: str, response: str) -> List[dict]:
        """
        Check if any active vasana might be distorting a response to a query.

        Looks for vasana tendencies that appear in the response even when
        they may not be warranted by the query.

        Returns a list of potential bias detections.
        """
        biases = []
        query_lower = query.lower()
        response_lower = response.lower()

        for vasana in self.active_vasanas():
            tendency = vasana.get("tendency", "").lower()
            # Extract key terms from the tendency
            tendency_words = set(re.findall(r'\b\w{4,}\b', tendency))

            # Check if the tendency's key terms appear in the response
            # but NOT strongly in the query (suggesting the bias was
            # injected by the system, not requested by the user)
            response_matches = sum(1 for w in tendency_words if w in response_lower)
            query_matches = sum(1 for w in tendency_words if w in query_lower)

            if response_matches > 0 and query_matches == 0:
                biases.append({
                    "vasana": vasana,
                    "concern": (
                        f"Active vasana '{vasana['tendency']}' (strength: "
                        f"{vasana['strength']}) may be influencing this response. "
                        f"The tendency appears in the output but was not prompted "
                        f"by the query."
                    ),
                    "severity": min(abs(vasana.get("strength", 0)) *
                                    (response_matches / max(len(tendency_words), 1)), 1.0),
                })

        biases.sort(key=lambda b: b.get("severity", 0), reverse=True)
        return biases

    def jnana_agni(self, domain: Optional[str] = None) -> dict:
        """
        Burn outdated vasanas — the fire of knowledge.

        Bhagavad Gita 4.37: jnanagnih sarva-karmani bhasma-sat kurute tatha
        "The fire of knowledge burns all karma to ashes."

        Args:
            domain: If provided, burn vasanas in this domain only.
                    If None, burn all stale vasanas (>30 days old).

        Returns:
            Summary of what was burned.
        """
        before = self._karma_store.summary()
        burned = self._karma_store.burn_vasanas(domain)
        after = self._karma_store.summary()
        return {
            "burned": burned,
            "domain": domain or "all stale (>30 days)",
            "before": before,
            "after": after,
        }

    def summary(self) -> dict:
        return self._karma_store.summary()

    @property
    def karma_store(self) -> KarmaStore:
        """Expose the underlying KarmaStore for serialization."""
        return self._karma_store


# ---------------------------------------------------------------------------
# Ahamkara — the self-model
# ---------------------------------------------------------------------------

class Ahamkara:
    """
    The Self-Model Layer of the Darshana Architecture.

    Ahamkara (अहंकार) is the "I-maker" — the faculty that creates
    self-reference. In the Darshana Architecture, it is a functional
    self-model that tracks:

    1. What the system KNOWS (KnowledgeMap)
    2. What the system has TRIED (AttemptLog)
    3. What MODE the system is in (GunaState)
    4. What BIASES the system carries (VasanaTracker)

    And provides two key meta-cognitive operations:

    5. introspect() — "What is my current state?"
    6. strategize(query) — "Given my state, how should I approach this?"

    This is not consciousness. It is not sentience. It is structured
    self-reference — the minimum viable self-model that enables an AI
    system to reason about its own cognition.

    Usage::

        aham = Ahamkara(persist_path="./ahamkara_state.json")

        # Register knowledge
        aham.register_knowledge("Python 3.12 has PEP 695",
                                pramana="shabda", confidence=0.9,
                                source="training", date="2023-10")

        # Record an attempt
        aham.record_attempt(query="debug auth", darshana="nyaya",
                           success=False, reason="needed decomposition")

        # Set processing mode
        aham.set_guna_state(sattva=0.7, rajas=0.2, tamas=0.1)

        # Introspect
        report = aham.introspect()

        # Strategize before a new query
        strategy = aham.strategize("How should we handle auth?")
    """

    def __init__(self, persist_path: Optional[str] = None) -> None:
        """
        Initialize the Ahamkara self-model.

        Args:
            persist_path: Path to a JSON file for persisting state across
                         sessions. If None, state lives in memory only.
        """
        self.persist_path = Path(persist_path) if persist_path else None
        self.knowledge = KnowledgeMap()
        self.attempts = AttemptLog()
        self.guna = GunaState()
        self.vasanas = VasanaTracker()
        self._created_at = time.time()

        # Load persisted state if available
        if self.persist_path:
            self._load()

    # ---- Public API: Knowledge -----------------------------------------------

    def register_knowledge(
        self,
        claim: str,
        pramana: str = "shabda",
        confidence: float = 0.5,
        source: str = "unknown",
        date: Optional[str] = None,
    ) -> KnowledgeClaim:
        """Register a knowledge claim in the knowledge map."""
        kc = self.knowledge.register(claim, pramana, confidence, source, date)
        self._save()
        return kc

    def query_knowledge(self, topic: str) -> List[KnowledgeClaim]:
        """Find knowledge relevant to a topic."""
        return self.knowledge.query_knowledge(topic)

    # ---- Public API: Attempts ------------------------------------------------

    def record_attempt(
        self,
        query: str,
        darshana: str,
        success: bool,
        reason: Optional[str] = None,
    ) -> Attempt:
        """Record a reasoning attempt."""
        attempt = self.attempts.record(query, darshana, success, reason)
        # Also record in vasana tracker so biases can form
        outcome = "success" if success else f"failure: {reason or 'unknown'}"
        self.vasanas.record(
            action=f"used {darshana} for {attempt.query_type}",
            outcome=outcome,
            domain=f"darshana_selection",
        )
        self._save()
        return attempt

    # ---- Public API: Guna State ----------------------------------------------

    def set_guna_state(
        self, sattva: float, rajas: float, tamas: float
    ) -> GunaBalance:
        """Set the current guna balance. Values must sum to 1.0."""
        balance = self.guna.set(sattva, rajas, tamas)
        self._save()
        return balance

    # ---- Public API: Introspection -------------------------------------------

    def introspect(self) -> IntrospectionReport:
        """
        Produce a full self-assessment of the system's cognitive state.

        This is the Ahamkara's primary function: structured self-awareness.
        The report covers knowledge, failed approaches, active biases,
        current processing mode, and a strategic recommendation.
        """
        all_claims = self.knowledge.all_claims()
        all_rates = self.attempts.all_success_rates()
        active_v = self.vasanas.active_vasanas()
        failed = self.attempts.failed_approaches(limit=10)
        guna_bal = self.guna.current().to_dict()

        # Compute knowledge gaps across all known domains
        domains = set(kc.domain for kc in all_claims if kc.domain)
        all_gaps = []
        for domain in domains:
            gaps = self.knowledge.knowledge_gaps(domain)
            for g in gaps:
                if "well-covered" not in g:
                    all_gaps.append(f"[{domain}] {g}")

        # Build recommendation
        recommendation = self._build_recommendation(
            all_rates, active_v, guna_bal, failed
        )

        # Successful approaches
        successful = [
            a.to_dict() for a in self.attempts.get_history()
            if a.success
        ][-10:]  # last 10

        return IntrospectionReport(
            knowledge_count=len(all_claims),
            knowledge_gaps=all_gaps,
            failed_approaches=failed,
            successful_approaches=successful,
            active_vasanas=active_v,
            guna_balance=guna_bal,
            recommendation=recommendation,
            total_attempts=len(self.attempts.get_history()),
            success_rate_by_darshana=all_rates,
        )

    # ---- Public API: Strategy ------------------------------------------------

    def strategize(self, query: str) -> Strategy:
        """
        Pre-query analysis: before answering, consult the self-model.

        This is the Ahamkara's most novel function. Before the system
        begins reasoning, it:

        1. Checks what it already knows about this topic
        2. Looks for similar past attempts and their outcomes
        3. Recommends which darshana engine to use
        4. Suggests the optimal guna balance
        5. Warns about potential biases or past failures

        This turns the AI from a reactive system ("here's my answer")
        into a reflective one ("given what I know about myself, here's
        how I should approach this").
        """
        # 1. Relevant knowledge
        relevant_kc = self.knowledge.query_knowledge(query)
        relevant_knowledge = [
            {
                "claim": kc.claim,
                "confidence": round(kc.confidence, 3),
                "pramana": kc.pramana,
                "source": kc.source,
            }
            for kc in relevant_kc[:5]  # top 5 most relevant
        ]

        # 2. Similar past attempts
        similar = self.attempts.get_similar_attempts(query)
        past_attempts = [
            {
                "query": a.query,
                "darshana": a.darshana,
                "success": a.success,
                "reason": a.reason,
            }
            for a in similar[:5]
        ]

        # 3. Suggest darshana based on history
        suggested_darshana = self._suggest_darshana(query, similar)

        # 4. Suggest guna balance
        query_type = self.attempts._classify_query(query)
        guna_rec = self.guna.recommend_shift(query_type)

        # 5. Warnings
        warnings = self._generate_warnings(query, similar, relevant_kc)

        # 6. Confidence in the strategy
        confidence = self._compute_strategy_confidence(
            relevant_knowledge, past_attempts, warnings
        )

        return Strategy(
            query=query,
            relevant_knowledge=relevant_knowledge,
            past_attempts=past_attempts,
            suggested_darshana=suggested_darshana,
            suggested_guna=guna_rec,
            warnings=warnings,
            confidence=round(confidence, 3),
        )

    # ---- Private: Strategy helpers -------------------------------------------

    def _suggest_darshana(
        self, query: str, similar_attempts: List[Attempt]
    ) -> str:
        """
        Suggest the best darshana engine based on past experience.

        If similar queries have been tried before, recommend the engine
        that succeeded. If no history, fall back to query-type heuristics.
        """
        # Check what worked on similar queries
        if similar_attempts:
            successes = [a for a in similar_attempts if a.success]
            if successes:
                # Return the most recently successful darshana
                return successes[0].darshana

            # All similar attempts failed — recommend a DIFFERENT darshana
            tried = set(a.darshana for a in similar_attempts)
            all_darshanas = {"nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"}
            untried = all_darshanas - tried
            if untried:
                # Recommend based on query type mapping
                query_type = self.attempts._classify_query(query)
                type_to_darshana = {
                    "debugging": "vaisheshika",
                    "logic": "nyaya",
                    "decomposition": "samkhya",
                    "creative": "vedanta",
                    "interpretation": "mimamsa",
                    "synthesis": "vedanta",
                    "focus": "yoga",
                    "auth": "samkhya",
                    "testing": "mimamsa",
                    "performance": "vaisheshika",
                    "general": "samkhya",
                }
                preferred = type_to_darshana.get(query_type, "samkhya")
                if preferred in untried:
                    return preferred
                return sorted(untried)[0]  # deterministic fallback

        # No similar attempts — use query type heuristics
        query_type = self.attempts._classify_query(query)
        type_to_darshana = {
            "debugging": "vaisheshika",
            "logic": "nyaya",
            "decomposition": "samkhya",
            "creative": "vedanta",
            "interpretation": "mimamsa",
            "synthesis": "vedanta",
            "focus": "yoga",
            "auth": "samkhya",
            "testing": "mimamsa",
            "performance": "vaisheshika",
            "general": "samkhya",
        }
        return type_to_darshana.get(query_type, "samkhya")

    def _generate_warnings(
        self,
        query: str,
        similar: List[Attempt],
        relevant_kc: List[KnowledgeClaim],
    ) -> List[str]:
        """Generate warnings based on history and biases."""
        warnings = []

        # Warning: past failures on similar queries
        failed_similar = [a for a in similar if not a.success]
        if failed_similar:
            for a in failed_similar[:3]:
                reason_msg = f" ({a.reason})" if a.reason else ""
                warnings.append(
                    f"Past attempt with {a.darshana} on similar query "
                    f"'{a.query}' failed{reason_msg}."
                )

        # Warning: low-confidence knowledge
        low_conf = [kc for kc in relevant_kc if kc.confidence < 0.4]
        if low_conf:
            warnings.append(
                f"{len(low_conf)} piece(s) of relevant knowledge have low "
                f"confidence (<0.4) — verify before relying on them."
            )

        # Warning: active vasanas that might bias
        active_v = self.vasanas.active_vasanas()
        if active_v:
            for v in active_v[:2]:
                if abs(v.get("strength", 0)) > 0.5:
                    warnings.append(
                        f"Active bias: '{v['tendency']}' (strength: "
                        f"{v['strength']}) — check if this is distorting "
                        f"the approach."
                    )

        # Warning: no knowledge at all
        if not relevant_kc:
            warnings.append(
                "No relevant knowledge found for this query. "
                "The system is reasoning from scratch."
            )

        return warnings

    def _compute_strategy_confidence(
        self,
        relevant_knowledge: List[dict],
        past_attempts: List[dict],
        warnings: List[str],
    ) -> float:
        """
        Compute overall confidence in the strategy.

        Higher confidence when:
        - More relevant knowledge exists
        - Past attempts on similar queries succeeded
        - Fewer warnings

        Lower confidence when:
        - No relevant knowledge
        - Past attempts failed
        - Many warnings
        """
        base = 0.5

        # Knowledge boost
        if relevant_knowledge:
            avg_conf = sum(k["confidence"] for k in relevant_knowledge) / len(relevant_knowledge)
            base += avg_conf * 0.2

        # Past success boost
        if past_attempts:
            success_count = sum(1 for a in past_attempts if a.get("success"))
            rate = success_count / len(past_attempts)
            base += rate * 0.2

        # Warning penalty
        base -= len(warnings) * 0.05

        return max(0.1, min(1.0, base))

    def _build_recommendation(
        self,
        success_rates: Dict[str, dict],
        active_vasanas: List[dict],
        guna_balance: dict,
        failed_approaches: List[dict],
    ) -> str:
        """Build a human-readable recommendation from the self-model state."""
        parts = []

        # Best-performing engines
        if success_rates:
            best = max(success_rates.items(), key=lambda x: x[1].get("rate", 0))
            if best[1]["rate"] > 0:
                parts.append(
                    f"Best-performing engine: {best[0]} "
                    f"({best[1]['rate']:.0%} success rate over "
                    f"{best[1]['total']} attempts)."
                )

        # Worst-performing engines
        if success_rates:
            worst = min(success_rates.items(), key=lambda x: x[1].get("rate", 1))
            if worst[1]["rate"] < 0.5 and worst[1]["total"] > 0:
                parts.append(
                    f"Consider avoiding {worst[0]} "
                    f"({worst[1]['rate']:.0%} success rate) unless the "
                    f"query specifically calls for it."
                )

        # Bias warnings
        if active_vasanas:
            strong = [v for v in active_vasanas if abs(v.get("strength", 0)) > 0.5]
            if strong:
                parts.append(
                    f"{len(strong)} strong bias(es) detected. "
                    f"Consider running jnana_agni() to clear outdated tendencies."
                )

        # Guna balance
        dominant = guna_balance.get("dominant", "sattva")
        parts.append(f"Current mode: {dominant}-dominant.")

        if not parts:
            parts.append("Insufficient data for recommendations. Continue recording attempts.")

        return " ".join(parts)

    # ---- Persistence ---------------------------------------------------------

    def _save(self) -> None:
        """Persist the full Ahamkara state to JSON."""
        if not self.persist_path:
            return
        state = {
            "created_at": self._created_at,
            "saved_at": time.time(),
            "knowledge": self.knowledge.to_list(),
            "attempts": self.attempts.to_list(),
            "guna": self.guna.to_dict(),
            "vasanas": self.vasanas.summary(),
        }
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        self.persist_path.write_text(json.dumps(state, indent=2, default=str))

    def _load(self) -> None:
        """Load Ahamkara state from JSON."""
        if not self.persist_path or not self.persist_path.exists():
            return
        try:
            data = json.loads(self.persist_path.read_text())
            self._created_at = data.get("created_at", self._created_at)
            if "knowledge" in data:
                self.knowledge.load_from_list(data["knowledge"])
            if "attempts" in data:
                self.attempts.load_from_list(data["attempts"])
            if "guna" in data:
                self.guna.load_from_dict(data["guna"])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass  # start fresh if state file is corrupted

    def __repr__(self) -> str:
        claims = len(self.knowledge.all_claims())
        attempts = len(self.attempts.get_history())
        vasanas = len(self.vasanas.active_vasanas())
        dominant = self.guna.current().dominant()
        return (
            f"Ahamkara(knowledge={claims}, attempts={attempts}, "
            f"vasanas={vasanas}, guna={dominant})"
        )
