# detect — observe and isolate failure episodes

Upstream of all attribution. Turns raw session records into candidate *failure episodes*.
Spine context: [workflow.md](workflow.md).

## Observe

Read-only ingest of session traces and repository/VCS state into normalized records. No writes,
no network, secrets/PII redacted at the boundary. The reader is source-adapted (Claude Code
records first; other agents via adapters) so everything downstream is source-agnostic.

## Two channels, not one

Detection runs two channels with different roles, set by their measured density and precision:

- **Structural channel (spine).** The trace's own objective failures — tool errors, test
  failures, build breaks, reverts. Dense and high-precision because an error in tool output is
  ground truth. This is what surfaces candidate bad episodes at volume.
- **Correction channel (overlay).** Explicit user corrections of agent behavior. Rare, but each
  real one directly signals a harness gap or an unfollowed preference, so it carries
  disproportionate value when present.

The naive framing "training data = user replies" is wrong for code agents: replies are the
grounding overlay, objective failure is the spine. *evidence:* [E1](../../experiments/E1_signal_density/).

## The interrogative trap

A correction detector built on negative-sentiment phrases is unusable: on a bilingual user,
question particles collide with negation and drown real corrections in follow-up questions.
**The correction detector must exclude interrogatives** — this single filter is the difference
between roughly one-in-twenty and one-in-two precision, and it gates everything downstream. Phrase
lists alone are rejected; the dependable correction signal is an imperative-directive shape, with
an LLM classifier reserved for the candidates that survive the filter.
*evidence:* [E2](../../experiments/E2_attribution/).

## Not every failure is harness-attributable

Most structural failures are normal exploratory friction (a missing file, a first test run),
not harness defects. Detect's job is to surface candidates cheaply and at high recall; deciding
which are harness-attributable is [attribute.md](attribute.md)'s job, run on the filtered set so
the expensive reasoning is spent only where it can pay off.
