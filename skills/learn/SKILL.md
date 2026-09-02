---
name: learn
description: Distill a reusable skill from the current session on demand. Use when the user says "/learn", "learn this", "记住这个做法", or asks to save/capture the workflow or lesson just worked through.
category: general
---
# Learn: distill this session into the skill library

Review the conversation so far and distill what is worth keeping — through the
standard proposal chain, never by writing files.

1. Identify class-level, reusable lessons: corrected approaches, non-trivial
   techniques, durable user preferences. Skip one-off narratives and
   environment-specific failures.
2. Compare first: read the injected skill index; if an existing skill covers
   the topic, prefer a `patch`/`update` over creating a near-duplicate.
3. Reconcile old with new: when a lesson supersedes an earlier rule, search
   the managed skill trees for contradicting statements and stage updates so
   the new version wins everywhere.
4. Stage every change exclusively via the `stage_skill` tool, one intent per
   lesson, with `reason` and a verbatim `evidence` quote from this session.
   The deterministic promoter validates and lands; rejects are reported at
   the next session start.

If nothing meets the bar, say so and stage nothing.
