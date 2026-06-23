# management — the typed DAG

The heart of the system: organize skills as a typed relation graph and run the four operations that
keep it healthy — relate, detect conflict, dedup, and gate additions. Spine: [workflow.md](workflow.md).

## The graph

Nodes are skills; edges are typed relations between them: dependency, specialization, duplication,
and a flagged **conflict** relation. This graph is the single structure conflict, dedup, retrieval,
and the admission gate all read.

## Relate

Edges are induced from skill text, not declared by hand: a two-view representation — what a skill
does, and what it requires — seeds candidate pairs, which a classifier types. This is the cold-start
construction borrowed from SkillDAG, applied to prose skills rather than executable contracts.

## Conflict

The active path detects **contradiction** — two skills whose instructions logically oppose — from
text, with no execution. This is deliberately the static half of conflict. **Behavioural
interference** — two individually-sound skills that degrade outcomes when used together — cannot be
seen in text and is reserved to the eval layer ([eval.md](eval.md)), which carries the outcome signal
it needs.

## Dedup

Semantic clustering surfaces duplicate and near-duplicate skills as merge candidates (borrowed:
SkillReducer). A standing hazard governs the action: text similarity alone cannot separate a
**redundant clone** from a **legitimate parallel specialist** — skills that read alike but cover
distinct interfaces, or would grow unwieldy if merged. Merges are therefore proposals a human
confirms, never an automatic collapse (hypothesis 5).

## Gated admission — how a skill is added

Addition is the one operation that grows the layer, so every candidate from intake passes a gate
before entering the graph:

- **overlaps an existing skill** → merge or generalize into it, do not add a sibling;
- **contradicts an existing skill** → resolve the conflict first;
- **neither, and recurring** → admit as a new node;
- **neither, and one-off** → reject.

This gate is what separates the system from an accumulation engine that only grows.

## Output

A maintained DAG plus reviewable change proposals — merges, conflict resolutions, admissions. The
layer proposes structural change; a human adopts it.
