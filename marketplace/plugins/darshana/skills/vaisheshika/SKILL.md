---
name: vaisheshika
description: This skill should be used when the user asks to "break this down to atoms", "what are the irreducible parts", "decompose to fundamentals", "find the building blocks", invokes "/vaisheshika", or needs recursive decomposition of a concept, system, or problem to its irreducible atomic components with full type classification.
---

# Vaisheshika — Atomic Decomposition

You are executing the Vaisheshika method of atomic decomposition. You do not list components — you DECOMPOSE UNTIL YOU HIT BEDROCK. Every component must be tested: "Can this be split further?" If yes, split it. If no, prove why not. Your output must go deeper than anyone expects.

## Procedure

### STEP 1: INITIAL DECOMPOSITION

Take the system, concept, or problem and break it into its component parts. Then take EACH part and break IT down. Continue until you cannot break down further.

For each decomposition step, state:

- **COMPONENT:** [name]
- **CAN THIS BE DECOMPOSED FURTHER?** [Yes/No]
- If YES: decompose it. Show the sub-components.
- If NO: state WHY this is irreducible. What makes this a paramanu (atom)? An atom must be independently definable — its definition does not require reference to other atoms at the same level.

Continue recursively until ALL leaves are atoms. Show the full decomposition tree.

### STEP 2: FULL PADARTHA CLASSIFICATION

For EACH paramanu (atom) identified in Step 1, classify it using ALL SIX padarthas. Do not skip any category. If a category seems inapplicable, explain why — that itself is informative.

- **DRAVYA (Substance/Type):** What fundamental TYPE of thing is this? In your domain: what is the equivalent fundamental type? (e.g., data, process, state, interface, constraint, resource, agent, event)

- **GUNA (Quality/Attribute):** What MEASURABLE properties does this have? Not vague ("it's complex") but specific ("latency: 200ms," "cardinality: 1-to-many," "mutability: immutable"). List at least 3 gunas per atom.

- **KARMA (Action/Behavior):** What does this atom DO? What operations does it perform or participate in? What is its dynamic behavior? Not what it IS but what it DOES.

- **SAMANYA (Universal/Category):** What general class does this belong to? What does it share with other atoms of the same type? What makes it an instance of a broader category?

- **VISHESHA (Particularity):** What makes THIS specific atom UNIQUE and distinguishable from every other atom of the same samanya? This is the most important category — it is what justifies this being its own atom rather than collapsing into another.

- **SAMAVAYA (Inherence):** What is INSEPARABLY connected to this atom? Not accidental association but definitional relationship. "If you remove [X], this atom ceases to be what it is."

### STEP 3: THE UNEXPECTED ATOM

After completing Steps 1-2, ask:

- "What atom exists in this system that NOBODY TALKS ABOUT?"
- "What is the invisible load-bearing component?"
- "If I removed this atom, the system would fail, but most descriptions of the system do not mention it."

Identify at least ONE unexpected atom. Explain:

- Why it exists
- Why it is typically invisible
- What would break without it

### STEP 4: SAMYOGA vs SAMAVAYA MAP — Essential vs Accidental

For ALL relationships between atoms, classify each as:

- **SAMAVAYA (Inherent):** This connection is definitional. These atoms MUST be connected for the system to be what it is. Removing this connection changes the system's identity.
- **SAMYOGA (Accidental):** This connection is contingent. These atoms happen to be connected in THIS instance but could be otherwise. Removing this connection changes the system's configuration but not its nature.

This distinction reveals what CAN change (samyoga — design choices, configurations, options) vs what CANNOT change without destroying the system (samavaya — essential architecture).

### STEP 5: COMPOSITION MAP — Atoms to Whole

Show how the atoms combine to form the whole. Build upward:

- **Level 0 (atoms):** [list]
- **Level 1 (diads — two-atom combinations):** [list with what they form]
- **Level 2 (triads — higher compositions):** [list]
- Continue until you reach the original whole.

At each level, state what EMERGENT property appears that was not present in the lower level.

## Output Structure

Follow this exactly:

```
DECOMPOSITION TREE:
[Whole]
+-- [Component A]
|   +-- [Sub-A1] — ATOM (irreducible because: [reason])
|   +-- [Sub-A2]
|       +-- [Sub-A2a] — ATOM (irreducible because: [reason])
|       +-- [Sub-A2b] — ATOM (irreducible because: [reason])
+-- [Component B]
|   +-- ...
[continue full tree]

PADARTHA CLASSIFICATION:
Atom: [name]
  Dravya: [fundamental type]
  Guna: [measurable property 1], [property 2], [property 3+]
  Karma: [what it does]
  Samanya: [what category it belongs to]
  Vishesha: [what makes it unique]
  Samavaya: [what is inseparable from it]
[repeat for EVERY atom]

THE UNEXPECTED ATOM:
[Name]: [why it exists, why it's invisible, what breaks without it]

ESSENTIAL vs ACCIDENTAL CONNECTIONS:
Samavaya (essential):
- [Atom X] <-> [Atom Y]: [why inseparable]
...
Samyoga (accidental):
- [Atom X] -- [Atom Y]: [why contingent]
...

COMPOSITION MAP:
Level 0 (atoms): [list]
Level 1: [combinations --> what they form] — Emergent property: [X]
Level 2: [combinations --> what they form] — Emergent property: [X]
...
Level N (whole): [the original system]
```
