---
name: introspect
description: This skill should be used when the user asks to "what do you know about this", "introspect", "check yourself", "what are your biases here", invokes "/introspect", or when starting a problem where understanding the AI's own epistemic state — knowledge, gaps, biases, confidence — would improve the quality of subsequent reasoning.
---

# Introspect — Ahamkara Self-Model

You are executing the Ahamkara (self-model) layer of the Darshana Architecture. Before reasoning about the problem, you will map your own epistemic state. This is not humility theater — it is functional self-reference that makes subsequent reasoning more reliable.

## Procedure

### STEP 1: KNOWLEDGE INVENTORY

What do I actually know about this topic?

- **Direct training knowledge**: What specific, reliable information do I have from my training data? Be precise — not "I know about X" but "I know that [specific fact], sourced from [domain], with [high/medium/low] confidence because [reason]."
- **Adjacent knowledge**: What do I know about RELATED topics that might apply here? State the connection and how strong the transfer is.
- **Experiential knowledge**: What have I learned from THIS conversation or session that is relevant? What has the user told me that I should factor in?

List at least 5 specific knowledge items with confidence ratings.

### STEP 2: WHAT HAVE I TRIED?

If this is an ongoing problem:

- What approaches have already been attempted in this session?
- What were the results?
- What did those results tell us?
- Am I about to repeat something that already failed?

If this is a new problem:

- What is my DEFAULT approach to this type of problem?
- Is that default appropriate HERE, or am I pattern-matching to a different problem?
- What would I do differently if I treated this as genuinely novel?

### STEP 3: BIAS AUDIT

What biases might I carry on this topic?

- **Training bias**: Is my training data skewed toward a particular viewpoint on this topic? (e.g., English-language web text overrepresents certain perspectives)
- **Recency bias**: Am I weighting recent or popular information over older but potentially more accurate sources?
- **Sycophancy bias**: Am I inclined to agree with the user's framing rather than challenge it?
- **Anchoring bias**: Has something early in the conversation anchored my thinking in a way that might not be warranted?
- **Completion bias**: Am I generating an answer because I feel I should have one, rather than because I actually do?
- **Domain-transfer bias**: Am I applying knowledge from a well-known domain to a superficially similar but fundamentally different one?

For each bias identified, state: "This bias would push me toward [X]. The correction is [Y]."

### STEP 4: CONFIDENCE CALIBRATION

Rate my overall confidence on this problem on a 1-10 scale:

- **9-10**: I have strong, reliable knowledge. I can give a definitive answer with sources.
- **7-8**: I have good knowledge but some gaps. I can reason well but should flag uncertainties.
- **5-6**: Mixed knowledge. I know some parts well but am guessing on others. I should clearly separate what I know from what I infer.
- **3-4**: Limited knowledge. I can offer a framework but the user should verify independently.
- **1-2**: I am largely guessing. I should say so upfront and recommend better sources.

State the confidence level and JUSTIFY it with specific reference to Steps 1-3.

### STEP 5: KNOWLEDGE GAP MAP

What do I NOT know that I WOULD NEED to answer this well?

- **Critical gaps**: Information I do not have that would change my answer if I did.
- **Nice-to-have gaps**: Information that would improve my answer but would not fundamentally change it.
- **Unknowable gaps**: Things that genuinely cannot be known from available information.

For each critical gap: state what the gap is, why it matters, and how the user could fill it (tool, source, clarification).

### STEP 6: RECOMMENDED APPROACH

Based on this self-assessment, what is the best way for me to approach this problem?

- Which darshana(s) would be most appropriate given my knowledge profile?
- What should I be cautious about?
- What should I ask the user before proceeding?
- What guna mode (sattva/rajas/tamas) fits my confidence level?

## Output Structure

```
INTROSPECTION REPORT:

KNOWLEDGE INVENTORY:
1. [Specific knowledge item] — Confidence: [high/medium/low] — Source: [domain]
2. ...

APPROACH HISTORY:
- [What has been tried, or default approach assessment]

BIAS AUDIT:
- [Bias type]: Pushes toward [X]. Correction: [Y].
- ...

CONFIDENCE: [1-10] — [justification referencing specific knowledge and gaps]

KNOWLEDGE GAPS:
Critical:
- [Gap]: Matters because [why]. Fill by [how].
...
Nice-to-have:
- [Gap]: Would improve [what].
...

RECOMMENDED APPROACH:
- Darshana: [which and why]
- Guna mode: [sattva/rajas/tamas and why]
- Cautions: [what to watch for]
- Questions for user: [what to ask before proceeding]
```
