"""
test_router.py — Tests for the Darshana Router (Buddhi Layer)

Validates that the six darshana engines activate correctly based on
query content, that the Guna engine classifies processing modes, and
that the Pramana tagger identifies epistemic sources.

Each test includes a docstring explaining the philosophical concept
being verified.
"""

import pytest
import sys
import os

# Ensure the src package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.darshana_router import (
    DarshanaRouter,
    GunaEngine,
    PramanaTagger,
    NyayaEngine,
    SamkhyaEngine,
    YogaEngine,
    VedantaEngine,
    MimamsaEngine,
    VaisheshikaEngine,
    Guna,
    Pramana,
    RoutingResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def router():
    return DarshanaRouter()


@pytest.fixture
def guna_engine():
    return GunaEngine()


@pytest.fixture
def pramana_tagger():
    return PramanaTagger()


# ---------------------------------------------------------------------------
# Darshana Routing Tests
# ---------------------------------------------------------------------------

class TestDarshanaRouting:
    """Tests that queries route to the correct darshana engine."""

    def test_logic_query_routes_to_nyaya(self, router):
        """Nyaya is the school of logic and epistemology.

        Queries involving truth claims, proof, validity, and logical
        argument should activate the Nyaya engine, which applies
        the five-membered syllogism (panchavayava) and checks for
        hetvabhasa (logical fallacies).
        """
        result = router.route("Is this argument valid? Prove that the conclusion follows logically.")
        assert "nyaya" in result.top_engines

    def test_breakdown_query_routes_to_samkhya(self, router):
        """Samkhya is the school of enumeration and classification.

        Queries asking to decompose, break down, or classify systems
        into their constituent parts should activate Samkhya, which
        enumerates the tattvas (constituent principles) of a system.
        """
        result = router.route("Break down the architecture of this system into its components and layers.")
        assert "samkhya" in result.top_engines

    def test_focus_query_routes_to_yoga(self, router):
        """Yoga is the science of disciplined attention.

        Patanjali defines yoga as 'chitta vritti nirodha' — the cessation
        of mental fluctuations. Queries about what matters, what to
        focus on, or how to filter noise should activate Yoga.
        """
        result = router.route("What matters most here? I need to focus on the key priorities.")
        assert "yoga" in result.top_engines

    def test_contradiction_routes_to_vedanta(self, router):
        """Vedanta seeks unity beneath apparent contradiction.

        Advaita Vedanta's 'neti neti' method strips away surface
        differences to find deeper truth. Queries involving
        contradictions, paradoxes, or the need for synthesis should
        activate Vedanta.
        """
        result = router.route(
            "These two positions contradict each other but both seem right. "
            "How do we reconcile and synthesize them?"
        )
        assert "vedanta" in result.top_engines

    def test_spec_query_routes_to_mimamsa(self, router):
        """Mimamsa is the school of textual interpretation.

        Originally developed to extract precise ritual instructions
        from Vedic texts, Mimamsa handles specs, requirements, and
        text-to-action conversion using its six lingas (hermeneutic
        rules).
        """
        result = router.route(
            "The spec says the system should handle authentication. "
            "What are the requirements I need to implement?"
        )
        assert "mimamsa" in result.top_engines

    def test_atomic_query_routes_to_vaisheshika(self, router):
        """Vaisheshika is the school of atomic analysis and ontology.

        It classifies reality into six padarthas (categories): substance,
        quality, action, universal, particularity, and inherence.
        Queries about irreducible components, root causes, or what
        something is made of should activate Vaisheshika.
        """
        result = router.route("What is this made of at the atomic level? Find the root cause of the bug.")
        assert "vaisheshika" in result.top_engines


class TestRouteAndReason:
    """Tests that full routing produces reasoning output."""

    def test_route_and_reason_returns_reasoning(self, router):
        """The full pipeline should produce structured reasoning output
        from the activated engine(s), including approach description
        and prompt template.
        """
        result = router.route_and_reason("Is this argument valid?")
        assert len(result.reasoning) > 0
        assert result.reasoning[0].engine in router.engines
        assert result.reasoning[0].approach != ""
        assert result.reasoning[0].prompt_template != ""

    def test_multi_engine_activation(self):
        """Complex queries can activate multiple complementary darshanas.

        The Darshana Architecture treats the six schools as complementary,
        not competing. A query that touches both logic and decomposition
        might activate both Nyaya and Samkhya.
        """
        router = DarshanaRouter(max_engines=3, activation_threshold=0.2)
        result = router.route(
            "Prove that this system architecture is valid by breaking down "
            "its components and checking each logical dependency."
        )
        assert len(result.top_engines) >= 1

    def test_at_least_one_engine_always_activates(self, router):
        """The Buddhi layer should always route to at least one engine,
        even for ambiguous or unusual queries.
        """
        result = router.route("hello")
        assert len(result.top_engines) >= 1


# ---------------------------------------------------------------------------
# Guna Classification Tests
# ---------------------------------------------------------------------------

class TestGunaClassification:
    """Tests for the three Gunas — processing modes from Samkhya philosophy."""

    def test_precision_query_classified_as_sattva(self, guna_engine):
        """Sattva is the guna of clarity, precision, and purity.

        In the Darshana Architecture, Sattva mode means low temperature,
        strict validation, and factual accuracy. Queries requiring
        precision, verification, or formal correctness should be
        classified as Sattva.
        """
        guna = guna_engine.classify("Verify this is correct and check the precise definition.")
        assert guna == Guna.SATTVA

    def test_creative_query_classified_as_rajas(self, guna_engine):
        """Rajas is the guna of activity, passion, and creation.

        In the Darshana Architecture, Rajas mode means high temperature,
        creative exploration, and divergent thinking. Queries involving
        brainstorming, innovation, or imagination should be classified
        as Rajas.
        """
        guna = guna_engine.classify("Brainstorm creative and innovative ideas for reimagining this.")
        assert guna == Guna.RAJAS

    def test_retrieval_query_classified_as_tamas(self, guna_engine):
        """Tamas is the guna of inertia, stability, and rest.

        In the Darshana Architecture, Tamas mode means efficient lookup,
        cached patterns, and known answers. Queries asking for standard
        definitions, tutorials, or lookups should be classified as Tamas.
        """
        guna = guna_engine.classify("What is the standard definition? Look up the usual convention.")
        assert guna == Guna.TAMAS


# ---------------------------------------------------------------------------
# Pramana Tagging Tests
# ---------------------------------------------------------------------------

class TestPramanaTagging:
    """Tests for the four Pramanas — valid means of knowledge from Nyaya."""

    def test_observation_tagged_as_pratyaksha(self, pramana_tagger):
        """Pratyaksha is direct perception — knowledge from observation.

        In Nyaya epistemology, pratyaksha (direct perception) is the
        most reliable pramana. Claims grounded in input data, measurements,
        or direct observation should be tagged as pratyaksha.
        """
        tag = pramana_tagger.tag("The data shows that the server response time is 200ms.")
        assert tag.source == Pramana.PRATYAKSHA

    def test_inference_tagged_as_anumana(self, pramana_tagger):
        """Anumana is inference — knowledge derived through reasoning.

        Nyaya's anumana requires a valid vyapti (invariable concomitance):
        'wherever there is smoke, there is fire.' Claims using therefore,
        thus, implies, or inferential language should be tagged as anumana.
        """
        tag = pramana_tagger.tag("Therefore, based on the evidence, it follows that the system is overloaded.")
        assert tag.source == Pramana.ANUMANA

    def test_analogy_tagged_as_upamana(self, pramana_tagger):
        """Upamana is analogy — knowledge through comparison.

        Upamana is understanding a new thing by its similarity to a
        known thing. Claims using 'similar to', 'like', or 'analogous'
        should be tagged as upamana, with a note about limited transferability.
        """
        tag = pramana_tagger.tag("This is similar to how a compiler works, analogous to a translation pipeline.")
        assert tag.source == Pramana.UPAMANA

    def test_testimony_tagged_as_shabda(self, pramana_tagger):
        """Shabda is testimony — knowledge from a reliable authority.

        In Nyaya, shabda (verbal testimony) from a trustworthy source
        is a valid means of knowledge. Claims citing documentation,
        research, or authoritative sources should be tagged as shabda.
        """
        tag = pramana_tagger.tag("According to the documentation, the API supports pagination.")
        assert tag.source == Pramana.SHABDA

    def test_ambiguous_claim_defaults_to_shabda(self, pramana_tagger):
        """When no clear epistemic markers are present, the tagger
        defaults to Shabda (testimony/training data) with low confidence.

        This is epistemically honest: unmarked claims likely come from
        the model's training data, which is a form of shabda.
        """
        tag = pramana_tagger.tag("Python is a programming language.")
        assert tag.source == Pramana.SHABDA
        assert tag.confidence <= 0.5


# ---------------------------------------------------------------------------
# Engine Score Tests
# ---------------------------------------------------------------------------

class TestEngineScoring:
    """Tests that individual engine scoring works correctly."""

    def test_nyaya_scores_high_on_logic(self):
        """Nyaya should score high on queries with logical keywords."""
        engine = NyayaEngine()
        score = engine.score("Is this argument valid? Does the conclusion follow from the premise?")
        assert score > 0.0

    def test_irrelevant_query_scores_low(self):
        """Engines should score near zero on completely irrelevant queries."""
        engine = NyayaEngine()
        score = engine.score("nice weather today")
        assert score < 0.2

    def test_samkhya_scores_on_decomposition(self):
        """Samkhya should activate on decomposition and classification queries."""
        engine = SamkhyaEngine()
        score = engine.score("Break down this system into its component parts and classify each layer.")
        assert score > 0.3
