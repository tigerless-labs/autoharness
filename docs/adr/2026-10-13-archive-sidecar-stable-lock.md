# Keep counter updates and archival under one stable symbol lock

## Context
A sidecar counter locks a file inside the skill directory. Archival can move that directory while the counter write is held, carrying the old sidecar and lock into the archive. The pending write then recreates a live directory with only metadata and loses the increment from the archived sidecar. A later stale bump can also recreate absent live metadata.

## Decision
Put shared archive/bump locks in the layer's existing state area, outside movable skill directories. Hash case-folded validated names into bounded filenames so legacy long names work and case aliases serialize; distinct case-sensitive names may harmlessly share a lock. Archive holds the same lock as counter read-modify-write. Reject a bump with no initialized sidecar, and let observational hooks explicitly skip that missing metadata case.

## Alternatives
An in-directory lock moves with its subject and cannot remain a stable rendezvous. Checking existence alone races with archival after the check. Rebuilding metadata after movement invents a live symbol without its skill. A global layer lock serializes unrelated symbols unnecessarily.

## Consequences
An update already inside the lock finishes before archive moves the directory. A bump after archive is rejected rather than resurrecting metadata. Empty permanent lock files stay in owned state; old in-directory lock files require no data migration and are left intact. Older implementations using the old lock do not gain this coordination during mixed-version operation. This does not synchronize all CRUD operations, recalculate an archival decision after it was made, or prove Windows behavior.

## Validation
Same final assertions on frozen bd9baf120f6b19a4a3dcd806bf24efa406632bbe:3fail/1legacy-long-name control pass. Actual owned filesystem/thread race holds the counter write, attempts archival, then verifies one complete archived directory with increment retained and no live metadata orphan. A stale observational handle and post-archive direct bump also fail safely. Candidate37focused tests and552full non-live tests pass, with1explicit live deselection, on Python3.13/macOS. Changed-file Ruff and whitespace pass. Existing cross-process counter tests remain in the full suite; this controlled archive test uses threads and real advisory file locks, not a separate Windows/process deployment. Mock collision fixtures now supply owned lock paths; earlier empty MagicMock-generated lock artifacts were retained privately after fixing fixtures. No client/model/provider call, live user skills or production database touched.
