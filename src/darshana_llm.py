"""
darshana_llm.py — The Main LLM Interface for the Darshana Architecture
=======================================================================

This module ties together every layer of the Darshana Architecture into a
single callable interface that routes queries through Hindu philosophical
reasoning engines backed by real LLM calls via the Anthropic Claude API.

Pipeline (mirrors the Samkhya tattva hierarchy from THESIS.md):

    Query
     |
     v
    BUDDHI (DarshanaRouter) — fast classification, engine selection
     |
     v
    GUNA ENGINE — sets processing mode (sattva/rajas/tamas)
     |
     v
    DARSHANA PROMPTS — engine-specific system prompt forces reasoning pattern
     |
     v
    ANTHROPIC API — actual LLM call with structured prompt
     |
     v
    VRITTI FILTER — classifies output quality (pramana/viparyaya/vikalpa/nidra/smriti)
     |
     v
    PRAMANA TAGGER — tags epistemic provenance of the response
     |
     v
    KARMA STORE — records the interaction for runtime learning
     |
     v
    DarshanaResponse — structured output with full metadata

Usage as library:

    from darshana_llm import DarshanaLLM

    llm = DarshanaLLM(api_key="sk-ant-...")
    response = llm.think("Should we rewrite our backend in Rust?")
    print(response.text)        # the answer
    print(response.darshana)    # which engine(s) reasoned
    print(response.guna)        # processing mode used
    print(response.vritti)      # output quality classification
    print(response.pramana)     # epistemic source tag
    print(response.confidence)  # vritti confidence score
    print(response.reasoning)   # darshana-specific reasoning trace

Usage from command line:

    python -m src "Should we rewrite our backend in Rust?"

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

import anthropic

from .darshana_router import (
    DarshanaRouter,
    PramanaTagger,
    Guna,
    Pramana,
    PramanaTag,
    RoutingResult,
)
from .vritti_filter import (
    VrittiFilter,
    Vritti,
    VrittiResult,
    MayaLayer,
    KarmaStore,
)
from .prompts import (
    get_darshana_prompt,
    build_multi_darshana_prompt,
)


# ---------------------------------------------------------------------------
# Response dataclass
# ---------------------------------------------------------------------------

@dataclass
class DarshanaResponse:
    """
    The complete output of a Darshana-routed LLM call.

    This is the Purusha-level view — the witness that sees all layers
    of processing and their results in a single structured object.

    Attributes:
        text: The final answer text (after vritti filtering).
        raw_text: The unfiltered LLM output (before vritti processing).
        darshana: List of engine names that processed this query.
        guna: The processing mode used (sattva/rajas/tamas).
        vritti: The output quality classification.
        pramana: The epistemic source tag for the primary claim.
        confidence: The vritti filter's confidence in the classification.
        reasoning: The darshana-specific reasoning trace (full LLM output).
        routing: The full routing result from the Buddhi layer.
        vritti_result: The full VrittiResult object with fallacies and suggestions.
        pramana_tag: The full PramanaTag object.
        maya_gaps: Any representation gaps detected by the Maya layer.
        model: The model used for the LLM call.
        latency_ms: Round-trip time for the LLM call in milliseconds.
        input_tokens: Number of input tokens used.
        output_tokens: Number of output tokens generated.
    """
    text: str
    raw_text: str
    darshana: List[str]
    guna: str
    vritti: str
    pramana: str
    confidence: float
    reasoning: str
    routing: Optional[RoutingResult] = None
    vritti_result: Optional[VrittiResult] = None
    pramana_tag: Optional[PramanaTag] = None
    maya_gaps: List[Dict] = field(default_factory=list)
    model: str = ""
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON output or logging."""
        return {
            "text": self.text,
            "darshana": self.darshana,
            "guna": self.guna,
            "vritti": self.vritti,
            "pramana": self.pramana,
            "confidence": round(self.confidence, 3),
            "reasoning": self.reasoning,
            "model": self.model,
            "latency_ms": round(self.latency_ms, 1),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "maya_gaps": self.maya_gaps,
        }


@dataclass
class MultiDarshanaResponse:
    """
    Output from think_multi() — all relevant darshanas run in sequence,
    then synthesized.

    Attributes:
        synthesis: The final synthesized response (Vedanta unification).
        individual: List of DarshanaResponse objects, one per engine.
        query: The original query.
        engines_used: Names of all engines that ran.
        total_latency_ms: Sum of all LLM call latencies.
    """
    synthesis: DarshanaResponse
    individual: List[DarshanaResponse]
    query: str
    engines_used: List[str]
    total_latency_ms: float = 0.0


# ---------------------------------------------------------------------------
# Main LLM wrapper
# ---------------------------------------------------------------------------

class DarshanaLLM:
    """
    The main interface to the Darshana Architecture.

    Takes a query, routes it through the Buddhi layer to one or more of the
    six darshana engines, calls the Anthropic Claude API with a darshana-specific
    system prompt that forces structured reasoning, then passes the output
    through the Vritti Filter and Pramana Tagger.

    This is the integration layer that turns philosophical architecture into
    working software.

    Usage::

        llm = DarshanaLLM(api_key="sk-ant-...")
        response = llm.think("Should we rewrite our backend in Rust?")
        print(response.darshana)     # ["nyaya", "samkhya"]
        print(response.guna)         # "sattva"
        print(response.vritti)       # "pramana"
        print(response.text)         # the actual answer

    Args:
        model: Anthropic model identifier. Defaults to claude-sonnet-4-20250514.
        api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
        max_tokens: Maximum tokens for LLM response.
        activation_threshold: Minimum score for a darshana engine to activate.
        max_engines: Maximum engines to activate per query.
        karma_store_path: Path for the KarmaStore JSON file. None = in-memory.
        knowledge_cutoff: Date string for the Maya layer's recency checks.
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_tokens: int = 4096,
        activation_threshold: float = 0.3,
        max_engines: int = 2,
        karma_store_path: Optional[str] = None,
        knowledge_cutoff: str = "2025-05",
    ) -> None:
        # Resolve API key: constructor > env var > error
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError(
                "Anthropic API key required. Pass api_key= to constructor "
                "or set ANTHROPIC_API_KEY environment variable."
            )

        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens

        # Initialize the Anthropic client
        self.client = anthropic.Anthropic(api_key=resolved_key)

        # Initialize the Darshana pipeline components
        self.router = DarshanaRouter(
            activation_threshold=activation_threshold,
            max_engines=max_engines,
        )
        self.vritti_filter = VrittiFilter()
        self.pramana_tagger = PramanaTagger()
        self.maya_layer = MayaLayer(knowledge_cutoff=knowledge_cutoff)
        self.karma_store = KarmaStore(store_path=karma_store_path)

    # ------------------------------------------------------------------
    # Primary API: think()
    # ------------------------------------------------------------------

    def think(
        self,
        query: str,
        context: Optional[str] = None,
    ) -> DarshanaResponse:
        """
        Process a query through the full Darshana pipeline.

        This is the main entry point. The pipeline:
        1. Buddhi (router) classifies the query and selects engine(s)
        2. Guna engine sets the processing mode
        3. Darshana-specific system prompt is constructed
        4. Anthropic API is called with the structured prompt
        5. Vritti filter classifies the output quality
        6. Pramana tagger tags the epistemic source
        7. Maya layer checks for representation gaps
        8. Karma store records the interaction

        Args:
            query: The user's question or problem.
            context: Optional grounding context (documents, prior conversation).

        Returns:
            A DarshanaResponse with the answer and full pipeline metadata.
        """
        # --- Step 1: Buddhi — route to darshana engine(s) ---
        routing = self.router.route(query)
        engines = routing.top_engines
        guna = routing.guna

        # --- Step 2: Construct the system prompt ---
        if len(engines) > 1:
            system_prompt = build_multi_darshana_prompt(
                engines, guna=guna.value
            )
        else:
            system_prompt = get_darshana_prompt(
                engines[0], guna=guna.value
            )

        # --- Step 3: Build the user message ---
        user_message = query
        if context:
            user_message = (
                f"CONTEXT:\n{context}\n\n"
                f"QUERY:\n{query}"
            )

        # --- Step 4: Call the Anthropic API ---
        raw_text, latency_ms, input_tokens, output_tokens = self._call_api(
            system_prompt=system_prompt,
            user_message=user_message,
        )

        # --- Step 5: Vritti filter — classify output quality ---
        vritti_result = self.vritti_filter.classify(raw_text, context=context)
        filtered_text = self.vritti_filter.filter(raw_text, context=context)

        # --- Step 6: Pramana tagger — epistemic provenance ---
        # Tag the first substantial sentence of the response
        first_claim = self._extract_first_claim(raw_text)
        pramana_tag = self.pramana_tagger.tag(first_claim)

        # --- Step 7: Maya layer — representation gap checks ---
        maya_gaps = []
        recency_gap = self.maya_layer.check_recency(raw_text)
        if recency_gap:
            maya_gaps.append(recency_gap.to_dict())
        if context:
            grounding_gap = self.maya_layer.check_grounding(raw_text, context)
            if grounding_gap:
                maya_gaps.append(grounding_gap.to_dict())

        # --- Step 8: Karma store — record the interaction ---
        self.karma_store.record_action(
            action=f"darshana={','.join(engines)} guna={guna.value} query_len={len(query)}",
            outcome=f"vritti={vritti_result.vritti.value} confidence={vritti_result.confidence:.2f}",
            domain="darshana_routing",
        )

        # --- Assemble the response ---
        return DarshanaResponse(
            text=filtered_text,
            raw_text=raw_text,
            darshana=engines,
            guna=guna.value,
            vritti=vritti_result.vritti.value,
            pramana=pramana_tag.source.value,
            confidence=vritti_result.confidence,
            reasoning=raw_text,
            routing=routing,
            vritti_result=vritti_result,
            pramana_tag=pramana_tag,
            maya_gaps=maya_gaps,
            model=self.model,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    # ------------------------------------------------------------------
    # Multi-darshana: think_multi()
    # ------------------------------------------------------------------

    def think_multi(
        self,
        query: str,
        context: Optional[str] = None,
    ) -> MultiDarshanaResponse:
        """
        Run ALL relevant darshana engines on the query, then synthesize.

        Unlike think() which routes to the top engine(s), think_multi()
        runs every engine that scores above the activation threshold and
        then performs a Vedanta synthesis across all their outputs.

        This is computationally expensive (multiple LLM calls) but provides
        the richest possible analysis — seeing a problem from all six
        philosophical perspectives.

        Args:
            query: The user's question or problem.
            context: Optional grounding context.

        Returns:
            A MultiDarshanaResponse containing individual engine outputs
            and a synthesized final answer.
        """
        # Route to get scores, but use ALL engines above threshold
        routing = self.router.route(query)
        guna = routing.guna

        # Get all engines above threshold, or at least the top 2
        sorted_engines = sorted(
            routing.engine_scores.items(), key=lambda x: x[1], reverse=True
        )
        relevant_engines = [
            name for name, score in sorted_engines
            if score >= self.router.activation_threshold
        ]
        if len(relevant_engines) < 2:
            relevant_engines = [name for name, _ in sorted_engines[:2]]

        # --- Run each darshana individually ---
        individual_responses: List[DarshanaResponse] = []
        total_latency = 0.0

        for engine_name in relevant_engines:
            system_prompt = get_darshana_prompt(engine_name, guna=guna.value)

            user_message = query
            if context:
                user_message = f"CONTEXT:\n{context}\n\nQUERY:\n{query}"

            raw_text, latency_ms, input_tokens, output_tokens = self._call_api(
                system_prompt=system_prompt,
                user_message=user_message,
            )

            vritti_result = self.vritti_filter.classify(raw_text, context=context)
            pramana_tag = self.pramana_tagger.tag(
                self._extract_first_claim(raw_text)
            )

            response = DarshanaResponse(
                text=raw_text,
                raw_text=raw_text,
                darshana=[engine_name],
                guna=guna.value,
                vritti=vritti_result.vritti.value,
                pramana=pramana_tag.source.value,
                confidence=vritti_result.confidence,
                reasoning=raw_text,
                model=self.model,
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            individual_responses.append(response)
            total_latency += latency_ms

        # --- Vedanta synthesis across all engines ---
        synthesis_prompt = self._build_synthesis_prompt(
            query, individual_responses, guna
        )

        synthesis_text, synth_latency, synth_in, synth_out = self._call_api(
            system_prompt=synthesis_prompt,
            user_message=f"Synthesize the above analyses for: {query}",
        )
        total_latency += synth_latency

        vritti_result = self.vritti_filter.classify(synthesis_text, context=context)
        filtered_synthesis = self.vritti_filter.filter(synthesis_text, context=context)
        pramana_tag = self.pramana_tagger.tag(
            self._extract_first_claim(synthesis_text)
        )

        synthesis_response = DarshanaResponse(
            text=filtered_synthesis,
            raw_text=synthesis_text,
            darshana=relevant_engines,
            guna=guna.value,
            vritti=vritti_result.vritti.value,
            pramana=pramana_tag.source.value,
            confidence=vritti_result.confidence,
            reasoning=synthesis_text,
            model=self.model,
            latency_ms=synth_latency,
            input_tokens=synth_in,
            output_tokens=synth_out,
        )

        # Record in karma store
        self.karma_store.record_action(
            action=f"multi_darshana engines={','.join(relevant_engines)} guna={guna.value}",
            outcome=f"vritti={vritti_result.vritti.value} confidence={vritti_result.confidence:.2f}",
            domain="darshana_routing",
        )

        return MultiDarshanaResponse(
            synthesis=synthesis_response,
            individual=individual_responses,
            query=query,
            engines_used=relevant_engines,
            total_latency_ms=total_latency,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _call_api(
        self,
        system_prompt: str,
        user_message: str,
    ) -> tuple[str, float, int, int]:
        """
        Make a single call to the Anthropic Messages API.

        Returns:
            Tuple of (response_text, latency_ms, input_tokens, output_tokens).

        Raises:
            anthropic.APIError: On API communication failures.
        """
        start = time.monotonic()

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message},
                ],
            )
        except anthropic.APIError as e:
            latency_ms = (time.monotonic() - start) * 1000
            # Return a descriptive error message rather than crashing
            error_text = (
                f"[API ERROR] The Anthropic API returned an error: {e}\n"
                f"Model: {self.model}\n"
                f"This may indicate an invalid API key, rate limit, or model issue."
            )
            return error_text, latency_ms, 0, 0

        latency_ms = (time.monotonic() - start) * 1000

        # Extract text from the response
        response_text = ""
        for block in message.content:
            if block.type == "text":
                response_text += block.text

        input_tokens = message.usage.input_tokens if message.usage else 0
        output_tokens = message.usage.output_tokens if message.usage else 0

        return response_text, latency_ms, input_tokens, output_tokens

    def _extract_first_claim(self, text: str) -> str:
        """
        Extract the first substantial sentence from LLM output for pramana tagging.

        Skips headers, blank lines, and very short fragments to find
        a meaningful claim to tag epistemically.
        """
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            cleaned = sentence.strip().lstrip("#*-•> 0123456789.")
            if len(cleaned) > 20 and not cleaned.startswith("["):
                return cleaned
        # Fallback: return the first 200 chars
        return text[:200] if text else ""

    def _build_synthesis_prompt(
        self,
        query: str,
        responses: List[DarshanaResponse],
        guna: Guna,
    ) -> str:
        """
        Build a Vedanta-style synthesis prompt that integrates multiple
        darshana perspectives into a unified answer.

        The synthesis follows the adhyaropa-apavada method:
        1. Lay out each perspective (superimposition)
        2. Find what they share
        3. Negate the false distinctions
        4. State the unified truth
        """
        sections = []
        for resp in responses:
            engine_name = resp.darshana[0].upper()
            sections.append(
                f"## {engine_name} ANALYSIS\n"
                f"(Vritti: {resp.vritti}, Confidence: {resp.confidence:.2f})\n\n"
                f"{resp.raw_text}"
            )

        perspectives = "\n\n---\n\n".join(sections)

        return (
            "You are performing a Vedanta synthesis — finding unity beneath "
            "multiple philosophical perspectives on the same problem.\n\n"
            f"ORIGINAL QUERY: {query}\n\n"
            f"The following analyses were produced by different Darshana engines, "
            f"each applying a different reasoning framework:\n\n"
            f"{perspectives}\n\n"
            f"---\n\n"
            f"YOUR TASK: Synthesize these perspectives using the Vedanta method:\n\n"
            f"1. **AGREEMENT** — Where do the darshanas converge? What shared "
            f"conclusions emerge?\n"
            f"2. **TENSION** — Where do they diverge? What genuine trade-offs "
            f"or disagreements exist?\n"
            f"3. **NETI NETI** — What false distinctions or frame-dependent "
            f"disagreements can be dissolved?\n"
            f"4. **UNIFIED ANSWER** — State the integrated answer that honors "
            f"each perspective's insight. This is not a compromise — it is a "
            f"higher-level truth from which each perspective can be re-derived.\n\n"
            f"End with a clear, actionable recommendation for the human."
        )

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def explain_routing(self, query: str) -> str:
        """
        Show how the Buddhi layer would route a query, without calling the API.

        Useful for debugging and understanding the router's classification.
        """
        routing = self.router.route(query)
        return self.router.explain_routing(routing)

    def get_vasanas(self, domain: str = "darshana_routing") -> list:
        """
        Retrieve accumulated behavioral tendencies from the Karma store.

        Returns the vasanas (tendencies) for the specified domain,
        showing how the system's routing patterns have evolved over time.
        """
        return self.karma_store.get_vasanas(domain)

    def burn_vasanas(self, domain: Optional[str] = None) -> int:
        """
        Clear outdated behavioral biases — the jnana-agni (fire of knowledge).

        See KarmaStore.burn_vasanas() for details.
        """
        return self.karma_store.burn_vasanas(domain)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """
    Command-line interface for the Darshana LLM.

    Usage:
        python -m src "Should we rewrite our backend in Rust?"
        python -m src --multi "What is consciousness?"
        python -m src --explain "Debug this failing test"
    """
    import json

    if len(sys.argv) < 2:
        print("Usage: python -m src [--multi|--explain] \"your query here\"")
        print()
        print("Options:")
        print("  --multi    Run all relevant darshanas and synthesize")
        print("  --explain  Show routing only (no API call)")
        print("  --model    Specify model (default: claude-sonnet-4-20250514)")
        print()
        print("Environment:")
        print("  ANTHROPIC_API_KEY  Required (or pass --api-key)")
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]
    multi_mode = False
    explain_mode = False
    model = None
    api_key = None
    query_parts = []

    i = 0
    while i < len(args):
        if args[i] == "--multi":
            multi_mode = True
        elif args[i] == "--explain":
            explain_mode = True
        elif args[i] == "--model" and i + 1 < len(args):
            model = args[i + 1]
            i += 1
        elif args[i] == "--api-key" and i + 1 < len(args):
            api_key = args[i + 1]
            i += 1
        else:
            query_parts.append(args[i])
        i += 1

    query = " ".join(query_parts)
    if not query:
        print("Error: No query provided.")
        sys.exit(1)

    # Explain mode — no API call needed
    if explain_mode:
        router = DarshanaRouter()
        routing = router.route(query)
        print(router.explain_routing(routing))
        print()
        result = router.route_and_reason(query)
        for r in result.reasoning:
            print(f"\n--- {r.engine.upper()} ---")
            print(r.approach)
        sys.exit(0)

    # Initialize and run
    try:
        llm = DarshanaLLM(model=model, api_key=api_key)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if multi_mode:
        print(f"Running multi-darshana analysis on: {query}\n")
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

        print(f"Darshana: {', '.join(response.darshana)}")
        print(f"Guna:     {response.guna}")
        print(f"Vritti:   {response.vritti}")
        print(f"Pramana:  {response.pramana}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Model:    {response.model}")
        print(f"Latency:  {response.latency_ms:.0f}ms")
        print(f"Tokens:   {response.input_tokens} in / {response.output_tokens} out")
        if response.maya_gaps:
            print(f"Maya gaps: {len(response.maya_gaps)}")
            for gap in response.maya_gaps:
                print(f"  - [{gap['gap_type']}] {gap['description']}")
        print()
        print("--- RESPONSE ---")
        print(response.text)


if __name__ == "__main__":
    main()
