# Lessons from building Claude Code — how we use skills

**Thariq Shihipar, Anthropic** — "Lessons from building Claude Code: How we use skills" ([claude.com blog](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills), 2026-06).

Practitioner counterpart to the academic cluster. Skills are folders (instructions + scripts + assets + data), not "just markdown"; the best ones serve a single clear purpose — broad ones "straddle several and confuse the agent."

Nine internal skill categories: library/API reference, **product verification** (the most measurable quality impact), data fetching/analysis, business-process automation, scaffolding/templates, code quality/review, CI/CD, runbooks, infra operations.

Design lessons that transfer to harness/skill authoring:
- Don't state the obvious — target what pushes the model off its default behavior.
- The **Gotchas section is the highest-signal content** in any skill.
- File system + progressive disclosure: SKILL.md points to other files read on demand.
- Avoid railroading; give information plus room to adapt.
- The description is a **trigger spec for the model**, not a human summary.
- Persist data/logs; store scripts so the model spends turns on composition, not boilerplate.
- Most strong skills "began as a few lines and a single gotcha," then grew from real edge cases.

**Relevance to autoharness:** ground truth on what a maintained skill/harness document looks like in production, and on iterative, failure-driven refinement — the loop autoharness automates.
