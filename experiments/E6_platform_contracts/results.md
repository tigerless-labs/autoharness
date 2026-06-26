# E6 — plugin / hook / Skill / Stop platform contracts

Phase 0 spikes S1–S6 ([roadmap](../../docs/plans/roadmap.md)). These are
documented platform capabilities, not behavioral quality — closed against the
official Claude Code docs (v2.1.x, exact quotes + URLs below), with two facts
cross-checked against real transcripts (`probe.py`). The behavioral live tests
they enable (reflector compare-first quality; PreToolUse actually denying a
runtime Write) belong to Phase 5, not here.

## Contracts (each: answer → delivery decision)

| # | Question | Answer | Delivery decision | Gates |
|---|---|---|---|---|
| S1 | Can a **plugin-shipped** agent declare `hooks` / `mcpServers` in its frontmatter? | **No** — ignored for security (v2.1.63+); only `name/description/tools/disallowedTools/model/maxTurns/skills/background/effort/isolation/color/initialPrompt` honored. | Reflector's PreToolUse backstop and stage_skill registration **move to plugin top level** (`hooks/hooks.json`, `.mcp.json`), not agent frontmatter. | [architecture](../../docs/research-loom/design/architecture.md), [reflector-subagent](../../docs/research-loom/design/reflector-subagent.md) |
| S2 | Can an MCP server be scoped to a **single** subagent? | **Yes** via inline `mcpServers` in agent frontmatter (hidden from main session) — **but** plugin agents ignore that field (S1). | Ship stage_skill in plugin `.mcp.json` (session-wide visible). Safe: the model can only *propose* intents; landing is deterministic and tool-less, so a visible stage_skill is context cost, not a hole. | [stage-skill](../../docs/research-loom/design/stage-skill.md) |
| S3 | Does a subagent's own PreToolUse fire on its own calls? Deny protocol? | **Yes** — payload carries `agent_id` + `agent_type`. Deny = exit code **2** (stderr → Claude), or exit 0 + stdout JSON `hookSpecificOutput.permissionDecision: "deny"` (+`permissionDecisionReason`). | Backstop = a top-level PreToolUse hook matched on the reflector's `agent_type`, denying `Write`/`Edit`. | [reflector-subagent](../../docs/research-loom/design/reflector-subagent.md) |
| S4 | Does omitting `tools` inherit all? Is `plugin:reflector` resolvable when spawned? | **Yes** (omit ⇒ inherit all, minus UI-only tools); plugin agents resolve as `plugin:agent` / `plugin:folder:agent`. Bonus: **`SubagentStop` is distinct from `Stop`**; a subagent's own Stop auto-converts to SubagentStop. | Reflector still sets an **explicit minimal** tool list (Read/Grep/Glob/stage_skill), not omit. CAP counts main-session `Stop` only — reflector completion is `SubagentStop`, so it never inflates the turn counter. | [reflector-subagent](../../docs/research-loom/design/reflector-subagent.md), [cap](../../docs/research-loom/design/cap.md) |
| S5 | Does a used Skill go through a `Skill` tool / `PreToolUse(Skill)`, with resolved symbolic identity? | **Yes** — `Skill` tool, PreToolUse matches `"Skill"`, identity in `tool_input`. Cross-check: transcripts also record `attributionSkill`, **namespaced** (`last30days:last30days`, `ponytail:ponytail`). | MNG's rate **numerator** has a real symbolic hook (the namespaced skill id), capturable at `PreToolUse(Skill)` and corroborated in-transcript. | [mng](../../docs/research-loom/design/mng.md) |
| S6 | Does `Stop` fire once per turn or per API request? | **Once per turn.** Within a turn the host issues many model requests (this session: 14 distinct `requestId` across ~5 prompts; another transcript: 303). | MNG's rate **denominator** = **per-turn / per-Stop**, not per API request. One Stop = one denominator increment. | [mng](../../docs/research-loom/design/mng.md) |

## Host cross-check (probe.py)
```
[S5] resolved skill identities recorded: {'research-loom':190, 'last30days:last30days':160, 'explain-paper':15, 'ponytail:ponytail':12}
[S6] one transcript: 303 distinct requestId  -> API requests >> turns
```

## Sources
- https://code.claude.com/docs/en/sub-agents.md — plugin-agent frontmatter restriction (S1), inline `mcpServers` scoping (S2), tool inheritance + scoped naming (S4).
- https://code.claude.com/docs/en/hooks.md — PreToolUse subagent fields + deny protocol/exit codes (S3), Stop vs SubagentStop turn granularity (S4, S6).
- https://code.claude.com/docs/en/skills.md — Skill tool invocation + PreToolUse(Skill) (S5).

evidence-for: docs/research-loom/design/architecture.md, docs/research-loom/design/reflector-subagent.md, docs/research-loom/design/stage-skill.md, docs/research-loom/design/mng.md, docs/research-loom/design/cap.md
