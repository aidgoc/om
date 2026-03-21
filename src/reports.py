"""
reports.py -- HTML Report Generator for the Darshana Architecture
=================================================================

    "The eye cannot see itself. It needs a mirror."

This module transforms structured responses from the Darshana Architecture
into self-contained, beautiful HTML reports. No external dependencies.
No Jinja, no npm, no CDN. Every report is a single .html file you can
open in any browser, email to a client, or archive for later.

Four report types:

    DarshanaReport      -- single-engine response (Antahkarana pipeline)
    YakshaReport        -- multi-darshana parallel analysis
    IntrospectionReport -- Ahamkara self-assessment
    ShaktiReport        -- budget and compute usage

Each report class has two methods:
    .generate(data) -> str          Returns HTML string
    .save(data, path) -> Path       Writes HTML to file and returns path

All styling is inline (CSS variables in <style> block). All reports are
responsive, dark-themed, and designed to look good enough to share.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import html
import os
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# Color palette and design tokens
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#0a0a0a",
    "card": "#141414",
    "border": "#2a2a2a",
    "text": "#e0e0e0",
    "muted": "#888",
    "accent": "#f59e0b",    # amber
    "accent2": "#8b5cf6",   # purple
    "red": "#ef4444",
    "green": "#22c55e",
    "blue": "#3b82f6",
    "cyan": "#06b6d4",
    "orange": "#f97316",
}

# Darshana-specific colors for cards
DARSHANA_COLORS = {
    "vaisheshika": "#f97316",   # orange — atomic decomposition
    "samkhya":     "#06b6d4",   # cyan — enumeration
    "nyaya":       "#3b82f6",   # blue — logic
    "yoga":        "#22c55e",   # green — signal/noise
    "mimamsa":     "#f59e0b",   # amber — action
    "vedanta":     "#8b5cf6",   # purple — synthesis
}

DARSHANA_DESCRIPTIONS = {
    "vaisheshika": "Irreducible Components",
    "samkhya":     "Layer Enumeration",
    "nyaya":       "Logical Analysis",
    "yoga":        "Signal vs Noise",
    "mimamsa":     "Actionable Commands",
    "vedanta":     "Synthesis",
}

# Vritti classification colors
VRITTI_COLORS = {
    "pramana":   "#22c55e",
    "viparyaya": "#ef4444",
    "vikalpa":   "#f59e0b",
    "nidra":     "#ef4444",
    "smriti":    "#3b82f6",
    "unknown":   "#888",
}

# Pramana type labels
PRAMANA_LABELS = {
    "pratyaksha": "Direct Perception",
    "anumana":    "Inference",
    "upamana":    "Analogy",
    "shabda":     "Testimony/Authority",
    "arthapatti":  "Postulation",
    "anupalabdhi": "Non-apprehension",
    "unknown":     "Unclassified",
}


# ---------------------------------------------------------------------------
# Base CSS — shared across all reports
# ---------------------------------------------------------------------------

BASE_CSS = """
:root {
  --bg: %(bg)s;
  --card: %(card)s;
  --border: %(border)s;
  --text: %(text)s;
  --muted: %(muted)s;
  --accent: %(accent)s;
  --accent2: %(accent2)s;
  --red: %(red)s;
  --green: %(green)s;
  --blue: %(blue)s;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Georgia', serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  padding: 2rem;
  max-width: 920px;
  margin: 0 auto;
}

@media (max-width: 640px) {
  body { padding: 1rem; }
  h1 { font-size: 1.5rem; }
}

h1 {
  font-size: 2rem;
  color: var(--accent);
  border-bottom: 2px solid var(--accent);
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--muted);
  font-style: italic;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

h2 {
  font-size: 1.3rem;
  color: var(--accent2);
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

h2 .tag {
  font-size: 0.7rem;
  background: var(--accent2);
  color: #fff;
  padding: 2px 8px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

h3 {
  font-size: 1.05rem;
  color: var(--text);
  margin-top: 1.2rem;
  margin-bottom: 0.6rem;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.card-accent {
  border-left: 3px solid var(--accent);
}

.routing-bar {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  margin-top: 0.8rem;
}

.routing-item {
  background: var(--border);
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-family: monospace;
}

.routing-item.active {
  background: var(--accent);
  color: #000;
  font-weight: bold;
}

.routing-item.purple {
  background: var(--accent2);
  color: #fff;
}

table {
  width: 100%%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}

th {
  text-align: left;
  padding: 0.6rem;
  border-bottom: 2px solid var(--accent);
  color: var(--accent);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

td {
  padding: 0.6rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}

tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.synthesis-box {
  background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(139,92,246,0.08));
  border: 1px solid var(--accent);
  padding: 1.5rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.signal-box {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--green);
  padding: 1.2rem;
  border-radius: 8px;
  margin: 1rem 0;
  text-align: center;
  font-size: 1.05rem;
  font-weight: bold;
  color: var(--green);
}

.warning-box {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--red);
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.9rem;
}

.maya-box {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid var(--accent2);
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.9rem;
}

blockquote {
  border-left: 3px solid var(--accent);
  padding: 0.8rem 1.2rem;
  margin: 1rem 0;
  background: rgba(245, 158, 11, 0.05);
  font-style: italic;
}

.mono {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 0.85rem;
}

code {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  background: var(--border);
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-size: 0.85rem;
}

pre {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  background: #1a1a2e;
  padding: 1.2rem;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.6;
  margin: 1rem 0;
}

/* Guna bar chart */
.guna-bar-container {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin: 0.4rem 0;
}

.guna-label {
  width: 70px;
  font-family: monospace;
  font-size: 0.85rem;
  text-align: right;
}

.guna-track {
  flex: 1;
  height: 24px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.guna-fill {
  height: 100%%;
  border-radius: 4px;
  transition: width 0.3s;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 6px;
  font-size: 0.7rem;
  font-family: monospace;
  color: #000;
  font-weight: bold;
}

.guna-sattva { background: var(--green); }
.guna-rajas { background: var(--accent); }
.guna-tamas { background: var(--red); }

/* Pie chart (CSS-only conic gradient) */
.pie-chart {
  width: 180px;
  height: 180px;
  border-radius: 50%%;
  margin: 1rem auto;
}

.pie-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin-top: 0.8rem;
  font-size: 0.8rem;
  font-family: monospace;
}

.pie-legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.pie-swatch {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  display: inline-block;
}

/* Action items */
.action-vidhi {
  color: var(--green);
  font-weight: bold;
}

.action-nishiddha {
  color: var(--red);
  font-weight: bold;
}

.action-arthavada {
  color: var(--accent);
  font-weight: bold;
}

/* Progress bar */
.progress-track {
  width: 100%%;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
  margin: 0.5rem 0;
}

.progress-fill {
  height: 100%%;
  border-radius: 4px;
}

/* Badge */
.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 3px;
  font-size: 0.75rem;
  font-family: monospace;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: bold;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.stat-box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  font-family: monospace;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 0.3rem;
}

/* Darshana card with colored border */
.darshana-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-top: 3px solid var(--accent2);
}

.darshana-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.darshana-name {
  font-size: 1.15rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.confidence-badge {
  font-family: monospace;
  font-size: 0.8rem;
  padding: 0.2rem 0.6rem;
  border-radius: 3px;
}

footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.8rem;
  text-align: center;
}

footer a { color: var(--accent); text-decoration: none; }

.om { font-size: 1.5rem; }
""" % COLORS


# ---------------------------------------------------------------------------
# HTML wrapper
# ---------------------------------------------------------------------------

def _wrap_html(title: str, body: str, timestamp: Optional[str] = None) -> str:
    """Wrap body content in a complete HTML document."""
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title)}</title>
<style>
{BASE_CSS}
</style>
</head>
<body>
{body}
<footer>
  <p><span class="om">&#x1F549;</span> Generated by the <a href="https://github.com/aidgoc/om">Darshana Architecture</a></p>
  <p style="margin-top: 0.3rem;">{_esc(ts)}</p>
  <p style="margin-top: 0.5rem;">By Harshwardhan (HNG) &mdash; MIT License</p>
  <p style="margin-top: 1rem; font-style: italic; color: var(--accent);">
    &#x090F;&#x0915;&#x0902; &#x0938;&#x0926;&#x094D; &#x0935;&#x093F;&#x092A;&#x094D;&#x0930;&#x093E; &#x092C;&#x0939;&#x0941;&#x0927;&#x093E; &#x0935;&#x0926;&#x0928;&#x094D;&#x0924;&#x093F;<br>
    &ldquo;Truth is one. The wise call it by many names.&rdquo;<br>
    <span style="color: var(--muted);">&mdash; Rig Veda 1.164.46</span>
  </p>
</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """HTML-escape text."""
    if text is None:
        return ""
    return html.escape(str(text))


def _format_content(text: str) -> str:
    """
    Convert plain text to HTML paragraphs.
    Respects blank-line paragraph breaks, preserves line breaks.
    """
    if not text:
        return ""
    paragraphs = text.strip().split("\n\n")
    parts = []
    for para in paragraphs:
        lines = para.strip().split("\n")
        escaped = "<br>\n".join(_esc(line) for line in lines)
        parts.append(f"<p>{escaped}</p>")
    return "\n".join(parts)


def _format_usd(amount: float) -> str:
    """Format a USD amount."""
    if amount < 0.01:
        return f"${amount:.4f}"
    return f"${amount:.2f}"


def _pct(value: float, total: float) -> float:
    """Safe percentage calculation."""
    if total <= 0:
        return 0.0
    return (value / total) * 100


def _color_for_confidence(conf: float) -> str:
    """Return a color based on confidence level."""
    if conf >= 0.8:
        return COLORS["green"]
    elif conf >= 0.5:
        return COLORS["accent"]
    else:
        return COLORS["red"]


def _vritti_color(vritti: str) -> str:
    """Return color for a vritti classification."""
    return VRITTI_COLORS.get(vritti.lower(), COLORS["muted"])


# ---------------------------------------------------------------------------
# Component builders — reusable HTML fragments
# ---------------------------------------------------------------------------

def _build_routing_header(
    darshanas: List[str],
    guna: str = "unknown",
    depth: int = 0,
    extra_items: Optional[List[str]] = None,
) -> str:
    """Build the Buddhi routing decision header card."""
    items = []

    # Guna badge
    guna_class = "active" if guna.lower() in ("rajas", "sattva") else ""
    items.append(f'<span class="routing-item {guna_class}">Guna: {_esc(guna.upper())}</span>')

    # Darshana badges
    if len(darshanas) == 1:
        items.append(f'<span class="routing-item active">Engine: {_esc(darshanas[0].upper())}</span>')
    else:
        items.append(f'<span class="routing-item active">Engines: {len(darshanas)}</span>')

    # Depth
    if depth > 0:
        items.append(f'<span class="routing-item">Depth: {depth}/100</span>')

    # Extra items
    if extra_items:
        for item in extra_items:
            items.append(f'<span class="routing-item">{_esc(item)}</span>')

    return f"""<div class="card">
  <strong style="color: var(--accent);">BUDDHI (Routing Decision)</strong>
  <div class="routing-bar">
    {"".join(items)}
  </div>
</div>"""


def _build_vritti_box(vritti: str, pramana: str, self_check: Optional[Dict] = None) -> str:
    """Build the vritti classification box."""
    v_color = _vritti_color(vritti)
    p_label = PRAMANA_LABELS.get(pramana.lower(), pramana)

    rows = ""
    if self_check:
        for claim, check in self_check.items():
            if isinstance(check, dict):
                v = check.get("vritti", "unknown")
                p = check.get("pramana", "unknown")
                vc = _vritti_color(v)
                rows += f"""<tr>
  <td>{_esc(claim)}</td>
  <td style="color: {vc}; font-family: monospace;">{_esc(v.upper())}</td>
  <td style="font-family: monospace;">{_esc(p)}</td>
</tr>"""
            else:
                rows += f"""<tr>
  <td>{_esc(claim)}</td>
  <td colspan="2" style="font-family: monospace;">{_esc(str(check))}</td>
</tr>"""

    self_check_html = ""
    if rows:
        self_check_html = f"""
<table style="margin-top: 1rem;">
  <tr><th>Claim</th><th>Vritti</th><th>Pramana</th></tr>
  {rows}
</table>"""

    return f"""<div class="card">
  <div style="display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
    <div>
      <span style="color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Vritti Classification</span><br>
      <span class="badge" style="background: {v_color}; color: #000; font-size: 0.9rem; margin-top: 0.3rem;">{_esc(vritti.upper())}</span>
    </div>
    <div>
      <span style="color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Pramana</span><br>
      <span style="font-family: monospace; font-size: 0.95rem;">{_esc(p_label)}</span>
    </div>
  </div>
  {self_check_html}
</div>"""


def _build_darshana_card(
    name: str,
    approach: str,
    reasoning: str,
    conclusion: str,
    confidence: float,
    pramana: str,
    number: int = 0,
    metadata: Optional[Dict] = None,
) -> str:
    """Build a styled card for a single darshana's analysis."""
    color = DARSHANA_COLORS.get(name.lower(), COLORS["accent2"])
    desc = DARSHANA_DESCRIPTIONS.get(name.lower(), "")
    conf_color = _color_for_confidence(confidence)
    p_label = PRAMANA_LABELS.get(pramana.lower(), pramana)

    # Number tag
    num_html = ""
    if number > 0:
        num_html = f'<span class="tag" style="background: {color};">{number}</span> '

    # Subtitle
    desc_html = f' &mdash; {_esc(desc)}' if desc else ""

    # Metadata badges
    meta_html = ""
    if metadata:
        badges = []
        for k, v in metadata.items():
            badges.append(f'<span class="routing-item" style="font-size: 0.75rem;">{_esc(k)}: {_esc(str(v))}</span>')
        meta_html = f'<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">{"".join(badges)}</div>'

    return f"""<h2>{num_html}{_esc(name.upper())}{desc_html}</h2>
<div class="darshana-card" style="border-top-color: {color};">
  <div class="darshana-card-header">
    <div>
      <span style="color: var(--muted); font-size: 0.85rem;">Approach: {_esc(approach)}</span>
    </div>
    <div style="display: flex; gap: 0.8rem; align-items: center;">
      <span class="confidence-badge" style="background: {conf_color}; color: #000;">
        {confidence:.0%} confidence
      </span>
      <span style="font-family: monospace; font-size: 0.8rem; color: var(--muted);">{_esc(p_label)}</span>
    </div>
  </div>
  {_format_content(reasoning)}
  <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid var(--border);">
    <strong>Conclusion:</strong> {_esc(conclusion)}
  </div>
  {meta_html}
</div>"""


def _build_synthesis_box(synthesis: str) -> str:
    """Build the Vedanta synthesis highlight box."""
    return f"""<h2><span class="tag" style="background: var(--accent2);">&#x2606;</span> VEDANTA &mdash; Synthesis</h2>
<div class="synthesis-box">
  {_format_content(synthesis)}
</div>"""


def _build_consensus_section(consensus: List[str]) -> str:
    """Build the consensus points section."""
    if not consensus:
        return ""
    items = "".join(f"<li>{_esc(c)}</li>" for c in consensus)
    return f"""<h2><span class="tag" style="background: var(--green);">&#x2713;</span> Consensus</h2>
<div class="card card-accent" style="border-left-color: var(--green);">
  <ul style="margin-left: 1.2rem; line-height: 2;">
    {items}
  </ul>
</div>"""


def _build_tensions_section(tensions: List[str]) -> str:
    """Build the tensions section."""
    if not tensions:
        return ""
    items = "".join(
        f'<li style="color: var(--text); margin-bottom: 0.6rem;">{_esc(t)}</li>'
        for t in tensions
    )
    return f"""<h2><span class="tag" style="background: var(--red);">&#x26A1;</span> Tensions</h2>
<div class="card card-accent" style="border-left-color: var(--red);">
  <p style="color: var(--muted); font-size: 0.85rem; margin-bottom: 0.8rem;">
    Where darshanas genuinely disagree &mdash; these are where the real complexity lives.
  </p>
  <ul style="margin-left: 1.2rem;">
    {items}
  </ul>
</div>"""


def _build_action_items(actions: List[str]) -> str:
    """Build the Mimamsa action items section."""
    if not actions:
        return ""
    rows = ""
    for action in actions:
        # Detect type from prefix patterns
        upper = action.upper()
        if upper.startswith("DO NOT") or upper.startswith("NISHIDDHA") or upper.startswith("AVOID"):
            cls = "action-nishiddha"
            label = "NISHIDDHA"
        elif upper.startswith("NOTE") or upper.startswith("ARTHAVADA") or upper.startswith("CONTEXT"):
            cls = "action-arthavada"
            label = "ARTHAVADA"
        else:
            cls = "action-vidhi"
            label = "VIDHI"
        rows += f'<tr><td class="{cls}">{label}</td><td>{_esc(action)}</td></tr>\n'

    return f"""<h2><span class="tag" style="background: var(--accent);">&#x25B6;</span> Action Items (Mimamsa)</h2>
<div class="card">
  <table>
    <tr><th>Type</th><th>Action</th></tr>
    {rows}
  </table>
</div>"""


def _build_maya_warnings(maya_gaps: List[Dict]) -> str:
    """Build the Maya layer warnings section."""
    if not maya_gaps:
        return ""
    items = ""
    for gap in maya_gaps:
        if isinstance(gap, dict):
            desc = gap.get("description", gap.get("gap", str(gap)))
            severity = gap.get("severity", "")
            sev_html = ""
            if severity:
                sev_color = COLORS["red"] if severity == "high" else COLORS["accent"] if severity == "medium" else COLORS["muted"]
                sev_html = f' <span style="color: {sev_color}; font-family: monospace; font-size: 0.8rem;">[{_esc(severity)}]</span>'
            items += f"<li>{_esc(desc)}{sev_html}</li>"
        else:
            items += f"<li>{_esc(str(gap))}</li>"

    return f"""<h2><span class="tag" style="background: var(--accent2);">&#x26A0;</span> MAYA LAYER &mdash; Representation Gaps</h2>
<div class="maya-box">
  <ul style="margin-left: 1.2rem; line-height: 2;">
    {items}
  </ul>
</div>"""


def _build_pipeline_trace(trace: Optional[Dict]) -> str:
    """Build the pipeline trace section."""
    if not trace:
        return ""

    steps = trace.get("steps", [])
    if not steps:
        return ""

    total_ms = trace.get("total_duration_ms", 0)
    rows = ""
    icons = {"completed": "&#x2713;", "skipped": "&#x2014;", "degraded": "~", "failed": "&#x2717;"}
    icon_colors = {"completed": COLORS["green"], "skipped": COLORS["muted"], "degraded": COLORS["accent"], "failed": COLORS["red"]}

    for i, step in enumerate(steps, 1):
        status = step.get("status", "unknown")
        icon = icons.get(status, "?")
        color = icon_colors.get(status, COLORS["muted"])
        detail = step.get("detail", "")
        detail_html = f' &mdash; <span style="color: var(--muted);">{_esc(detail)}</span>' if detail else ""
        rows += f"""<tr>
  <td style="color: {color}; text-align: center; font-family: monospace;">{icon}</td>
  <td>{i}. {_esc(step.get("name", ""))}</td>
  <td class="mono">{step.get("duration_ms", 0):.0f}ms</td>
  <td style="font-family: monospace; font-size: 0.8rem;">{_esc(status)}{detail_html}</td>
</tr>"""

    return f"""<h2><span class="tag">TRACE</span> Pipeline Trace</h2>
<div class="card">
  <p style="color: var(--muted); font-size: 0.85rem; margin-bottom: 0.8rem;">Total: {total_ms:.0f}ms</p>
  <table>
    <tr><th></th><th>Step</th><th>Time</th><th>Status</th></tr>
    {rows}
  </table>
</div>"""


def _build_cost_box(cost: float, model: str = "", tokens_in: int = 0, tokens_out: int = 0, latency_ms: float = 0) -> str:
    """Build the cost/performance info box."""
    parts = []
    if cost > 0:
        parts.append(f'<span class="routing-item">Cost: {_format_usd(cost)}</span>')
    if model:
        parts.append(f'<span class="routing-item">{_esc(model)}</span>')
    if tokens_in or tokens_out:
        parts.append(f'<span class="routing-item">{tokens_in:,} in / {tokens_out:,} out tokens</span>')
    if latency_ms > 0:
        parts.append(f'<span class="routing-item">{latency_ms:.0f}ms</span>')

    if not parts:
        return ""

    return f"""<div style="display: flex; gap: 0.6rem; flex-wrap: wrap; margin: 1rem 0;">
  {"".join(parts)}
</div>"""


def _build_guna_bars(guna_balance: Dict[str, float]) -> str:
    """Build CSS bar chart for guna balance."""
    if not guna_balance:
        return ""

    total = sum(guna_balance.values()) or 1
    bars = ""
    guna_order = ["sattva", "rajas", "tamas"]

    for g in guna_order:
        val = guna_balance.get(g, 0)
        pct = _pct(val, total)
        bars += f"""<div class="guna-bar-container">
  <span class="guna-label">{g.upper()}</span>
  <div class="guna-track">
    <div class="guna-fill guna-{g}" style="width: {pct:.1f}%;">{pct:.0f}%</div>
  </div>
</div>"""

    return f"""<div style="margin: 1rem 0;">
{bars}
</div>"""


def _build_pie_chart(data: Dict[str, float], colors: Optional[Dict[str, str]] = None) -> str:
    """Build a CSS conic-gradient pie chart."""
    if not data:
        return ""

    total = sum(data.values()) or 1
    default_colors = [
        COLORS["accent"], COLORS["accent2"], COLORS["blue"],
        COLORS["green"], COLORS["red"], COLORS["cyan"],
        COLORS["orange"], COLORS["muted"],
    ]

    # Build conic gradient stops
    stops = []
    legend_items = []
    angle = 0
    for i, (label, value) in enumerate(data.items()):
        color = (colors or {}).get(label, default_colors[i % len(default_colors)])
        pct = _pct(value, total)
        stops.append(f"{color} {angle:.1f}deg {angle + pct * 3.6:.1f}deg")
        angle += pct * 3.6
        legend_items.append(
            f'<span class="pie-legend-item">'
            f'<span class="pie-swatch" style="background: {color};"></span>'
            f'{_esc(label)}: {_format_usd(value)} ({pct:.0f}%)'
            f'</span>'
        )

    gradient = ", ".join(stops)

    return f"""<div style="text-align: center;">
  <div class="pie-chart" style="background: conic-gradient({gradient});"></div>
  <div class="pie-legend">
    {"".join(legend_items)}
  </div>
</div>"""


def _build_stat_box(value: str, label: str, color: str = "") -> str:
    """Build a single stat display box."""
    color_style = f' color: {color};' if color else ""
    return f"""<div class="stat-box">
  <div class="stat-value" style="{color_style}">{_esc(value)}</div>
  <div class="stat-label">{_esc(label)}</div>
</div>"""


def _build_stats_grid(stats: List[Dict[str, str]]) -> str:
    """Build a grid of stat boxes."""
    boxes = "".join(
        _build_stat_box(s.get("value", ""), s.get("label", ""), s.get("color", ""))
        for s in stats
    )
    return f'<div class="stats-grid">{boxes}</div>'


# ---------------------------------------------------------------------------
# DarshanaReport — single-engine response
# ---------------------------------------------------------------------------

class DarshanaReport:
    """
    Generate an HTML report from a single-engine Antahkarana response.

    Usage:
        html = DarshanaReport.generate(response)
        DarshanaReport.save(response, "output.html")
    """

    @staticmethod
    def generate(response: Any, title: Optional[str] = None) -> str:
        """
        Generate HTML from an AntahkaranaResponse or equivalent dict.

        Args:
            response: An AntahkaranaResponse object or dict with matching keys.
            title: Optional custom report title.

        Returns:
            Complete self-contained HTML string.
        """
        # Normalize to dict
        if hasattr(response, "to_dict"):
            data = response.to_dict()
        elif isinstance(response, dict):
            data = response
        else:
            data = {"text": str(response)}

        # Extract fields with safe defaults
        text = data.get("text", "")
        darshanas = data.get("darshana", [])
        if isinstance(darshanas, str):
            darshanas = [darshanas]
        vritti = data.get("vritti", "unknown")
        pramana_val = data.get("pramana", "unknown")
        guna = data.get("guna", "unknown")
        cost = data.get("cost", 0.0)
        depth = data.get("depth_score", 0)
        model = data.get("model", "")
        latency = data.get("latency_ms", 0.0)
        tokens_in = data.get("input_tokens", 0)
        tokens_out = data.get("output_tokens", 0)
        confidence = data.get("confidence", 0.0)
        self_check = data.get("self_check", {})
        maya_gaps = data.get("maya_gaps", [])
        pipeline_trace = None
        if "pipeline_trace" in data:
            pt = data["pipeline_trace"]
            if hasattr(pt, "to_dict"):
                pipeline_trace = pt.to_dict()
            elif isinstance(pt, dict):
                pipeline_trace = pt

        # Determine title
        query = ""
        if pipeline_trace and "query" in pipeline_trace:
            query = pipeline_trace["query"]
        report_title = title or f"Darshana Analysis"
        subtitle = f'Query: "{_esc(query)}"' if query else ""
        if darshanas:
            subtitle += f" &mdash; {', '.join(d.upper() for d in darshanas)} engine"

        # Build sections
        sections = []

        # Title
        sections.append(f'<h1><span class="om">&#x1F549;</span> {_esc(report_title)}</h1>')
        if subtitle:
            sections.append(f'<p class="subtitle">{subtitle}</p>')

        # Routing header
        sections.append(_build_routing_header(
            darshanas=darshanas,
            guna=guna,
            depth=depth,
            extra_items=[f"Confidence: {confidence:.0%}"] if confidence else None,
        ))

        # Main content
        if text:
            sections.append('<div class="card">')
            sections.append(_format_content(text))
            sections.append('</div>')

        # Vritti box
        sections.append(f'<h2><span class="tag">&#x2713;</span> VRITTI SELF-CHECK</h2>')
        sections.append(_build_vritti_box(vritti, pramana_val, self_check))

        # Maya warnings
        if maya_gaps:
            sections.append(_build_maya_warnings(maya_gaps))

        # Pipeline trace
        if pipeline_trace:
            sections.append(_build_pipeline_trace(pipeline_trace))

        # Cost/performance
        cost_html = _build_cost_box(cost, model, tokens_in, tokens_out, latency)
        if cost_html:
            sections.append(cost_html)

        body = "\n\n".join(sections)
        return _wrap_html(report_title, body)

    @staticmethod
    def save(response: Any, path: str, title: Optional[str] = None) -> Path:
        """Generate and save HTML report to file. Returns the Path."""
        html_str = DarshanaReport.generate(response, title)
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_str, encoding="utf-8")
        return out


# ---------------------------------------------------------------------------
# YakshaReport — multi-darshana parallel analysis
# ---------------------------------------------------------------------------

class YakshaReport:
    """
    Generate an HTML report from a YakshaResult (multi-darshana analysis).

    Usage:
        html = YakshaReport.generate(yaksha_result)
        YakshaReport.save(yaksha_result, "output.html")
    """

    @staticmethod
    def generate(result: Any, title: Optional[str] = None) -> str:
        """
        Generate HTML from a YakshaResult or equivalent dict.

        Args:
            result: A YakshaResult object or dict with matching keys.
            title: Optional custom report title.

        Returns:
            Complete self-contained HTML string.
        """
        # Normalize to dict
        if hasattr(result, "__dataclass_fields__"):
            # dataclass — manually extract
            data = {}
            data["query"] = getattr(result, "query", "")
            data["guna"] = getattr(result, "guna", "sattva")
            data["duration_ms"] = getattr(result, "duration_ms", 0)
            data["synthesis"] = getattr(result, "synthesis", "")
            data["consensus"] = getattr(result, "consensus", [])
            data["tensions"] = getattr(result, "tensions", [])
            data["action_items"] = getattr(result, "action_items", [])

            perspectives = getattr(result, "perspectives", {})
            data["perspectives"] = {}
            for name, analysis in perspectives.items():
                if hasattr(analysis, "__dataclass_fields__"):
                    data["perspectives"][name] = {
                        "darshana": getattr(analysis, "darshana", name),
                        "approach": getattr(analysis, "approach", ""),
                        "reasoning": getattr(analysis, "reasoning", ""),
                        "conclusion": getattr(analysis, "conclusion", ""),
                        "confidence": getattr(analysis, "confidence", 0.0),
                        "pramana": getattr(analysis, "pramana", "unknown"),
                        "metadata": getattr(analysis, "metadata", {}),
                    }
                elif isinstance(analysis, dict):
                    data["perspectives"][name] = analysis
                else:
                    data["perspectives"][name] = {"reasoning": str(analysis)}

            # Vritti self-check (may be added by the pipeline)
            data["vritti_check"] = getattr(result, "vritti_check", {})
            data["maya_gaps"] = getattr(result, "maya_gaps", [])
        elif isinstance(result, dict):
            data = result
        else:
            data = {"query": "", "perspectives": {}, "synthesis": str(result)}

        query = data.get("query", "")
        guna = data.get("guna", "sattva")
        duration = data.get("duration_ms", 0)
        perspectives = data.get("perspectives", {})
        synthesis = data.get("synthesis", "")
        consensus = data.get("consensus", [])
        tensions = data.get("tensions", [])
        action_items = data.get("action_items", [])
        vritti_check = data.get("vritti_check", {})
        maya_gaps = data.get("maya_gaps", [])

        darshana_names = list(perspectives.keys())
        report_title = title or "Yaksha Protocol — Multi-Darshana Analysis"

        # Build sections
        sections = []

        # Title
        sections.append(f'<h1><span class="om">&#x1F549;</span> {_esc(report_title)}</h1>')
        subtitle_parts = []
        if query:
            subtitle_parts.append(f'Query: &ldquo;{_esc(query)}&rdquo;')
        subtitle_parts.append(f"Full {len(perspectives)}-darshana analysis with Vedanta synthesis")
        sections.append(f'<p class="subtitle">{" &mdash; ".join(subtitle_parts)}</p>')

        # Routing header
        extra = []
        if duration > 0:
            extra.append(f"{duration:.0f}ms")
        sections.append(_build_routing_header(
            darshanas=darshana_names,
            guna=guna,
            extra_items=extra or None,
        ))

        # Individual darshana cards
        ordered_darshanas = [
            "vaisheshika", "samkhya", "nyaya", "yoga", "mimamsa", "vedanta"
        ]
        numbered = 1
        for d_name in ordered_darshanas:
            if d_name in perspectives:
                p = perspectives[d_name]
                sections.append(_build_darshana_card(
                    name=d_name,
                    approach=p.get("approach", ""),
                    reasoning=p.get("reasoning", ""),
                    conclusion=p.get("conclusion", ""),
                    confidence=p.get("confidence", 0.0),
                    pramana=p.get("pramana", "unknown"),
                    number=numbered,
                    metadata=p.get("metadata"),
                ))
                numbered += 1

        # Any darshanas not in the standard order
        for d_name, p in perspectives.items():
            if d_name not in ordered_darshanas:
                sections.append(_build_darshana_card(
                    name=d_name,
                    approach=p.get("approach", ""),
                    reasoning=p.get("reasoning", ""),
                    conclusion=p.get("conclusion", ""),
                    confidence=p.get("confidence", 0.0),
                    pramana=p.get("pramana", "unknown"),
                    number=numbered,
                    metadata=p.get("metadata"),
                ))
                numbered += 1

        # Vedanta synthesis
        if synthesis:
            sections.append(_build_synthesis_box(synthesis))

        # Consensus
        sections.append(_build_consensus_section(consensus))

        # Tensions
        sections.append(_build_tensions_section(tensions))

        # Action items
        sections.append(_build_action_items(action_items))

        # Vritti self-check table
        if vritti_check:
            sections.append(f'<h2><span class="tag">&#x2713;</span> VRITTI SELF-CHECK</h2>')
            sections.append(_build_vritti_box("pramana", "anumana", vritti_check))

        # Maya warnings
        if maya_gaps:
            sections.append(_build_maya_warnings(maya_gaps))

        body = "\n\n".join(s for s in sections if s)
        return _wrap_html(report_title, body)

    @staticmethod
    def save(result: Any, path: str, title: Optional[str] = None) -> Path:
        """Generate and save HTML report to file. Returns the Path."""
        html_str = YakshaReport.generate(result, title)
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_str, encoding="utf-8")
        return out


# ---------------------------------------------------------------------------
# IntrospectionReport — Ahamkara self-assessment
# ---------------------------------------------------------------------------

class IntrospectionReportGenerator:
    """
    Generate an HTML report from an Ahamkara introspection result.

    Usage:
        html = IntrospectionReportGenerator.generate(introspection)
        IntrospectionReportGenerator.save(introspection, "output.html")
    """

    @staticmethod
    def generate(report: Any, title: Optional[str] = None) -> str:
        """
        Generate HTML from an IntrospectionReport or equivalent dict.

        Args:
            report: An IntrospectionReport dataclass or dict.
            title: Optional custom report title.

        Returns:
            Complete self-contained HTML string.
        """
        # Normalize
        if hasattr(report, "to_dict"):
            data = report.to_dict()
        elif hasattr(report, "__dataclass_fields__"):
            from dataclasses import asdict
            data = asdict(report)
        elif isinstance(report, dict):
            data = report
        else:
            data = {}

        knowledge_count = data.get("knowledge_count", 0)
        knowledge_gaps = data.get("knowledge_gaps", [])
        failed = data.get("failed_approaches", [])
        successful = data.get("successful_approaches", [])
        vasanas = data.get("active_vasanas", [])
        guna_balance = data.get("guna_balance", {})
        recommendation = data.get("recommendation", "")
        total_attempts = data.get("total_attempts", 0)
        success_by_darshana = data.get("success_rate_by_darshana", {})

        # Additional memory stats if present
        memory_stats = data.get("memory_stats", {})

        report_title = title or "Ahamkara Introspection Report"

        sections = []

        # Title
        sections.append(f'<h1><span class="om">&#x1F549;</span> {_esc(report_title)}</h1>')
        sections.append(f'<p class="subtitle">Self-assessment of the Darshana Architecture\'s epistemic state</p>')

        # Summary stats
        success_total = len(successful)
        fail_total = len(failed)
        success_rate = _pct(success_total, total_attempts) if total_attempts else 0

        sections.append(_build_stats_grid([
            {"value": str(knowledge_count), "label": "Knowledge Claims", "color": COLORS["accent"]},
            {"value": str(total_attempts), "label": "Total Attempts", "color": COLORS["blue"]},
            {"value": f"{success_rate:.0f}%", "label": "Success Rate", "color": COLORS["green"] if success_rate >= 60 else COLORS["red"]},
            {"value": str(len(vasanas)), "label": "Active Vasanas", "color": COLORS["accent2"]},
        ]))

        # Guna state visualization
        if guna_balance:
            sections.append(f'<h2><span class="tag">&#x25CE;</span> Guna Balance</h2>')
            sections.append('<div class="card">')
            sections.append('<p style="color: var(--muted); font-size: 0.85rem; margin-bottom: 0.8rem;">'
                           'Current cognitive disposition: sattva (clarity), rajas (action), tamas (inertia)</p>')
            sections.append(_build_guna_bars(guna_balance))
            sections.append('</div>')

        # Knowledge map
        sections.append(f'<h2><span class="tag" style="background: var(--green);">&#x2726;</span> Knowledge Map</h2>')
        sections.append('<div class="card">')
        if knowledge_gaps:
            sections.append('<p style="margin-bottom: 0.8rem;"><strong>Knowledge Gaps:</strong></p>')
            gap_items = "".join(f'<li style="color: var(--muted);">{_esc(g)}</li>' for g in knowledge_gaps)
            sections.append(f'<ul style="margin-left: 1.2rem;">{gap_items}</ul>')
        else:
            sections.append('<p style="color: var(--muted);">No knowledge gaps currently tracked.</p>')
        sections.append('</div>')

        # Success rate by darshana
        if success_by_darshana:
            sections.append(f'<h2><span class="tag" style="background: var(--blue);">&#x2261;</span> Success Rate by Darshana</h2>')
            sections.append('<div class="card">')
            rows = ""
            for d_name, rate in success_by_darshana.items():
                color = DARSHANA_COLORS.get(d_name.lower(), COLORS["accent2"])
                rate_pct = rate * 100 if isinstance(rate, float) and rate <= 1.0 else rate
                bar_color = COLORS["green"] if rate_pct >= 60 else COLORS["accent"] if rate_pct >= 40 else COLORS["red"]
                rows += f"""<tr>
  <td style="font-family: monospace; color: {color}; text-transform: uppercase;">{_esc(d_name)}</td>
  <td style="width: 60%%;">
    <div class="progress-track">
      <div class="progress-fill" style="width: {rate_pct:.0f}%; background: {bar_color};"></div>
    </div>
  </td>
  <td class="mono" style="text-align: right;">{rate_pct:.0f}%</td>
</tr>"""
            sections.append(f'<table>{rows}</table>')
            sections.append('</div>')

        # Attempt history
        if successful or failed:
            sections.append(f'<h2><span class="tag" style="background: var(--accent);">&#x21BB;</span> Attempt History</h2>')

            if successful:
                sections.append('<div class="card card-accent" style="border-left-color: var(--green);">')
                sections.append(f'<strong style="color: var(--green);">Successful Approaches ({len(successful)})</strong>')
                for s in successful[:10]:  # Show top 10
                    darshana = s.get("darshana", "unknown") if isinstance(s, dict) else "unknown"
                    query_str = s.get("query", "") if isinstance(s, dict) else str(s)
                    sections.append(
                        f'<div style="margin-top: 0.6rem; padding: 0.4rem 0; border-bottom: 1px solid var(--border);">'
                        f'<span style="color: {DARSHANA_COLORS.get(darshana.lower(), COLORS["muted"])}; '
                        f'font-family: monospace; font-size: 0.8rem;">{_esc(darshana.upper())}</span> '
                        f'<span style="font-size: 0.9rem;">{_esc(query_str[:100])}</span></div>'
                    )
                sections.append('</div>')

            if failed:
                sections.append('<div class="card card-accent" style="border-left-color: var(--red);">')
                sections.append(f'<strong style="color: var(--red);">Failed Approaches ({len(failed)})</strong>')
                for f_item in failed[:10]:
                    darshana = f_item.get("darshana", "unknown") if isinstance(f_item, dict) else "unknown"
                    reason = f_item.get("reason", "") if isinstance(f_item, dict) else str(f_item)
                    sections.append(
                        f'<div style="margin-top: 0.6rem; padding: 0.4rem 0; border-bottom: 1px solid var(--border);">'
                        f'<span style="color: var(--red); font-family: monospace; font-size: 0.8rem;">'
                        f'{_esc(darshana.upper())}</span> '
                        f'<span style="font-size: 0.9rem; color: var(--muted);">{_esc(reason[:100])}</span></div>'
                    )
                sections.append('</div>')

        # Active vasanas (biases)
        if vasanas:
            sections.append(f'<h2><span class="tag" style="background: var(--accent2);">&#x26A0;</span> Active Vasanas (Biases)</h2>')
            sections.append('<div class="card">')
            sections.append('<p style="color: var(--muted); font-size: 0.85rem; margin-bottom: 1rem;">'
                           'Vasanas are cognitive tendencies — habitual patterns that may distort reasoning.</p>')
            for v in vasanas:
                if isinstance(v, dict):
                    name = v.get("name", v.get("vasana", ""))
                    strength = v.get("strength", 0)
                    desc = v.get("description", "")
                    strength_color = COLORS["red"] if strength > 0.7 else COLORS["accent"] if strength > 0.4 else COLORS["green"]
                    sections.append(
                        f'<div style="margin-bottom: 0.8rem; padding: 0.8rem; background: var(--border); border-radius: 6px;">'
                        f'<strong>{_esc(name)}</strong> '
                        f'<span style="color: {strength_color}; font-family: monospace; font-size: 0.8rem;">'
                        f'strength: {strength:.2f}</span>'
                        f'<p style="font-size: 0.9rem; color: var(--muted); margin-top: 0.3rem;">{_esc(desc)}</p>'
                        f'</div>'
                    )
                else:
                    sections.append(f'<div style="margin-bottom: 0.5rem;">{_esc(str(v))}</div>')
            sections.append('</div>')

        # Memory stats
        if memory_stats:
            sections.append(f'<h2><span class="tag" style="background: var(--blue);">&#x2756;</span> Memory Stats</h2>')
            stat_items = []
            for k, v in memory_stats.items():
                stat_items.append({"value": str(v), "label": k.replace("_", " ").title()})
            sections.append(_build_stats_grid(stat_items[:8]))

        # Recommendation
        if recommendation:
            sections.append(f'<h2><span class="tag" style="background: var(--green);">&#x279C;</span> Recommendation</h2>')
            sections.append(f'<div class="signal-box">{_esc(recommendation)}</div>')

        body = "\n\n".join(s for s in sections if s)
        return _wrap_html(report_title, body)

    @staticmethod
    def save(report: Any, path: str, title: Optional[str] = None) -> Path:
        """Generate and save HTML report to file. Returns the Path."""
        html_str = IntrospectionReportGenerator.generate(report, title)
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_str, encoding="utf-8")
        return out


# ---------------------------------------------------------------------------
# ShaktiReport — budget and compute usage
# ---------------------------------------------------------------------------

class ShaktiReport:
    """
    Generate an HTML report from a Shakti budget report.

    Usage:
        html = ShaktiReport.generate(shakti_manager.report())
        ShaktiReport.save(shakti_manager.report(), "output.html")
    """

    @staticmethod
    def generate(report: Any, title: Optional[str] = None) -> str:
        """
        Generate HTML from a Shakti report dict.

        Args:
            report: Dict from ShaktiManager.report() or equivalent.
            title: Optional custom report title.

        Returns:
            Complete self-contained HTML string.
        """
        if hasattr(report, "to_dict"):
            data = report.to_dict()
        elif isinstance(report, dict):
            data = report
        else:
            data = {}

        # Extract sections
        daily = data.get("daily", {})
        weekly = data.get("weekly", {})
        monthly = data.get("monthly", {})
        budget = data.get("budget", {})
        by_tier = data.get("by_tier", {})
        by_darshana = data.get("by_darshana", {})
        by_guna = data.get("by_guna", {})
        cache = data.get("cache", {})
        prana = data.get("prana", {})
        efficiency = data.get("efficiency_score", 0)
        suggestions = data.get("suggestions", [])

        report_title = title or "Shakti Energy Report"

        sections = []

        # Title
        sections.append(f'<h1><span class="om">&#x1F549;</span> {_esc(report_title)}</h1>')
        sections.append(f'<p class="subtitle">Compute budget and energy allocation report</p>')

        # Budget overview stats
        daily_spend = daily.get("total_cost", daily.get("cost", 0))
        weekly_spend = weekly.get("total_cost", weekly.get("cost", 0))
        monthly_spend = monthly.get("total_cost", monthly.get("cost", 0))
        daily_budget = budget.get("daily_budget_usd", 0)
        daily_remaining = budget.get("daily_remaining_usd", 0)
        monthly_budget = budget.get("monthly_budget_usd", 0)
        monthly_remaining = budget.get("monthly_remaining_usd", 0)

        sections.append(_build_stats_grid([
            {"value": _format_usd(daily_spend), "label": "Today", "color": COLORS["accent"]},
            {"value": _format_usd(weekly_spend), "label": "This Week", "color": COLORS["blue"]},
            {"value": _format_usd(monthly_spend), "label": "This Month", "color": COLORS["accent2"]},
            {"value": f"{efficiency}" if efficiency else "N/A", "label": "Efficiency", "color": COLORS["green"]},
        ]))

        # Budget bars
        if daily_budget > 0:
            daily_pct = min(_pct(daily_spend, daily_budget), 100)
            monthly_pct = min(_pct(monthly_spend, monthly_budget), 100) if monthly_budget else 0
            daily_bar_color = COLORS["green"] if daily_pct < 70 else COLORS["accent"] if daily_pct < 90 else COLORS["red"]
            monthly_bar_color = COLORS["green"] if monthly_pct < 70 else COLORS["accent"] if monthly_pct < 90 else COLORS["red"]

            sections.append(f'<h2><span class="tag" style="background: var(--accent);">$</span> Budget Status</h2>')
            sections.append('<div class="card">')
            sections.append(
                f'<div style="margin-bottom: 1rem;">'
                f'<div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 0.85rem;">'
                f'<span>Daily: {_format_usd(daily_spend)} / {_format_usd(daily_budget)}</span>'
                f'<span style="color: var(--muted);">{_format_usd(daily_remaining)} remaining</span></div>'
                f'<div class="progress-track"><div class="progress-fill" style="width: {daily_pct:.0f}%; background: {daily_bar_color};"></div></div>'
                f'</div>'
            )
            if monthly_budget > 0:
                sections.append(
                    f'<div>'
                    f'<div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 0.85rem;">'
                    f'<span>Monthly: {_format_usd(monthly_spend)} / {_format_usd(monthly_budget)}</span>'
                    f'<span style="color: var(--muted);">{_format_usd(monthly_remaining)} remaining</span></div>'
                    f'<div class="progress-track"><div class="progress-fill" style="width: {monthly_pct:.0f}%; background: {monthly_bar_color};"></div></div>'
                    f'</div>'
                )
            sections.append('</div>')

        # Spend by model tier — pie chart
        if by_tier:
            tier_colors = {
                "haiku": COLORS["green"],
                "sonnet": COLORS["blue"],
                "opus": COLORS["accent2"],
            }
            sections.append(f'<h2><span class="tag" style="background: var(--blue);">&#x25CE;</span> Spend by Model Tier</h2>')
            sections.append('<div class="card">')
            sections.append(_build_pie_chart(by_tier, tier_colors))

            # Also show as table
            rows = ""
            tier_total = sum(by_tier.values()) or 1
            for tier_name, tier_cost in sorted(by_tier.items(), key=lambda x: -x[1]):
                pct = _pct(tier_cost, tier_total)
                color = tier_colors.get(tier_name.lower(), COLORS["muted"])
                rows += f"""<tr>
  <td style="color: {color}; font-family: monospace; text-transform: uppercase;">{_esc(tier_name)}</td>
  <td class="mono">{_format_usd(tier_cost)}</td>
  <td class="mono">{pct:.1f}%</td>
</tr>"""
            sections.append(f'<table style="margin-top: 1.5rem;"><tr><th>Tier</th><th>Cost</th><th>Share</th></tr>{rows}</table>')
            sections.append('</div>')

        # Spend by darshana
        if by_darshana:
            sections.append(f'<h2><span class="tag" style="background: var(--accent2);">&#x2726;</span> Spend by Darshana</h2>')
            sections.append('<div class="card">')
            rows = ""
            d_total = sum(by_darshana.values()) or 1
            for d_name, d_cost in sorted(by_darshana.items(), key=lambda x: -x[1]):
                pct = _pct(d_cost, d_total)
                color = DARSHANA_COLORS.get(d_name.lower(), COLORS["muted"])
                rows += f"""<tr>
  <td style="color: {color}; font-family: monospace; text-transform: uppercase;">{_esc(d_name)}</td>
  <td class="mono">{_format_usd(d_cost)}</td>
  <td class="mono">{pct:.1f}%</td>
  <td style="width: 40%%;">
    <div class="progress-track">
      <div class="progress-fill" style="width: {pct:.0f}%; background: {color};"></div>
    </div>
  </td>
</tr>"""
            sections.append(f'<table><tr><th>Darshana</th><th>Cost</th><th>Share</th><th></th></tr>{rows}</table>')
            sections.append('</div>')

        # Cache efficiency
        if cache:
            hits = cache.get("hits", 0)
            misses = cache.get("misses", 0)
            total_lookups = hits + misses
            hit_rate = _pct(hits, total_lookups) if total_lookups else 0
            saved = cache.get("cost_saved", 0)

            sections.append(f'<h2><span class="tag" style="background: var(--green);">&#x21BB;</span> Cache Efficiency</h2>')
            sections.append('<div class="card">')
            sections.append(_build_stats_grid([
                {"value": f"{hit_rate:.0f}%", "label": "Hit Rate", "color": COLORS["green"] if hit_rate > 50 else COLORS["red"]},
                {"value": str(hits), "label": "Hits"},
                {"value": str(misses), "label": "Misses"},
                {"value": _format_usd(saved), "label": "Cost Saved", "color": COLORS["green"]},
            ]))
            sections.append('</div>')

        # Cost optimization suggestions
        if suggestions:
            sections.append(f'<h2><span class="tag" style="background: var(--accent);">&#x2605;</span> Optimization Suggestions</h2>')
            sections.append('<div class="card">')
            for s in suggestions:
                sections.append(
                    f'<div style="padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-size: 0.9rem;">'
                    f'<span style="color: var(--accent);">&#x279C;</span> {_esc(s)}</div>'
                )
            sections.append('</div>')

        body = "\n\n".join(s for s in sections if s)
        return _wrap_html(report_title, body)

    @staticmethod
    def save(report: Any, path: str, title: Optional[str] = None) -> Path:
        """Generate and save HTML report to file. Returns the Path."""
        html_str = ShaktiReport.generate(report, title)
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_str, encoding="utf-8")
        return out
