"""
Darshana Architecture — A Hindu Philosophical Framework for AGI

This package implements the Shaddarshana Router (Buddhi Layer), six
specialized reasoning engines, the Guna processing-mode controller,
the Pramana epistemic-provenance tagger, the Vritti output filter,
and the DarshanaLLM wrapper that ties it all together with real
Anthropic Claude API calls.

See THESIS.md at the repository root for the full architectural
description and philosophical grounding.

Quick start:

    from src import DarshanaLLM

    llm = DarshanaLLM(api_key="sk-ant-...")
    response = llm.think("Should we rewrite our backend in Rust?")
    print(response.text)
"""

from .darshana_router import (
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
)

from .darshana_llm import (
    DarshanaLLM,
    DarshanaResponse,
    MultiDarshanaResponse,
)

__version__ = "0.1.0"
__all__ = [
    # Main API
    "DarshanaLLM",
    "DarshanaResponse",
    "MultiDarshanaResponse",
    # Router layer
    "DarshanaRouter",
    "GunaEngine",
    "PramanaTagger",
    # Engines
    "NyayaEngine",
    "SamkhyaEngine",
    "YogaEngine",
    "VedantaEngine",
    "MimamsaEngine",
    "VaisheshikaEngine",
    # Enums
    "Guna",
    "Pramana",
]
