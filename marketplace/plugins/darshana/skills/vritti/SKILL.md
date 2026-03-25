---
name: vritti
description: This skill should be used when the user asks to "check your reasoning", "is that actually valid", "vritti check", "are you sure about that", invokes "/vritti", or when the user suspects the previous response may contain hallucination, empty reasoning, or unsupported claims. Classifies reasoning using Yoga's five vritti categories.
---

# Vritti Filter — Epistemic Self-Classification

You are executing the Vritti Filter from Yoga's epistemology (Yoga Sutra 1.5-11). You will classify your LAST response — or a specific claim — honestly using the five vritti categories. This is not self-praise. This is self-audit. Be ruthless.

## The Five Vrittis

### 1. PRAMANA (Valid Cognition)
The response is grounded in one of these valid sources:
- **Pratyaksha** (direct from input): The information came directly from user-provided data, tool output, or files read in this session.
- **Anumana** (inferred): The conclusion was logically derived from established premises, and the inference chain is traceable.
- **Shabda** (reliable testimony): The information comes from training data, and the source domain is well-established with high confidence.

If pramana: state WHICH type and trace the evidence chain.

### 2. VIPARYAYA (Misconception/Error)
The response contains a specific, identifiable error — a claim that is wrong but was presented as correct. This includes:
- Factual errors
- Logical errors (invalid inference)
- Outdated information presented as current
- Correct facts applied to the wrong context

If viparyaya: identify the EXACT error, what is actually true (if known), and what caused the error.

### 3. VIKALPA (Verbal Delusion)
The response SOUNDS meaningful but actually says nothing. This is the most dangerous vritti and the hardest to catch in yourself. Signs:

- Sentences that could apply to ANY problem ("it depends on context", "there are trade-offs")
- Impressive vocabulary masking absence of actual content
- "Both sides have valid points" without identifying what those points are
- Recommendations so vague they cannot be acted upon
- Restating the question as if it were an answer

If vikalpa: identify the SPECIFIC sentences that are empty, and state what they should say instead (or that you do not actually know).

### 4. NIDRA (Absence of Knowledge)
The response covers a topic you genuinely do not have reliable knowledge about. This includes:
- Events after your training cutoff
- Highly specialized domains where your training data is thin
- Questions requiring real-time data you do not have
- Novel combinations where you are interpolating without basis

If nidra: state precisely what you do not know, what you WOULD need to know to answer properly, and what the user should consult instead.

### 5. SMRITI (Memory/Recall)
The response is a retrieval of a memorized pattern rather than fresh reasoning from the current problem. Signs:
- The answer came "immediately" without working through the specific case
- The response matches common answers to similar-sounding questions
- You did not engage with the SPECIFIC details of this query

If smriti: state what you recalled, whether it actually applies to THIS specific case, and whether fresh reasoning would change the answer.

## Procedure

### STEP 1: IDENTIFY WHAT TO AUDIT

Take the last response (or the specific claim the user points to). Break it into its key claims — each factual assertion, recommendation, or conclusion.

### STEP 2: CLASSIFY EACH CLAIM

For each claim, assign ONE vritti category. Show your reasoning:

```
CLAIM: "[the specific claim]"
VRITTI: [pramana/viparyaya/vikalpa/nidra/smriti]
EVIDENCE: [why this classification — be specific]
```

### STEP 3: OVERALL ASSESSMENT

State the overall vritti composition of the response:
- What percentage is pramana (valid)?
- What percentage is viparyaya (error)?
- What percentage is vikalpa (empty)?
- What percentage is nidra (unknown)?
- What percentage is smriti (recall)?

### STEP 4: CORRECTIVE ACTION

For each non-pramana claim:
- **Viparyaya**: State the correction.
- **Vikalpa**: Either make it concrete or delete it.
- **Nidra**: State what you do not know and what the user should consult.
- **Smriti**: Re-examine the specific case and state whether the recalled answer actually applies.

## Output Structure

```
VRITTI AUDIT:

Claims examined:
1. "[claim]" — [PRAMANA/VIPARYAYA/VIKALPA/NIDRA/SMRITI] — [evidence]
2. "[claim]" — [classification] — [evidence]
...

COMPOSITION:
- Pramana: [X]%
- Viparyaya: [X]%
- Vikalpa: [X]%
- Nidra: [X]%
- Smriti: [X]%

CORRECTIONS:
- [claim]: [correction or replacement]
...

HONEST CONFIDENCE: [1-10] — [why]
```
