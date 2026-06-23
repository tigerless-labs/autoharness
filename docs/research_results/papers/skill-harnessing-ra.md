# [论文] Harnessing Agent Skills: Architectural Patterns and a Reference Architecture for Skill-Mediated LLM Agents

**Boming Xia, Liming Zhu, Zhenchang Xing, Qinghua Lu, Dino Sejdinovic, Xiwei Xu** (RAIR Centre · Adelaide Univ · CSIRO · UNSW) — [arXiv:2606.20631](https://arxiv.org/abs/2606.20631) · 2026-05-29.

The framing/architecture companion (sequential arXiv id to [SkillHarness](skillharness.md)). Defines **agent skill harnessing**: the layer governing *static artefact → skill-in-use (run-scoped) → skill-mediated behaviour (observable output)*. Output: a 10-pattern catalogue + 4-layer reference architecture, evaluated over 8 systems.

**Five core patterns.** (1) **Progressive Skill Activation** — available→selectable→active; descriptor-first to cut "context tax." (2) **Skill–Execution Authority Separation** — a capability reference grants no execution authority; authority comes from a separate policy. (3) **Verifiable Skill Contract** — independently checkable criteria → passed/failed/inconclusive/verifier-error. (4) **Runtime Skill-BOM** — per-run, skill-centred provenance manifest (exposed/selected/activated/excluded/unavailable). (5) **Skill–Agent Co-Evolution Loop** — run evidence drives *validated candidate changes*, never direct mutation of shared artefacts.
**Five supporting patterns.** Skill Eligibility Gate · Skill Scope Cascade · Skill Resource Materialisation Boundary · Skill Extension Bundle · Runtime Skill Repair (bounded same-run, stored artefact unchanged).

**Reference architecture (4 layers):** Supply Chain (artefacts at rest + return path) · Mediation (resolution, admission, staged activation) · Execution Control (executable consequences; Runtime Action Control at the boundary) · Evidence & Feedback (records/verifications/repair → back to Mediation; accepted changes → back to Supply Chain). Cross-cutting: Policy/Config + Identifier.

**Taxonomy.** Skills are distinctive because **five dimensions take their skill-form simultaneously**: runtime participation, enactment, authority implication, evidence need, evolution path. Skills vs tools (interpreted-not-executed; reference-without-authority) vs memory (run-scoped skill-centred evidence + governed feedback to a versioned artefact) vs reusable prompts (boundary is **dimensional, not categorical**). Splits **skill harnessing** (run-scoped artefact→use) from **skill management** (lifecycle: authoring/distribution/storage/update).

**Referenced directions.** §9.1 Agent Harness & Harness Engineering; §9.2 Agent Skills & Skill Harnessing. Cited across intro/patterns: externalisation/harness (rajasekaran2026, lin2026, trivedy2026, lopopolo2026, zhou2026externalization); capability security (miller2003); software supply-chain (williams2025, xia2023empirical); skill systems — Claude Code, OpenAI Codex, OpenHands, Cline, Windsurf, OpenCode; research — [HASP](hasp.md) (liu2026harnessing), FlowEvo, [SkillOS](skillos.md) (ouyang2026), SkillWeaver, SkillClaw.

**Relevance to autoharness.** This is the **architecture vocabulary for exactly what we build** — most of our invariants map onto a named pattern, which is useful for [docs/design/](../../design/index.md):
- **Skill–Agent Co-Evolution Loop** (run evidence → validated candidate, not direct mutation) = our **never-auto-write + gate** (invariants 1, 7).
- **Verifiable Skill Contract** (passed/failed/inconclusive) = our **zero-oracle objective gate** (invariant 7).
- **Skill Eligibility Gate** (applicability/trust/provenance before selectability) = **applicability** (invariant 6).
- **Skill–Execution Authority Separation + Runtime Action Control** = our security chokepoints / least-privilege.
- **Runtime Skill-BOM** = the provenance/evidence trail behind our attribution→lever.
- The **harnessing vs management split** directly frames our new `docs/design/management.md` (lifecycle) vs the run-scoped maintenance loop, and **Runtime Skill Repair** (same-run, artefact unchanged) is *not* us — we persist maintenance, so it's a clean boundary to state.
