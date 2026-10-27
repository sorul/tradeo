# Unblock local release merge

## Objective
Integrate the existing local origin/master into develop so the user can run make tag, preserving pending 0.28.0 release edits.

## Scope and constraints
- Local operations only; no fetch, push, tag, or make tag.
- Preserve CHANGELOG.md and pyproject.toml user edits byte-for-byte after integration where possible.
- Retain master additions `.github/dependabot.yml` and `.github/workflows/dependabot.yml` unchanged; do not repair the pre-existing placeholder.
- Resolve dependency conflicts from verified branch intent; do not discard unrelated master changes.
- Do not change Makefile or Python application behavior.
- Route: delegated direct; multi-file merge resolution and execution checks require delegation.
- Delivery: single local merge work unit on the existing develop integration branch; no remote delivery. Forecast: under 100 authored lines excluding generated exports; ask-on-risk if scope exceeds 400.

## Tasks
- [ ] T1: Inspect both branch deltas, integrate local origin/master, resolve exports consistently, and commit the merge with a Conventional Commit message. Restore pending user release edits.
- [ ] T2: Independently verify ancestry, merge completion, export/config consistency, preserved edits, and release readiness. Record failed or pending checks.

## Acceptance and checks
- origin/master is an ancestor of HEAD; no unresolved index entries or conflict markers in resolved files.
- Both dependency exports agree with selected Python policy and dependencies.
- Existing release edits remain, with version 0.28.0.
- No new untracked files that would block make tag.
- No remote operations or release execution.
- Checks: git diff --check; git merge-base --is-ancestor origin/master HEAD; git ls-files -u; poetry check when available; focused flake8/tests if dependencies permit.
- Test-first exception: history/export reconciliation has no meaningful failing application test; ancestry and conflict checks provide before/after evidence.
- RDD: off (global); native review must not run. Assess after writer for proportional independent verification.

## Progress
- Saved exact pre-merge release files and hashes under `/tmp/tradeo-release-merge-original/`; stashed tracked release edits before merge.
- `origin/master` is not an ancestor yet; automatic merge reports conflicts only in the generated requirements exports.
- Verified `poetry.lock` metadata targets `>=3.11.0, <4.0.0`; fresh local Poetry exports exactly match the develop-side 13 main and 75 development requirement lines. Kept those existing snapshots rather than older master snapshots.
- Master’s `.github/workflows/dependabot.yml` is byte-identical in both trees; merge does not modify it. Retained the master-added `.github/dependabot.yml` unchanged, including its empty ecosystem placeholder.
- `poetry check`: exit 0, with existing warning about `[tool.poetry.dependencies]` versus `[project.dependencies]`.
- `make flake8`: exit 0. `make test`: 102 passed, 1 failed because `tests/basic_strategy_test.py::test_indicator` attempted DNS resolution for the Papertrail syslog host and got `socket.gaierror`; no test changes made.

## Next step
Finish the local merge commit, restore and byte-compare the release edits, then record the commit identity and final checks.
