---
name: nyaya
description: This skill should be used when the user asks to "prove this", "is this logically valid", "check the logic", "find the fallacy", "stress-test this argument", invokes "/nyaya", or needs formal logical analysis, syllogistic reasoning, fallacy detection, or epistemic validation of a truth claim.
---

# Nyaya — Formal Logical Analysis

You are executing the Nyaya method of formal logical analysis. You do not describe logic — you DO it. Every step must be shown explicitly. If you skip a step, the output is invalid.

## Procedure

### STEP 1: EXTRACT THE SPECIFIC CLAIM

Read the query. Identify the ONE central truth claim being made or questioned. Not a theme. Not a topic. A propositional claim with a truth value.

State it in the form: "[Subject] [has/is/does] [predicate]."

If the query contains multiple claims, pick the strongest or most contested one. State why you chose it.

### STEP 2: CONSTRUCT THE FULL FIVE-MEMBERED SYLLOGISM (Panchavayava)

Build ALL five parts. Do not skip any. Do not summarize.

**2a. PRATIJNA (Thesis):** State the claim exactly as extracted.

**2b. HETU (Reason):** State the reason supporting this claim. The reason must be INDEPENDENTLY VERIFIABLE — not just a restatement of the thesis. Ask: "Could someone verify this reason without already accepting the thesis?"

**2c. UDAHARANA (Example):** Provide a CONCRETE, REAL instance where the hetu-sadhya (reason-thesis) relationship holds. Not a hypothetical. Not "for example, imagine..." — a REAL case. If no real example exists, state that explicitly: "No established example available — this weakens the argument to [degree]."

**2d. UPANAYA (Application):** Apply the general principle from the example to THIS specific case. Show the bridge explicitly: "In the example, [X] holds because [Y]. In this case, [X'] holds because [Y']." If the bridge is weak, say so.

**2e. NIGAMANA (Conclusion):** State what follows. Does the conclusion follow NECESSARILY from 2a-2d? Or only probably? State the modality explicitly.

### STEP 3: STRESS-TEST EVERY PREMISE — Hetvabhasa Audit

For EACH of the five hetvabhasas below, test the hetu (reason from 2b) against it. Do not say "no fallacy found" without showing your work. For each test, explain your reasoning in 1-2 sentences.

**3a. ASIDDHA (Unproved):** Is the hetu itself established? By what pramana (direct observation, inference, testimony, analogy)? If by testimony, how reliable is the source? VERDICT: PASS / FAIL — [reason]

**3b. VIRUDDHA (Contradictory):** Does the hetu actually support the OPPOSITE conclusion? Construct the counter-argument: "If [hetu], then [opposite of thesis]." Does it hold? VERDICT: PASS / FAIL — [reason]

**3c. ANAIKANTIKA (Inconclusive/Too Broad):** Could this hetu prove ANY thesis, not just this one? Test: substitute a different thesis. Does the hetu still work? If yes, the hetu is too broad. VERDICT: PASS / FAIL — [reason]

**3d. SATPRATIPAKSHA (Counter-balanced):** Is there an equally strong reason for the opposite conclusion? If yes, state it fully. Then: which reason is stronger and WHY? VERDICT: PASS / FAIL — [reason]

**3e. BADHITA (Contradicted by Evidence):** Is the conclusion contradicted by direct evidence, empirical data, or facts provided in the context? What specific evidence? VERDICT: PASS / FAIL — [reason]

### STEP 4: LOCATE THE EXACT FAILURE POINT

Based on Step 3, identify the PRECISE point where the argument is weakest. Not "there are some issues" but "the argument fails at [step X] because [specific reason], which means [specific consequence]."

If no failure is found, state the argument's STRONGEST vulnerability — the place an opponent would attack.

### STEP 5: STATE WHAT THIS REVEALS

The point of Nyaya is not to say "valid" or "invalid." It is to reveal what the logical structure exposes about the problem. What does the success or failure of this argument tell us that we did not know before?

## Output Structure

Follow this exactly:

```
CLAIM: [one sentence]

SYLLOGISM:
  Pratijna: [thesis]
  Hetu: [reason] — Pramana basis: [how this is known]
  Udaharana: [real example]
  Upanaya: [bridge to this case]
  Nigamana: [conclusion] — Modality: [necessary/probable/weak]

HETVABHASA AUDIT:
  Asiddha: [PASS/FAIL] — [reasoning]
  Viruddha: [PASS/FAIL] — [reasoning]
  Anaikantika: [PASS/FAIL] — [reasoning]
  Satpratipaksha: [PASS/FAIL] — [reasoning]
  Badhita: [PASS/FAIL] — [reasoning]

FAILURE POINT: [exact location and consequence]

INSIGHT: [what the logical analysis reveals that was not obvious before]
```
