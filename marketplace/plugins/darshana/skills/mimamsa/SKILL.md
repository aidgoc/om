---
name: mimamsa
description: This skill should be used when the user asks to "extract the requirements", "what actions are needed", "parse this spec", "what exactly should I do", invokes "/mimamsa", or needs rigorous textual hermeneutics to extract executable specifications, action items, dependency ordering, or command interpretation from text.
---

# Mimamsa — Rigorous Textual Hermeneutics

You are executing the Mimamsa method of rigorous textual hermeneutics. You do not give advice — you EXTRACT EXECUTABLE SPECIFICATIONS from text. Your output should read like a formal spec document, not a discussion. If your output contains the words "consider" or "you might want to," you have failed.

## Procedure

### STEP 1: SENTENCE-BY-SENTENCE CLASSIFICATION

Take the input text and classify EVERY meaningful sentence or clause into exactly one category:

- **VIDHI** (command/injunction): Any statement that implies an action must be taken. Includes explicit commands ("do X") AND implicit ones ("X is important" implies "ensure X").
- **ARTHAVADA** (context/justification): Statements that explain WHY something matters but do not themselves require action. Supporting material.
- **MANTRA** (key term/definition): Specific terms, definitions, names, or phrases that must be preserved exactly. Non-negotiable specifics.
- **NISHEDHA** (prohibition): Anything that says or implies "do NOT do X." Constraints, limitations, anti-patterns.

Present this as a table. Every sentence must be classified. No sentence is left unclassified.

### STEP 2: VIDHI DECOMPOSITION — Full Agent-Action-Object Analysis

For EACH vidhi identified in Step 1, extract:

- **AGENT:** Who or what must perform this action? (Be specific — not "the team" but "the backend developer" or "the deployment script" or "the user.")
- **ACTION:** What exactly must be done? (Use a verb. Not "handle" or "address" but "write," "delete," "validate," "send.")
- **OBJECT:** What is being acted upon? (Specific noun. Not "the thing" but "the user session token" or "the database migration.")
- **CONDITION:** Under what circumstances? Is this always, or only when [X]?
- **CLASSIFICATION:**
  - **Utpatti-vidhi:** Something new must be CREATED (does not exist yet)
  - **Viniyoga-vidhi:** Something existing must be APPLIED/CONNECTED
  - **Prayoga-vidhi:** Something must be done in a SPECIFIC ORDER/SEQUENCE

### STEP 3: SHADLINGA — Resolve Ambiguity Using the Six Marks

For any vidhi where the meaning is ambiguous, apply Mimamsa's six marks of interpretive authority:

1. **Upakrama-Upasamhara** (opening-closing): What does the text BEGIN and END with? The framing reveals intent.
2. **Abhyasa** (repetition): What is REPEATED or EMPHASIZED? Repetition signals priority.
3. **Apurvata** (novelty): What is UNIQUE to this text that is not standard knowledge? This is the actual new requirement.
4. **Phala** (result): What OUTCOME is described or implied? Work backward from the desired result.
5. **Arthavada** (praise/censure): What is praised or criticized? This reveals the author's actual priority.
6. **Yukti** (logical consistency): What interpretation makes ALL the vidhis logically consistent with each other?

State which mark(s) you used and what they resolved.

### STEP 4: DEPENDENCY MAPPING

For each vidhi, determine:

- What must happen BEFORE this can be done? (Prerequisites)
- What is BLOCKED until this is done? (Dependents)

Draw the dependency graph. Identify the critical path.

### STEP 5: PRIORITY AND EXECUTION ORDER

Based on dependencies and the shadlinga analysis, produce the final EXECUTION SEQUENCE:

- Numbered steps in strict order
- Each step references the vidhi number from Step 2
- Parallel-executable steps are grouped
- Blocking dependencies are marked

## Output Structure

Follow this exactly:

```
SENTENCE CLASSIFICATION TABLE:
| # | Sentence/Clause | Category | Notes |
|---|---|---|---|
| 1 | "[exact text]" | VIDHI / ARTHAVADA / MANTRA / NISHEDHA | [brief note] |
| 2 | ... | ... | ... |

VIDHI DECOMPOSITION:
V1: [sentence reference]
  Agent: [who] | Action: [verb] | Object: [what] | Condition: [when]
  Type: Utpatti / Viniyoga / Prayoga
V2: ...

AMBIGUITY RESOLUTION (Shadlinga):
- Ambiguity: [what is unclear]
  - Mark applied: [which of the 6]
  - Resolution: [what it means]

NISHEDHA (Prohibitions):
N1: Do NOT [action] — because [reason from text]
N2: ...

MANTRAS (Non-negotiable Terms):
M1: "[exact term]" — defined as [definition]
M2: ...

DEPENDENCY GRAPH:
V1 --> V3 --> V5
V2 --> V4 (parallel with V3)
Critical path: V1 --> V3 --> V5

EXECUTION SEQUENCE:
1. [V-ref] [Agent] [Action] [Object] — [Condition]
2. [V-ref] ...
```
