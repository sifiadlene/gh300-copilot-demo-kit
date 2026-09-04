# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
"""Tests for the guarded demo reset utility."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.reset_guard import load_scenario

PROJECT_ROOT = Path(__file__).parents[1]
RESET_SCRIPT = PROJECT_ROOT / "scripts" / "demo-reset.sh"


@pytest.fixture
def demo_repository(tmp_path: Path) -> Path:
    """Create a minimal repository with a tagged JavaScript checkpoint."""
    repository = tmp_path / "repository"
    (repository / "src").mkdir(parents=True)
    (repository / "demo").mkdir()
    (repository / "tests").mkdir()
    (repository / "src" / "cart.js").write_text(
        "export const version = 'baseline';\n", encoding="utf-8"
    )
    _git(repository, "init", "--initial-branch=main")
    _git(repository, "config", "user.name", "Demo Test")
    _git(repository, "config", "user.email", "demo@example.invalid")
    _git(repository, "add", "src/cart.js")
    _git(repository, "commit", "-m", "Create baseline")
    _git(repository, "tag", "demo/baseline-2026-08")
    baseline = _git(repository, "rev-parse", "HEAD").stdout.strip()
    manifest = {
        "version": 1,
        "scenarios": {
            "javascript": {
                "description": "Test scenario",
                "ref": "demo/baseline-2026-08",
                "commit": baseline,
                "restorePaths": ["src/cart.js"],
                "generatedPaths": ["tests/cart.test.js"],
            }
        },
    }
    (repository / "demo" / "checkpoints.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    _git(repository, "add", "demo/checkpoints.json")
    _git(repository, "commit", "-m", "Add checkpoint manifest")
    return repository


def test_dry_run_preserves_allowlisted_change(demo_repository: Path) -> None:
    """Show planned operations without restoring a modified source file."""
    source = demo_repository / "src" / "cart.js"
    source.write_text("changed\n", encoding="utf-8")

    result = _reset(demo_repository, "--dry-run", "javascript")

    assert result.returncode == 0
    assert "Dry run: no files changed." in result.stdout
    assert source.read_text(encoding="utf-8") == "changed\n"


def test_unknown_scenario_is_rejected(demo_repository: Path) -> None:
    """Return a useful failure for a scenario absent from the manifest."""
    result = _reset(demo_repository, "--dry-run", "unknown")

    assert result.returncode != 0
    assert "unknown scenario 'unknown'" in result.stderr


def test_change_outside_allowlist_blocks_reset(demo_repository: Path) -> None:
    """Protect unrelated work even when noninteractive approval is supplied."""
    (demo_repository / "notes.txt").write_text("keep me\n", encoding="utf-8")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode != 0
    assert "outside the scenario allowlist" in result.stderr
    assert (demo_repository / "notes.txt").exists()


def test_confirmed_reset_restores_and_cleans(demo_repository: Path) -> None:
    """Restore tracked source and remove only configured generated output."""
    source = demo_repository / "src" / "cart.js"
    generated = demo_repository / "tests" / "cart.test.js"
    source.write_text("changed\n", encoding="utf-8")
    generated.write_text("generated\n", encoding="utf-8")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode == 0
    assert source.read_text(encoding="utf-8") == "export const version = 'baseline';\n"
    assert not generated.exists()


def test_ignored_generated_output_is_removed(demo_repository: Path) -> None:
    """Remove ignored output when its path is explicitly allowlisted."""
    ignored = demo_repository / ".gitignore"
    ignored.write_text("tests/cart.test.js\n", encoding="utf-8")
    _git(demo_repository, "add", ".gitignore")
    _git(demo_repository, "commit", "-m", "Ignore generated test")
    generated = demo_repository / "tests" / "cart.test.js"
    generated.write_text("generated\n", encoding="utf-8")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode == 0
    assert not generated.exists()


def test_staged_source_change_is_fully_restored(demo_repository: Path) -> None:
    """Restore both the index and worktree for an allowlisted source file."""
    source = demo_repository / "src" / "cart.js"
    source.write_text("staged change\n", encoding="utf-8")
    _git(demo_repository, "add", "src/cart.js")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode == 0
    assert _git(demo_repository, "status", "--short").stdout == ""


def test_tracked_generated_path_is_rejected(demo_repository: Path) -> None:
    """Refuse cleanup when a generated path has become tracked content."""
    generated = demo_repository / "tests" / "cart.test.js"
    generated.write_text("tracked\n", encoding="utf-8")
    _git(demo_repository, "add", "tests/cart.test.js")
    _git(demo_repository, "commit", "-m", "Track generated path")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode != 0
    assert "generated path is tracked" in result.stderr
    assert generated.exists()


def test_moved_checkpoint_tag_is_rejected(demo_repository: Path) -> None:
    """Require the friendly tag to resolve to its pinned full commit ID."""
    _git(demo_repository, "tag", "--force", "demo/baseline-2026-08", "HEAD")

    result = _reset(demo_repository, "--dry-run", "javascript")

    assert result.returncode != 0
    assert "does not match pinned commit" in result.stderr


def test_rename_from_outside_allowlist_is_rejected(demo_repository: Path) -> None:
    """Inspect both paths in Git's NUL-delimited rename status record."""
    notes = demo_repository / "notes.txt"
    notes.write_text("outside content\n", encoding="utf-8")
    _git(demo_repository, "add", "notes.txt")
    _git(demo_repository, "commit", "-m", "Add unrelated file")
    (demo_repository / "src" / "cart.js").unlink()
    notes.rename(demo_repository / "src" / "cart.js")
    _git(demo_repository, "add", "--all")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode != 0
    assert "notes.txt" in result.stderr


def test_pathspec_magic_is_rejected(demo_repository: Path) -> None:
    """Reject a manifest entry that Git could interpret as pathspec magic."""
    manifest_path = demo_repository / "demo" / "checkpoints.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["scenarios"]["javascript"]["restorePaths"] = [":(glob)**"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode != 0
    assert "unsafe literal path" in result.stderr


def test_pathspec_wildcard_is_rejected(demo_repository: Path) -> None:
    """Reject wildcard syntax that Git could expand during forced cleanup."""
    manifest_path = demo_repository / "demo" / "checkpoints.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["scenarios"]["javascript"]["generatedPaths"] = ["tests/*.js"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = _reset(demo_repository, "--yes", "javascript")

    assert result.returncode != 0
    assert "unsafe literal path" in result.stderr


def test_repository_checkpoint_contains_intentional_starters() -> None:
    """Verify the real pinned checkpoint contains both demo source targets."""
    scenario = load_scenario(
        PROJECT_ROOT / "demo" / "checkpoints.json", "starter"
    )
    resolved_tag = _git(
        PROJECT_ROOT, "rev-parse", f"{scenario.ref}^{{commit}}"
    ).stdout.strip()

    cart = _git(
        PROJECT_ROOT, "show", f"{scenario.commit}:src/cart.js"
    ).stdout
    inventory = _git(
        PROJECT_ROOT, "show", f"{scenario.commit}:src/inventory_legacy.py"
    ).stdout

    assert resolved_tag == scenario.commit
    assert "i <= cart.items.length" in cart
    assert "user.cardNumber" in cart
    assert '"SELECT qty FROM stock WHERE sku = \'" + sku' in inventory


def _reset(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(RESET_SCRIPT), *arguments],
        cwd=repository,
        capture_output=True,
        check=False,
        text=True,
    )


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repository,
        capture_output=True,
        check=True,
        text=True,
    )