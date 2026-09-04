---
title: Demo Checkpoints and Reset Workflow
description: Safe Git checkpoint and reset procedures for independent GH-300 demonstrations
ms.date: 2026-09-04
ms.topic: how-to
---

## Purpose

Copilot demonstrations modify source files and create tests or scripts. A
later lab must not inherit those changes. Each scenario therefore restores an
explicit set of tracked files from an immutable tag and removes only its
allowlisted generated output.

The checkpoint configuration is in `demo/checkpoints.json`. The initial
`demo/baseline-2026-08` tag points to the intentionally defective source used
for debugging, modernization, testing, security, and review exercises. The
manifest also pins the full commit ID, so moving the friendly tag causes the
reset to fail rather than silently changing the baseline.

## Available scenarios

| Scenario | Restored source | Removed generated output |
|---|---|---|
| `javascript` | `src/cart.js` | `tests/cart.test.js` |
| `python` | `src/inventory_legacy.py` | `tests/test_inventory_legacy.py` |
| `starter` | Both source modules | Both generated tests and `backups/` |

## Safe reset procedure

1. Save intentional work in a commit or stash.
2. Inspect the reset plan without changing files.

   ```bash
   scripts/demo-reset.sh --dry-run starter
   ```

3. Confirm that the displayed ref, restored paths, and removed paths match the
   intended scenario.
4. Run the reset interactively.

   ```bash
   scripts/demo-reset.sh starter
   ```

5. Confirm the resulting working tree with `git status --short`.

For trusted automation, `--yes` bypasses only the interactive confirmation. It
does not bypass allowlist validation or protection for unrelated changes.

## Safety behavior

The utility:

* Requires both Git and Python 3
* Requires execution inside a Git repository
* Validates the scenario and rejects absolute paths or parent traversal
* Rejects Git pathspec magic, control characters, duplicate paths, and
   overlapping restore and cleanup paths
* Verifies that the checkpoint tag resolves to the pinned full commit ID
* Verifies that every restored path exists in the pinned commit
* Rejects all tracked or untracked changes outside the selected allowlist
* Restores both index and worktree for configured tracked paths
* Refuses to clean a generated path if it has become tracked
* Uses path-scoped `git clean -x` only for configured generated paths, including
   ignored output such as `backups/`
* Requires confirmation before destructive work unless `--yes` is supplied

It does not run `git reset --hard`, clean the entire repository, switch
branches, modify commits, or push tags.

## Maintain checkpoints

Treat published checkpoint tags as immutable. To introduce a revised baseline:

1. Ensure the starter source contains only documented intentional defects.
2. Run all repository validation that is expected to pass at the starter
   checkpoint.
3. Commit the complete baseline.
4. Create a new annotated, versioned tag rather than moving an existing tag.
5. Update each affected `ref` in `demo/checkpoints.json`.
6. Run the reset tests and exercise every scenario from a dirty allowlisted
   state.
7. Push the commit and the new tag only after review.

The baseline tag name includes the study-guide version because product and exam
objectives change independently of source-code semantic versions.

## Validate the workflow

Run the automated reset and coverage tests:

```bash
uv run pytest tests/test_demo_reset.py tests/test_validate_coverage.py
```

Run static checks:

```bash
uv run ruff check scripts tests
bash -n scripts/demo-reset.sh
shellcheck scripts/demo-reset.sh
```

ShellCheck is required in CI even when it is not installed on a presenter's
workstation.