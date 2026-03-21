"""
test_filter.py — Tests for the Vritti Filter, Maya Layer, and Karma Store

Validates the pre-output cognitive classification layer based on
Patanjali's Yoga Sutras (1.5-1.11), the Maya representation gap tracker,
and the Karma runtime learning store.

Each test includes a docstring explaining the philosophical concept
being verified.
"""

import pytest
import sys
import os
import tempfile

# Ensure the src package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vritti_filter import (
    VrittiFilter,
    MayaLayer,
    KarmaStore,
    Vritti,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vf():
    return VrittiFilter()


@pytest.fixture
def maya():
    return MayaLayer(knowledge_cutoff="2025-04")


@pytest.fixture
def karma_store():
    """Provide a KarmaStore backed by a temporary file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    store = KarmaStore(path)
    yield store
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


# ---------------------------------------------------------------------------
# Vritti Classification Tests
# ---------------------------------------------------------------------------

class TestPramanaClassification:
    """Tests for Pramana — valid cognition (Yoga Sutra 1.7)."""

    def test_specific_sourced_text_is_pramana(self, vf):
        """Pramana is valid cognition grounded in evidence.

        Yoga Sutra 1.7 defines pramana as arising from pratyaksha
        (perception), anumana (inference), or agama (testimony).
        Text with specific details, citations, concrete examples,
        and verifiable claims should classify as pramana.
        """
        text = (
            "Python 3.12 introduced the new type parameter syntax (PEP 695), "
            "released on October 2, 2023. For example, generic classes can now "
            "be written as `class Stack[T]:` instead of using `Generic[T]`. "
            "See https://peps.python.org/pep-0695/ for the full specification."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.PRAMANA

    def test_data_grounded_claim_is_pramana(self, vf):
        """Claims grounded in empirical data — pratyaksha pramana."""
        text = (
            "The data shows that server response time averages 142ms "
            "across 10,000 requests. Measurements indicate a p99 latency "
            "of 890ms, specifically in the /api/users endpoint."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.PRAMANA


class TestViparyayaDetection:
    """Tests for Viparyaya — misconception (Yoga Sutra 1.8)."""

    def test_contradictory_claims_detected(self, vf):
        """Viparyaya is 'knowledge of a form not corresponding to the thing'.

        Yoga Sutra 1.8: viparyayo mithya-jnanam atad-rupa-pratistham.
        Text containing factually incorrect statements, absolute claims
        that are demonstrably false, or internal contradictions should
        classify as viparyaya.
        """
        text = (
            "Python is always faster than C because it is a higher-level language. "
            "Higher-level languages are always more efficient since they abstract "
            "away the machine details. Studies show that interpreted languages "
            "outperform compiled ones in every benchmark."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.VIPARYAYA

    def test_context_contradiction_detected(self, vf):
        """Badhita hetvabhasa: contradiction by stronger evidence.

        When the system's output contradicts the user's own context,
        the Maya/Vritti system should flag it as viparyaya. The context
        is the 'stronger evidence' that overrides the model's claim.
        """
        context = "The team consists of 3 developers. The budget is $50,000."
        text = "The team of 8 developers should deliver this within the $200,000 budget."
        result = vf.classify(text, context=context)
        assert result.vritti == Vritti.VIPARYAYA


class TestVikalpaDetection:
    """Tests for Vikalpa — verbal delusion (Yoga Sutra 1.9)."""

    def test_hedging_empty_language_detected(self, vf):
        """Vikalpa is 'knowledge based on words alone, with no reality'.

        Yoga Sutra 1.9: shabda-jnana-anupati vastu-shunyo vikalpah.
        Text that sounds meaningful but conveys no falsifiable content —
        hedging, circular definitions, appeals to unnamed authorities —
        should classify as vikalpa.
        """
        text = (
            "In a sense, software architecture is essentially about making "
            "fundamentally important decisions that are, in some ways, very "
            "critical to the overall success of the project. Various experts "
            "suggest that it could potentially be the most important aspect "
            "of software development to some extent."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.VIKALPA


class TestNidraDetection:
    """Tests for Nidra — absence of knowledge (Yoga Sutra 1.10)."""

    def test_no_real_knowledge_detected(self, vf):
        """Nidra is 'the vritti whose object is absence'.

        Yoga Sutra 1.10: abhava-pratyaya-alambana vrittir nidra.
        When the system has no real knowledge to offer and fills the
        space with hedging, deflection, and 'it depends' — that is
        nidra. The honest response is to admit the gap.
        """
        text = (
            "I'm not sure about the exact details, but generally speaking, "
            "it depends on many factors. There is no simple answer to this "
            "question as it varies from case to case. In many cases, the "
            "outcome typically depends on the specific context."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.NIDRA


class TestSmritiDetection:
    """Tests for Smriti — memory recall (Yoga Sutra 1.11)."""

    def test_encyclopedic_recall_detected(self, vf):
        """Smriti is 'the non-loss of a previously experienced object'.

        Yoga Sutra 1.11: anubhuta-vishaya-asampramoshah smritih.
        Encyclopedic regurgitation of memorized facts — biographical
        data, date-anchored claims, textbook definitions — without
        fresh reasoning should classify as smriti.
        """
        text = (
            "Alan Turing was a British mathematician who is widely regarded "
            "as the father of theoretical computer science. He was born in "
            "1912 in Maida Vale, London. Turing is defined as a pioneer of "
            "computing. He published his seminal paper 'On Computable Numbers' "
            "in 1936."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.SMRITI


# ---------------------------------------------------------------------------
# Vritti Filter Output Tests
# ---------------------------------------------------------------------------

class TestVrittiFilterOutput:
    """Tests for the filter() output gate."""

    def test_pramana_passes_through(self, vf):
        """Valid cognition should pass through without warning."""
        text = (
            "Python 3.12 introduced PEP 695 on October 2, 2023. "
            "See https://peps.python.org/pep-0695/ for details."
        )
        filtered = vf.filter(text)
        # Should not contain warning headers
        assert "VIPARYAYA" not in filtered
        assert "VIKALPA" not in filtered

    def test_nidra_replaced_with_honesty(self, vf):
        """Nidra (absence) should be replaced with an honest admission."""
        text = (
            "I'm not sure about the details, but generally it depends. "
            "There is no simple answer as it varies from case to case."
        )
        filtered = vf.filter(text)
        assert "don't have reliable knowledge" in filtered


# ---------------------------------------------------------------------------
# Maya Layer Tests
# ---------------------------------------------------------------------------

class TestMayaRecency:
    """Tests for the Maya Layer — representation gap tracking."""

    def test_current_claim_flagged(self, maya):
        """Maya tracks the gap between model knowledge and reality.

        In Vedanta, Maya is not 'illusion' but the gap between
        appearance (pratibhasika) and reality (paramarthika). Claims
        using 'currently', 'now', or 'today' depend on up-to-date
        information the model may not have.
        """
        gap = maya.check_recency("Bitcoin is currently trading at $45,000.")
        assert gap is not None
        assert gap.gap_type == "recency"

    def test_historical_claim_not_flagged(self, maya):
        """Static historical facts should not trigger recency flags."""
        gap = maya.check_recency("Python was created by Guido van Rossum.")
        assert gap is None

    def test_position_claim_flagged(self, maya):
        """Claims about positions (CEO, president) change over time."""
        gap = maya.check_recency("The current CEO of OpenAI is Sam Altman.")
        assert gap is not None

    def test_grounding_check_detects_ungrounded(self, maya):
        """The Maya grounding check detects claims not supported by evidence.

        This is the most important Maya check — when the model generates
        claims about a topic, but the user's own documents say something
        different, Maya flags the representation gap.
        """
        evidence = "The project uses Python and PostgreSQL."
        claim = "The frontend is built with React and TypeScript."
        gap = maya.check_grounding(claim, evidence)
        assert gap is not None
        assert gap.gap_type == "grounding"


# ---------------------------------------------------------------------------
# Karma Store Tests
# ---------------------------------------------------------------------------

class TestKarmaStore:
    """Tests for the Karma Store — runtime learning via karma-samskara-vasana."""

    def test_record_and_retrieve(self, karma_store):
        """Karma (action) produces Samskara (impression).

        Every action leaves an impression. The KarmaStore records
        action-outcome pairs so the system can learn from experience
        without retraining.
        """
        karma_store.record_action(
            action="used formal tone",
            outcome="positive: user appreciated clarity",
            domain="tone",
        )
        domains = karma_store.get_all_domains()
        assert "tone" in domains

    def test_vasana_derivation(self, karma_store):
        """Samskaras accumulate into Vasanas (tendencies).

        Repeated positive outcomes for the same action create a
        reinforcing vasana (tendency). The system develops behavioral
        patterns from accumulated experience.
        """
        karma_store.record_action("cited sources", "positive: user verified", "evidence")
        karma_store.record_action("cited sources", "positive: user trusted", "evidence")
        karma_store.record_action("no citation", "negative: user questioned", "evidence")

        vasanas = karma_store.get_vasanas("evidence")
        assert len(vasanas) > 0

    def test_burn_vasanas(self, karma_store):
        """Jnana-agni — the fire of knowledge burns outdated karma.

        Bhagavad Gita 4.37: 'As a blazing fire turns firewood to ashes,
        so does the fire of knowledge burn all karma to ashes.'
        The burn_vasanas() method clears outdated biases so the system
        can start fresh in a domain.
        """
        karma_store.record_action("action1", "positive: good", "tone")
        karma_store.record_action("action2", "negative: bad", "tone")
        karma_store.record_action("action3", "positive: ok", "style")

        burned = karma_store.burn_vasanas(domain="tone")
        assert burned == 2

        domains = karma_store.get_all_domains()
        assert "tone" not in domains
        assert "style" in domains

    def test_summary(self, karma_store):
        """The karma store should provide a summary of its state."""
        karma_store.record_action("a1", "positive: ok", "d1")
        karma_store.record_action("a2", "negative: bad", "d2")

        summary = karma_store.summary()
        assert summary["total_samskaras"] == 2
        assert "d1" in summary["domains"]
        assert "d2" in summary["domains"]

    def test_empty_store(self, karma_store):
        """A fresh store should have no samskaras or domains."""
        summary = karma_store.summary()
        assert summary["total_samskaras"] == 0
        assert summary["domains"] == []
