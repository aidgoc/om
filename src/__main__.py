#!/usr/bin/env python3
"""
__main__.py -- Full CLI Harness for the Darshana Architecture
=============================================================

Two modes:
    Interactive REPL:   python -m darshana
    Single query:       python -m darshana "Is this argument valid?"

See --help for all flags.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

__version__ = "0.1.0"

# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

_NO_COLOR = os.environ.get("NO_COLOR") or not sys.stdout.isatty()


def _sgr(code: str) -> str:
    return "" if _NO_COLOR else f"\033[{code}m"


class C:
    """Terminal color codes."""
    RESET   = _sgr("0")
    BOLD    = _sgr("1")
    DIM     = _sgr("2")
    ITALIC  = _sgr("3")
    ULINE   = _sgr("4")
    # foreground
    RED     = _sgr("31")
    GREEN   = _sgr("32")
    YELLOW  = _sgr("33")
    BLUE    = _sgr("34")
    MAGENTA = _sgr("35")
    CYAN    = _sgr("36")
    WHITE   = _sgr("37")
    # bright
    BRED    = _sgr("91")
    BGREEN  = _sgr("92")
    BYELLOW = _sgr("93")
    BBLUE   = _sgr("94")
    BMAGENTA= _sgr("95")
    BCYAN   = _sgr("96")
    BWHITE  = _sgr("97")
    # background
    BG_BLUE = _sgr("44")


# ---------------------------------------------------------------------------
# Box-drawing helpers
# ---------------------------------------------------------------------------

_BOX_TL = "\u250c"  # top-left
_BOX_TR = "\u2510"  # top-right
_BOX_BL = "\u2514"  # bottom-left
_BOX_BR = "\u2518"  # bottom-right
_BOX_H  = "\u2500"  # horizontal
_BOX_V  = "\u2502"  # vertical


def _box(title: str, lines: List[str], width: int = 52, color: str = C.CYAN) -> str:
    """Draw a box with a title and content lines."""
    inner = width - 4  # 2 for borders, 2 for padding
    parts: List[str] = []

    # top border with title
    label = f" {title} "
    remaining = max(0, width - 2 - len(label))
    parts.append(f"  {color}{_BOX_TL}{_BOX_H}{label}{_BOX_H * remaining}{_BOX_TR}{C.RESET}")

    # content
    for line in lines:
        # truncate if too long
        display = line[:inner]
        pad = inner - len(display)
        parts.append(f"  {color}{_BOX_V}{C.RESET} {display}{' ' * pad} {color}{_BOX_V}{C.RESET}")

    # bottom border
    parts.append(f"  {color}{_BOX_BL}{_BOX_H * (width - 2)}{_BOX_BR}{C.RESET}")
    return "\n".join(parts)


def _section_header(name: str) -> str:
    """A clearly labeled section header for darshana output."""
    return f"\n  {C.BOLD}{C.BYELLOW}[{name}]{C.RESET}"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".darshana"
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "api_key": "",
    "model": "claude-sonnet-4-20250514",
    "daily_budget": 5.0,
    "memory_path": "~/.darshana/smriti.db",
    "default_mode": "dharana",
    "max_engines": 3,
}


def _load_config() -> Dict[str, Any]:
    """Load config from ~/.darshana/config.json, creating defaults if absent."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            # Merge with defaults for any missing keys
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except (json.JSONDecodeError, OSError):
            pass

    # First run -- write defaults
    _save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def _save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def _resolve_api_key(cfg: Dict[str, Any], cli_key: Optional[str] = None) -> str:
    """Resolve API key from CLI flag > env var > config file > interactive prompt."""
    key = cli_key or os.environ.get("ANTHROPIC_API_KEY") or cfg.get("api_key", "")
    if key:
        return key

    # Interactive prompt
    print(f"\n  {C.YELLOW}No Anthropic API key found.{C.RESET}")
    print(f"  Set ANTHROPIC_API_KEY env var, or enter it now to save to config.\n")
    try:
        key = input(f"  {C.BOLD}API key:{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(1)

    if key:
        cfg["api_key"] = key
        _save_config(cfg)
        print(f"  {C.GREEN}Saved to {CONFIG_PATH}{C.RESET}\n")
        return key

    print(f"\n  {C.RED}Cannot proceed without an API key.{C.RESET}")
    print(f"  Options:")
    print(f"    export ANTHROPIC_API_KEY='sk-ant-...'")
    print(f"    Edit {CONFIG_PATH}")
    print(f"    python -m darshana --dry-run \"query\"   (no API key needed)\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Antahkarana instantiation
# ---------------------------------------------------------------------------

def _make_mind(
    cfg: Dict[str, Any],
    api_key: str,
    model: Optional[str] = None,
    no_memory: bool = False,
) -> Any:
    """Build the Antahkarana pipeline."""
    from .antahkarana import Antahkarana

    mem_path = None if no_memory else os.path.expanduser(cfg.get("memory_path", "~/.darshana/smriti.db"))
    state_path = None if no_memory else os.path.expanduser("~/.darshana/ahamkara_state.json")

    return Antahkarana(
        api_key=api_key,
        model=model or cfg.get("model", "claude-sonnet-4-20250514"),
        memory_path=mem_path,
        state_path=state_path,
        budget_daily=cfg.get("daily_budget", 5.0),
        max_engines=cfg.get("max_engines", 3),
    )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _format_response(resp: Any, show_trace: bool = False, show_budget: bool = False) -> str:
    """Format an AntahkaranaResponse for terminal display."""
    parts: List[str] = []

    # -- BUDDHI box (routing) --
    buddhi_lines = []
    if resp.darshana:
        buddhi_lines.append(f"Darshana: {', '.join(resp.darshana)}")
    if resp.guna and resp.guna != "unknown":
        guna_desc = {"sattva": "precision", "rajas": "exploration", "tamas": "retrieval"}.get(resp.guna, "")
        label = f"{resp.guna} ({guna_desc})" if guna_desc else resp.guna
        buddhi_lines.append(f"Guna: {label}")
    if resp.darshana:
        depth_label = "deep" if len(resp.darshana) == 1 else f"broad ({len(resp.darshana)} engines)"
        buddhi_lines.append(f"Depth: {depth_label}")
    if resp.model:
        buddhi_lines.append(f"Model: {resp.model}")

    if buddhi_lines:
        parts.append("")
        parts.append(_box("BUDDHI", buddhi_lines, color=C.CYAN))

    # -- Main response text --
    text = resp.text or resp.raw_text or "(no response)"
    if text:
        # If text has darshana section markers, highlight them
        formatted_lines: List[str] = []
        for line in text.split("\n"):
            formatted_lines.append(f"  {line}")
        parts.append("")
        parts.append("\n".join(formatted_lines))

    # -- VRITTI box (classification) --
    vritti_lines = []
    if resp.vritti and resp.vritti != "unknown":
        conf_str = f"{resp.confidence:.2f}" if resp.confidence else "?"
        vritti_lines.append(f"Classification: {resp.vritti} (confidence: {conf_str})")
    if resp.depth_score or resp.novelty_score != 50:
        vritti_lines.append(f"Novelty: {resp.novelty_score}/100  Depth: {resp.depth_score}/100")
    if resp.pramana and resp.pramana != "unknown":
        vritti_lines.append(f"Pramana: {resp.pramana}")
    if resp.maya_gaps:
        vritti_lines.append(f"Maya gaps: {len(resp.maya_gaps)}")
    if resp.cost > 0:
        vritti_lines.append(f"Cost: ${resp.cost:.6f}  Tokens: {resp.input_tokens}in/{resp.output_tokens}out")
    if resp.latency_ms > 0:
        vritti_lines.append(f"Latency: {resp.latency_ms:.0f}ms")

    if vritti_lines:
        parts.append("")
        parts.append(_box("VRITTI", vritti_lines, color=C.MAGENTA))

    # -- Pipeline trace --
    if show_trace and resp.pipeline_trace:
        parts.append("")
        parts.append(f"  {C.DIM}{resp.pipeline_trace.summary()}{C.RESET}")

    # -- Budget --
    if show_budget and resp.cost > 0:
        parts.append("")
        parts.append(f"  {C.DIM}Query cost: ${resp.cost:.6f}{C.RESET}")

    parts.append("")
    return "\n".join(parts)


def _format_json(resp: Any) -> str:
    """Format an AntahkaranaResponse as JSON."""
    d = resp.to_dict()
    if resp.pipeline_trace:
        d["pipeline_trace"] = resp.pipeline_trace.to_dict()
    return json.dumps(d, indent=2, default=str)


def _format_html(resp: Any, query: str) -> str:
    """Format an AntahkaranaResponse as a styled HTML report."""
    darshana_str = ", ".join(resp.darshana) if resp.darshana else "auto"
    text_html = (resp.text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>\n")

    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <title>Darshana Report</title>
    <style>
      body {{ font-family: 'Georgia', serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #222; background: #fafaf7; }}
      h1 {{ color: #5b4a3f; border-bottom: 2px solid #c4a882; padding-bottom: .3rem; }}
      .meta {{ background: #f0ebe3; border-radius: 6px; padding: 1rem; margin: 1rem 0; font-size: .9rem; }}
      .meta dt {{ font-weight: bold; color: #5b4a3f; }}
      .meta dd {{ margin: 0 0 .5rem 0; }}
      .response {{ white-space: pre-wrap; line-height: 1.6; background: #fff; padding: 1.5rem; border-radius: 6px; border: 1px solid #e0d8cc; }}
      .footer {{ font-size: .8rem; color: #888; margin-top: 2rem; text-align: center; }}
    </style>
    </head>
    <body>
    <h1>Darshana Report</h1>
    <p><em>Query: {query.replace('<', '&lt;')}</em></p>
    <div class="meta">
    <dl>
      <dt>Darshana</dt><dd>{darshana_str}</dd>
      <dt>Guna</dt><dd>{resp.guna}</dd>
      <dt>Vritti</dt><dd>{resp.vritti} (confidence: {resp.confidence:.2f})</dd>
      <dt>Pramana</dt><dd>{resp.pramana}</dd>
      <dt>Depth / Novelty</dt><dd>{resp.depth_score}/100 / {resp.novelty_score}/100</dd>
      <dt>Model</dt><dd>{resp.model}</dd>
      <dt>Cost</dt><dd>${resp.cost:.6f} ({resp.input_tokens}in / {resp.output_tokens}out)</dd>
    </dl>
    </div>
    <div class="response">{text_html}</div>
    <div class="footer">Generated by Darshana v{__version__}</div>
    </body>
    </html>
    """)


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------

def _dry_run(query: str, mode: Optional[str] = None, force_darshana: Optional[str] = None) -> None:
    """Show routing classification without calling the LLM."""
    from .darshana_router import DarshanaRouter

    router = DarshanaRouter(max_engines=3)
    routing = router.route(query)

    if force_darshana:
        if force_darshana not in router.engines:
            print(f"\n  {C.RED}Unknown darshana: '{force_darshana}'{C.RESET}")
            print(f"  Available: {', '.join(router.engines.keys())}\n")
            sys.exit(1)
        routing.top_engines = [force_darshana]

    if mode == "deep":
        routing.top_engines = routing.top_engines[:1]
    elif mode == "broad":
        sorted_engines = sorted(routing.engine_scores.items(), key=lambda x: x[1], reverse=True)
        routing.top_engines = [n for n, _ in sorted_engines[:4]]

    # Routing box
    rbox_lines = [
        f"Engines: {', '.join(routing.top_engines)}",
        f"Guna: {routing.guna.value}",
        f"Mode: {mode or 'auto (dharana)'}",
    ]
    print()
    print(_box("DRY RUN -- Buddhi Routing", rbox_lines, width=56, color=C.YELLOW))

    # Scores
    print(f"\n  {C.BOLD}Engine Scores:{C.RESET}")
    for engine, score in sorted(routing.engine_scores.items(), key=lambda x: x[1], reverse=True):
        bar_len = int(score * 30)
        marker = f"{C.BGREEN}*{C.RESET}" if engine in routing.top_engines else " "
        bar = f"{C.GREEN}{'=' * bar_len}{C.RESET}{'.' * (30 - bar_len)}"
        print(f"  {marker} {engine:14s} {bar} {score:.3f}")

    # What would happen
    print(f"\n  {C.DIM}No LLM call made. Use without --dry-run to get a full response.{C.RESET}\n")


# ---------------------------------------------------------------------------
# Interactive REPL
# ---------------------------------------------------------------------------

_HELP_TEXT = f"""
  {C.BOLD}Darshana REPL Commands:{C.RESET}

  {C.CYAN}/think <query>{C.RESET}      Process a query (same as just typing)
  {C.CYAN}/deep <query>{C.RESET}       Deep analysis (dhyana mode, single engine)
  {C.CYAN}/broad <query>{C.RESET}      Broad analysis (pratyahara mode, multi-engine)

  {C.CYAN}/teach <fact>{C.RESET}       Store a memory / knowledge claim
  {C.CYAN}/recall <topic>{C.RESET}     Search memories about a topic
  {C.CYAN}/forget <domain>{C.RESET}    Clear memories for a domain

  {C.CYAN}/introspect{C.RESET}         Full self-report (knowledge, vasanas, guna)
  {C.CYAN}/trace{C.RESET}              Show pipeline trace of last query
  {C.CYAN}/budget{C.RESET}             Show Shakti report (spend, remaining)
  {C.CYAN}/guna{C.RESET}               Show current guna balance

  {C.CYAN}/mode <name>{C.RESET}        Set default mode (pratyahara | dharana | dhyana)
  {C.CYAN}/darshana <name>{C.RESET}    Force a specific darshana for next query
  {C.CYAN}/model <name>{C.RESET}       Switch model

  {C.CYAN}/export <file>{C.RESET}      Export last response (as .md, .html, or .json)
  {C.CYAN}/history{C.RESET}            Show conversation history
  {C.CYAN}/clear{C.RESET}              Clear conversation history

  {C.CYAN}/help{C.RESET}               Show this message
  {C.CYAN}/quit{C.RESET} or {C.CYAN}/exit{C.RESET}     Exit

  Or just type a question to think about it.
"""


def _repl(cfg: Dict[str, Any], cli_model: Optional[str] = None, cli_key: Optional[str] = None) -> None:
    """Run the interactive REPL."""

    # Setup readline for history/editing
    try:
        import readline
        hist_path = CONFIG_DIR / "history"
        if hist_path.exists():
            readline.read_history_file(str(hist_path))
        readline.set_history_length(500)
    except (ImportError, OSError):
        readline = None  # type: ignore[assignment]

    # Resolve API key
    api_key = _resolve_api_key(cfg, cli_key)

    # Build pipeline
    model = cli_model or cfg.get("model", "claude-sonnet-4-20250514")
    try:
        mind = _make_mind(cfg, api_key, model=model)
    except Exception as e:
        print(f"\n  {C.RED}Failed to initialize Antahkarana: {e}{C.RESET}")
        print(f"  Try: python -m darshana --dry-run \"your query\"\n")
        sys.exit(1)

    # State
    history: List[Dict[str, str]] = []
    last_response: Any = None
    last_query: str = ""
    forced_darshana: Optional[str] = None
    default_mode: str = cfg.get("default_mode", "dharana")

    # Banner
    print(f"""
  {C.BOLD}{C.BYELLOW}DARSHANA{C.RESET} {C.DIM}v{__version__}{C.RESET} {C.DIM}-- The Darshana Architecture{C.RESET}
  {C.DIM}Type a question to think. Type /help for commands.{C.RESET}
""")

    def _do_think(query: str, mode: Optional[str] = None) -> None:
        nonlocal last_response, last_query, forced_darshana

        if not query.strip():
            return

        last_query = query

        # Determine effective mode
        effective_mode = mode
        if effective_mode is None and default_mode == "dhyana":
            effective_mode = "deep"
        elif effective_mode is None and default_mode == "pratyahara":
            effective_mode = "broad"

        # Show spinner hint
        print(f"\n  {C.DIM}Thinking...{C.RESET}", end="", flush=True)

        try:
            if effective_mode == "deep":
                resp = mind.think_deep(query)
            elif effective_mode == "broad":
                resp = mind.think_broad(query)
            else:
                resp = mind.think(query)
        except Exception as e:
            print(f"\r  {C.RED}Error: {e}{C.RESET}")
            print(f"  {C.DIM}Try --dry-run to test routing without API calls.{C.RESET}\n")
            return

        # Clear spinner
        print(f"\r{' ' * 40}\r", end="")

        last_response = resp
        forced_darshana = None

        # Record in history
        history.append({"role": "user", "content": query})
        history.append({"role": "darshana", "content": resp.text or ""})

        # Display
        print(_format_response(resp))

    def _do_teach(fact: str) -> None:
        if not fact.strip():
            print(f"  {C.YELLOW}Usage: /teach <fact to remember>{C.RESET}")
            return
        result = mind.teach(fact)
        print(f"\n  {C.GREEN}{result}{C.RESET}\n")

    def _do_recall(topic: str) -> None:
        if not topic.strip():
            print(f"  {C.YELLOW}Usage: /recall <topic>{C.RESET}")
            return
        result = mind.what_do_i_know(topic)
        claims = result.get("claims", [])
        if claims:
            print(f"\n  {C.BOLD}Knowledge about '{topic}':{C.RESET}")
            for cl in claims:
                conf = cl.get("confidence", 0)
                pram = cl.get("pramana", "?")
                print(f"  {C.DIM}[{pram}, conf={conf:.2f}]{C.RESET} {cl.get('claim', '')}")
        else:
            print(f"\n  {C.DIM}No knowledge found about '{topic}'.{C.RESET}")

        gaps = result.get("gaps", [])
        if gaps:
            print(f"\n  {C.YELLOW}Knowledge gaps:{C.RESET}")
            for g in gaps:
                print(f"    - {g}")
        print()

    def _do_forget(domain: str) -> None:
        if not domain.strip():
            print(f"  {C.YELLOW}Usage: /forget <domain>{C.RESET}")
            return
        result = mind.forget(domain=domain)
        print(f"\n  {C.GREEN}{result}{C.RESET}\n")

    def _do_introspect() -> None:
        report = mind.introspect()
        print(f"\n  {C.BOLD}Introspection Report:{C.RESET}")
        print(f"  Interactions: {report.get('interaction_count', 0)}")
        print(f"  Model: {report.get('model', '?')}")

        budget = report.get("budget", {})
        if budget:
            print(f"\n  {C.BOLD}Budget:{C.RESET}")
            print(f"    Daily limit:  ${budget.get('daily_limit', 0):.2f}")
            print(f"    Spent today:  ${budget.get('spent_today', 0):.4f}")
            print(f"    Remaining:    ${budget.get('remaining', 0):.4f}")

        modules = report.get("modules", {})
        if modules:
            print(f"\n  {C.BOLD}Modules:{C.RESET}")
            for mod, avail in modules.items():
                icon = f"{C.GREEN}ON{C.RESET}" if avail else f"{C.RED}OFF{C.RESET}"
                print(f"    {mod:16s} {icon}")

        ahamkara = report.get("ahamkara", {})
        if ahamkara:
            kc = ahamkara.get("knowledge_claims", 0)
            attempts = ahamkara.get("total_attempts", 0)
            vasanas = ahamkara.get("vasana_count", 0)
            guna_balance = ahamkara.get("guna_balance", {})
            print(f"\n  {C.BOLD}Ahamkara:{C.RESET}")
            print(f"    Knowledge claims: {kc}")
            print(f"    Total attempts:   {attempts}")
            print(f"    Vasanas:          {vasanas}")
            if guna_balance:
                print(f"    Guna balance:     sattva={guna_balance.get('sattva', 0):.2f}  "
                      f"rajas={guna_balance.get('rajas', 0):.2f}  "
                      f"tamas={guna_balance.get('tamas', 0):.2f}")
        print()

    def _do_trace() -> None:
        trace = mind.pipeline_trace()
        if not trace:
            print(f"\n  {C.DIM}No pipeline trace yet. Run a query first.{C.RESET}\n")
            return
        print(f"\n  {C.BOLD}Pipeline Trace:{C.RESET}")
        for step in trace.steps:
            icons = {"completed": f"{C.GREEN}+{C.RESET}", "skipped": f"{C.DIM}-{C.RESET}",
                     "degraded": f"{C.YELLOW}~{C.RESET}", "failed": f"{C.RED}!{C.RESET}"}
            icon = icons.get(step.status, "?")
            ms = f"{step.duration_ms:.0f}ms" if step.duration_ms else ""
            print(f"  [{icon}] {step.name:20s} {step.status:10s} {ms:>8s}  {C.DIM}{step.detail}{C.RESET}")
        print(f"\n  {C.DIM}Total: {trace.total_duration_ms:.0f}ms{C.RESET}\n")

    def _do_budget() -> None:
        report = mind.budget_remaining()
        print()
        blines = [
            f"Daily limit:   ${report['daily_limit']:.2f}",
            f"Spent today:   ${report['spent_today']:.6f}",
            f"Remaining:     ${report['remaining']:.6f}",
            f"Utilization:   {report['utilization_pct']:.1f}%",
        ]
        print(_box("SHAKTI", blines, color=C.YELLOW))
        print()

    def _do_guna() -> None:
        report = mind.introspect()
        ahamkara = report.get("ahamkara", {})
        guna_balance = ahamkara.get("guna_balance", {})
        if guna_balance:
            s = guna_balance.get("sattva", 0)
            r = guna_balance.get("rajas", 0)
            t = guna_balance.get("tamas", 0)
            print(f"\n  {C.BOLD}Guna Balance:{C.RESET}")
            print(f"    Sattva (precision):   {'=' * int(s * 30):<30s} {s:.2f}")
            print(f"    Rajas  (exploration): {'=' * int(r * 30):<30s} {r:.2f}")
            print(f"    Tamas  (retrieval):   {'=' * int(t * 30):<30s} {t:.2f}")
        else:
            print(f"\n  {C.DIM}Guna balance not available (Ahamkara module may be inactive).{C.RESET}")
        print()

    def _do_export(arg: str) -> None:
        nonlocal last_response, last_query
        if not last_response:
            print(f"  {C.YELLOW}No response to export. Run a query first.{C.RESET}\n")
            return
        if not arg.strip():
            print(f"  {C.YELLOW}Usage: /export <filename.md|.html|.json>{C.RESET}\n")
            return

        filepath = Path(arg.strip()).expanduser()
        ext = filepath.suffix.lower()

        try:
            if ext == ".json":
                content = _format_json(last_response)
            elif ext == ".html":
                content = _format_html(last_response, last_query)
            else:
                # Default to markdown
                content = f"# Darshana Report\n\n"
                content += f"**Query:** {last_query}\n\n"
                content += f"**Darshana:** {', '.join(last_response.darshana)}\n"
                content += f"**Guna:** {last_response.guna}\n"
                content += f"**Vritti:** {last_response.vritti} (confidence: {last_response.confidence:.2f})\n"
                content += f"**Pramana:** {last_response.pramana}\n\n"
                content += f"---\n\n{last_response.text}\n"

            with open(filepath, "w") as f:
                f.write(content)
            print(f"  {C.GREEN}Exported to {filepath}{C.RESET}\n")
        except OSError as e:
            print(f"  {C.RED}Export failed: {e}{C.RESET}\n")

    def _do_history() -> None:
        if not history:
            print(f"\n  {C.DIM}No conversation history yet.{C.RESET}\n")
            return
        print(f"\n  {C.BOLD}Conversation History:{C.RESET}")
        for i, entry in enumerate(history):
            role = entry["role"]
            text = entry["content"][:120]
            if role == "user":
                print(f"  {C.CYAN}{i+1}. You:{C.RESET} {text}")
            else:
                print(f"  {C.MAGENTA}{i+1}. Darshana:{C.RESET} {text}{'...' if len(entry['content']) > 120 else ''}")
        print()

    # REPL loop
    try:
        while True:
            try:
                line = input(f"  {C.BOLD}{C.BYELLOW}darshana>{C.RESET} ").strip()
            except EOFError:
                print()
                break

            if not line:
                continue

            # Parse commands
            if line.startswith("/"):
                parts = line.split(None, 1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if cmd in ("/quit", "/exit", "/q"):
                    break
                elif cmd == "/help":
                    print(_HELP_TEXT)
                elif cmd == "/think":
                    _do_think(arg)
                elif cmd == "/deep":
                    _do_think(arg, mode="deep")
                elif cmd == "/broad":
                    _do_think(arg, mode="broad")
                elif cmd == "/teach":
                    _do_teach(arg)
                elif cmd == "/recall":
                    _do_recall(arg)
                elif cmd == "/forget":
                    _do_forget(arg)
                elif cmd == "/introspect":
                    _do_introspect()
                elif cmd == "/trace":
                    _do_trace()
                elif cmd == "/budget":
                    _do_budget()
                elif cmd == "/guna":
                    _do_guna()
                elif cmd == "/mode":
                    arg = arg.strip().lower()
                    if arg in ("pratyahara", "dharana", "dhyana"):
                        default_mode = arg
                        print(f"\n  {C.GREEN}Default mode set to: {default_mode}{C.RESET}\n")
                    else:
                        print(f"  {C.YELLOW}Usage: /mode <pratyahara | dharana | dhyana>{C.RESET}\n")
                elif cmd == "/darshana":
                    dname = arg.strip().lower()
                    if dname:
                        forced_darshana = dname
                        print(f"\n  {C.GREEN}Next query will use darshana: {dname}{C.RESET}\n")
                    else:
                        forced_darshana = None
                        print(f"  {C.DIM}Darshana override cleared. Auto-routing resumed.{C.RESET}\n")
                elif cmd == "/model":
                    new_model = arg.strip()
                    if new_model:
                        model = new_model
                        try:
                            mind = _make_mind(cfg, api_key, model=model)
                            print(f"\n  {C.GREEN}Model switched to: {model}{C.RESET}\n")
                        except Exception as e:
                            print(f"  {C.RED}Failed to reinitialize with model {model}: {e}{C.RESET}\n")
                    else:
                        print(f"  {C.DIM}Current model: {model}{C.RESET}\n")
                elif cmd == "/export":
                    _do_export(arg)
                elif cmd == "/history":
                    _do_history()
                elif cmd == "/clear":
                    history.clear()
                    last_response = None
                    last_query = ""
                    print(f"\n  {C.GREEN}Conversation cleared.{C.RESET}\n")
                else:
                    print(f"  {C.YELLOW}Unknown command: {cmd}. Type /help for available commands.{C.RESET}\n")
            else:
                # Bare text -> think
                _do_think(line)

    except KeyboardInterrupt:
        print()
    finally:
        # Save readline history
        try:
            if readline is not None:
                readline.write_history_file(str(CONFIG_DIR / "history"))
        except (OSError, NameError):
            pass

    print(f"\n  {C.DIM}Namaste.{C.RESET}\n")


# ---------------------------------------------------------------------------
# Single-query mode
# ---------------------------------------------------------------------------

def _single_query(
    query: str,
    cfg: Dict[str, Any],
    api_key: str,
    mode: Optional[str] = None,
    model: Optional[str] = None,
    force_darshana: Optional[str] = None,
    output_json: bool = False,
    output_html: bool = False,
    show_trace: bool = False,
    no_memory: bool = False,
    show_budget: bool = False,
) -> None:
    """Run a single query and print the result."""
    try:
        mind = _make_mind(cfg, api_key, model=model, no_memory=no_memory)
    except Exception as e:
        print(f"\n  {C.RED}Failed to initialize: {e}{C.RESET}", file=sys.stderr)
        sys.exit(1)

    try:
        if mode == "deep":
            resp = mind.think_deep(query)
        elif mode == "broad":
            resp = mind.think_broad(query)
        else:
            resp = mind.think(query)
    except Exception as e:
        print(f"\n  {C.RED}Error: {e}{C.RESET}", file=sys.stderr)
        print(f"  {C.DIM}Try: python -m darshana --dry-run \"{query}\"{C.RESET}", file=sys.stderr)
        sys.exit(1)

    # Output
    if output_json:
        print(_format_json(resp))
    elif output_html:
        print(_format_html(resp, query))
    else:
        print(_format_response(resp, show_trace=show_trace, show_budget=show_budget))


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="darshana",
        description=(
            "The Darshana Architecture -- Hindu philosophical reasoning "
            "framework.\n\n"
            "Routes queries through six classical reasoning engines "
            "(Nyaya, Samkhya, Yoga, Vedanta, Mimamsa, Vaisheshika), "
            "classifies processing mode via the three Gunas, and tags "
            "knowledge claims with their Pramana (epistemic source)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            The six darshanas:
              nyaya        Logic, proof chains, fallacy detection
              samkhya      Decomposition, classification, enumeration
              yoga         Noise filtering, focus, relevance ranking
              vedanta      Contradiction resolution, synthesis
              mimamsa      Text interpretation, action extraction
              vaisheshika  Atomic analysis, root cause, ontology

            Modes:
              dharana      Default balanced mode (auto routing)
              dhyana       Deep focus (single engine, max depth)
              pratyahara   Broad withdrawal (multi-engine, Yaksha Protocol)

            Examples:
              darshana                                    # interactive REPL
              darshana "Is this argument valid?"          # single query
              darshana --deep "Break down the auth system"
              darshana --broad "Should we pivot to B2C?"
              darshana --json "query" > output.json
              darshana --dry-run "query"                  # routing only, no API
        """),
    )

    parser.add_argument(
        "query", nargs="?", default=None,
        help="Query to process. If omitted, starts the interactive REPL.",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--deep", action="store_true",
        help="Deep analysis: dhyana mode, single darshana, maximum depth.",
    )
    mode_group.add_argument(
        "--broad", action="store_true",
        help="Broad analysis: pratyahara mode, multi-darshana, Yaksha Protocol.",
    )

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json", action="store_true",
        help="Output as structured JSON.",
    )
    output_group.add_argument(
        "--html", action="store_true",
        help="Output as a styled HTML report.",
    )

    parser.add_argument(
        "--darshana", metavar="NAME",
        help="Force routing to a specific darshana engine.",
    )
    parser.add_argument(
        "--trace", action="store_true",
        help="Include the full pipeline trace in output.",
    )
    parser.add_argument(
        "--no-memory", action="store_true",
        help="Do not use or store memories for this query.",
    )
    parser.add_argument(
        "--budget", action="store_true",
        help="Show cost/budget info after the response.",
    )
    parser.add_argument(
        "--model", metavar="MODEL",
        help="Override the model (e.g. claude-sonnet-4-20250514, claude-haiku-4-20250514).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show routing classification only -- no LLM call, no API key needed.",
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="Disable colored output.",
    )
    parser.add_argument(
        "--api-key", metavar="KEY",
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var or config).",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"darshana {__version__}",
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point for the Darshana Architecture."""
    parser = _build_parser()
    args = parser.parse_args()

    # Handle --no-color globally
    global _NO_COLOR
    if args.no_color:
        _NO_COLOR = True
        # Rebuild color constants
        for attr in dir(C):
            if not attr.startswith("_"):
                setattr(C, attr, "")

    # Load config
    cfg = _load_config()

    # Dry-run mode (no API key needed)
    if args.dry_run:
        if not args.query:
            print(f"\n  {C.RED}--dry-run requires a query.{C.RESET}")
            print(f"  Usage: python -m darshana --dry-run \"your query\"\n")
            sys.exit(1)
        mode = "deep" if args.deep else ("broad" if args.broad else None)
        _dry_run(args.query, mode=mode, force_darshana=args.darshana)
        return

    # Single query mode
    if args.query:
        api_key = _resolve_api_key(cfg, args.api_key)
        mode = "deep" if args.deep else ("broad" if args.broad else None)
        _single_query(
            query=args.query,
            cfg=cfg,
            api_key=api_key,
            mode=mode,
            model=args.model,
            force_darshana=args.darshana,
            output_json=args.json,
            output_html=args.html,
            show_trace=args.trace,
            no_memory=args.no_memory,
            show_budget=args.budget,
        )
        return

    # Interactive REPL (default)
    _repl(cfg, cli_model=args.model, cli_key=args.api_key)


if __name__ == "__main__":
    main()
