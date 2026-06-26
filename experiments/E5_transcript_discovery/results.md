# E5 — session-id → transcript discovery, and tail-N survival under compaction

Phase 0 spike S7 ([roadmap](../../docs/plans/roadmap.md)). Gates CAP's window
materialization ([cap](../../docs/research-loom/design/cap.md)). Host-observed.

## Question
CAP discovers a session's transcript from its session id and materializes a
tail-N window to feed REF. Two unknowns:
1. Is session-id → transcript path deterministic and sufficient to find it?
2. Under compaction, does the tail-N window still reach the **original** turns,
   or does compaction overwrite them with a summary?

## Method
Scan every transcript Claude Code (v2.1.193) wrote for this project under
`~/.claude/projects/<cwd-slug>/`. `probe.py`:
- asserts each file's stem equals the `sessionId` recorded inside it;
- finds transcripts carrying `isCompactSummary` records and counts raw
  `user`/`assistant` turns surviving **after** the last summary.

## Result
```
[discovery] 94 transcripts; filename stem == sessionId on 94
[compaction] 21387156-…: 1 summary record, 2452 total, 551 raw turns survive after the last summary
[compaction] b7b5d284-…: 2 summary records, 1877 total,  321 raw turns survive after the last summary
```
- Path is **`<sessionId>.jsonl`** under the project's slugified-cwd dir — exact,
  no scan/heuristic needed. Confirmed deterministic on all 94 files.
- A transcript is append-only JSONL; each record carries `sessionId`,
  `parentUuid`, `type`, `timestamp`, `isSidechain`, `cwd`, `gitBranch`.
- Compaction **appends** a record of type `user` with `isCompactSummary: true`
  (+ `isVisibleInTranscriptOnly`); it does **not** delete or rewrite the prior
  raw turns. Raw turns persist both before and after each summary point.

## Conclusion (S7 → yes)
- **Discovery: yes.** session-id → path is deterministic; CAP needs no index.
- **Compaction: yes.** The `.jsonl` retains original turns regardless of
  compaction, so a tail-N slice over the file always reaches raw turns. CAP
  reads the file, not the host's in-context (post-compaction) view — so the
  window is unaffected by compaction. The `isCompactSummary` record is
  identifiable and can be skipped when slicing raw turns.

Reproduce: `python3 probe.py [PROJECT_TRANSCRIPT_DIR]`.

evidence-for: docs/research-loom/design/cap.md (transcript 发现 + compaction 下 tail-N)
