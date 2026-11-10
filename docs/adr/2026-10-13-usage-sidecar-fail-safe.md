# Preserve unavailable skill sidecars during usage observation

## Context
Skill and Read hooks promise observational, fail-safe counting without interfering with host skills. A corrupt JSON sidecar, non-object JSON or malformed counter currently escapes the hook as an exception. These are owned metadata failures, not evidence the host tool itself failed.

## Decision
Return counted:false with sidecar_unavailable when sidecar ownership lookup or increment encounters filesystem, decoding or shape/conversion errors. Keep strict sidecar readers and atomic writes; never repair/reset metadata merely to count a usage event. Preserve existing unknown/non-agent and healthy-count results.

## Alternatives
Replacing malformed metadata with an empty object can destroy ownership and counters. Swallowing every exception would conceal programming failures beyond the known metadata boundary. Changing sidecar.read globally would alter lifecycle and promoter decisions outside this observational scope.

## Consequences
Unavailable metadata skips one count and remains intact for diagnosis. This is explicitly undercounting rather than claiming success; healthy symbols and later events remain countable. No sidecar or skill is created for an unowned symbol. Other metadata consumers retain their existing error behavior.

## Validation
Same six new cases against frozen bd9baf120f6b19a4a3dcd806bf24efa406632bbe all fail: both Skill and Read routes, malformed JSON, array JSON and string counters. Corrected cases assert exact preserved bytes and explicit skip result. Candidate focused/full non-live suite and changed-file Ruff results recorded in local campaign evidence. Live Claude sessions, provider calls and original user skill trees are excluded; fixtures use owned temporary roots.

Python3.13 isolated environment: focused usage/sidecar suites32passed; full non-live suite554passed/1explicitlive deselection; changed-file Ruff and diff whitespace pass. No full hosted Python3.11/3.12 or actual client validation claimed.
