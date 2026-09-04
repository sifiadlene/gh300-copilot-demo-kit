#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
"""Validate a demo-reset scenario and protect unrelated Git changes."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
FULL_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
REF_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")
SECTION_MARKERS = {"--RESTORE--", "--GENERATED--"}


class ResetGuardError(ValueError):
    """Raised when a reset scenario or repository state is unsafe."""


@dataclass(frozen=True)
class Scenario:
    """Represent one validated checkpoint scenario."""

    ref: str
    commit: str
    restore_paths: tuple[str, ...]
    generated_paths: tuple[str, ...]


def load_scenario(manifest_path: Path, name: str) -> Scenario:
    """Load and validate one scenario from a checkpoint manifest.

    Args:
        manifest_path: Path to the checkpoint manifest.
        name: Scenario key to load.

    Returns:
        Validated scenario configuration.

    Raises:
        ResetGuardError: If the manifest or scenario is invalid.
    """
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ResetGuardError("checkpoint manifest version must be 1")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, dict):
        raise ResetGuardError("manifest scenarios must be an object")
    raw = scenarios.get(name)
    if not isinstance(raw, dict):
        available = ", ".join(sorted(str(item) for item in scenarios))
        raise ResetGuardError(f"unknown scenario {name!r}; available: {available}")

    ref = raw.get("ref")
    commit = raw.get("commit")
    if not isinstance(ref, str) or not REF_PATTERN.fullmatch(ref):
        raise ResetGuardError("scenario ref has an invalid format")
    if not isinstance(commit, str) or not FULL_COMMIT_PATTERN.fullmatch(commit):
        raise ResetGuardError("scenario commit must be a full lowercase object ID")
    restore_paths = _validated_paths(raw.get("restorePaths"), "restorePaths")
    generated_paths = _validated_paths(raw.get("generatedPaths"), "generatedPaths")
    _validate_nonoverlap(restore_paths, generated_paths)
    return Scenario(ref, commit, restore_paths, generated_paths)


def _validated_paths(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ResetGuardError(f"scenario field {field!r} must be a non-empty list")
    if not all(isinstance(item, str) for item in value):
        raise ResetGuardError(f"every path in {field!r} must be a string")
    paths = tuple(value)
    if len(set(paths)) != len(paths):
        raise ResetGuardError(f"scenario field {field!r} contains duplicate paths")
    for value_path in paths:
        path = PurePosixPath(value_path)
        invalid = (
            value_path in SECTION_MARKERS
            or value_path.startswith(":")
            or path.is_absolute()
            or path == PurePosixPath(".")
            or ".." in path.parts
            or str(path) != value_path
            or any(character in value_path for character in "*?[]\\")
            or any(ord(character) < 32 for character in value_path)
        )
        if invalid:
            raise ResetGuardError(f"unsafe literal path in {field!r}: {value_path!r}")
    return paths


def _validate_nonoverlap(
    restore_paths: tuple[str, ...], generated_paths: tuple[str, ...]
) -> None:
    for restore_path in restore_paths:
        for generated_path in generated_paths:
            if _is_within(restore_path, generated_path) or _is_within(
                generated_path, restore_path
            ):
                raise ResetGuardError(
                    "restorePaths and generatedPaths must not overlap"
                )


def validate_repository(repository: Path, scenario: Scenario) -> None:
    """Validate checkpoint identity, contents, and current repository changes.

    Args:
        repository: Git repository root.
        scenario: Validated scenario configuration.

    Raises:
        ResetGuardError: If reset operations would be unsafe.
    """
    resolved = _git_text(repository, "rev-parse", f"{scenario.ref}^{{commit}}")
    if resolved != scenario.commit:
        raise ResetGuardError(
            f"checkpoint ref {scenario.ref!r} does not match pinned commit"
        )
    for path in scenario.restore_paths:
        _git(repository, "cat-file", "-e", f"{scenario.commit}:{path}")
    for path in scenario.generated_paths:
        tracked = _git(repository, "ls-files", "-z", "--", path).stdout
        if tracked:
            raise ResetGuardError(
                f"generated path is tracked and will not be removed: {path}"
            )
    _validate_changed_paths(repository, scenario)


def _validate_changed_paths(repository: Path, scenario: Scenario) -> None:
    output = _git(
        repository, "status", "--porcelain=v1", "-z", "--untracked-files=all"
    ).stdout
    records = output.split(b"\0")
    blocked: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            raise ResetGuardError("could not parse Git worktree status")
        status = record[:2]
        paths = [record[3:].decode("utf-8", errors="surrogateescape")]
        if b"R" in status or b"C" in status:
            if index >= len(records) or not records[index]:
                raise ResetGuardError("incomplete Git rename or copy status")
            paths.append(records[index].decode("utf-8", errors="surrogateescape"))
            index += 1
        blocked.extend(path for path in paths if not _is_allowed(path, scenario))
    if blocked:
        formatted = "\n  ".join(sorted(set(blocked)))
        raise ResetGuardError(
            f"changes outside the scenario allowlist:\n  {formatted}\n"
            "commit, stash, or revert these changes first"
        )


def _is_allowed(path: str, scenario: Scenario) -> bool:
    return any(
        _is_within(path, allowed)
        for allowed in (*scenario.restore_paths, *scenario.generated_paths)
    )


def _is_within(path: str, allowed: str) -> bool:
    return path == allowed or path.startswith(f"{allowed}/")


def emit_scenario(scenario: Scenario) -> None:
    """Write a shell-readable scenario after all validation succeeds.

    Args:
        scenario: Validated scenario to emit.
    """
    print(scenario.ref)
    print(scenario.commit)
    print("--RESTORE--")
    print(*scenario.restore_paths, sep="\n")
    print("--GENERATED--")
    print(*scenario.generated_paths, sep="\n")


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=repository,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.decode("utf-8", errors="replace").strip()
        message = stderr or f"Git command failed: {' '.join(arguments)}"
        raise ResetGuardError(message) from error


def _git_text(repository: Path, *arguments: str) -> str:
    return _git(repository, *arguments).stdout.decode("ascii").strip()


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("scenario")
    return parser


def main() -> int:
    """Validate and emit one scenario, returning a process exit code.

    Returns:
        Zero when safe, otherwise one.
    """
    args = create_parser().parse_args()
    try:
        scenario = load_scenario(args.manifest, args.scenario)
        validate_repository(args.repository, scenario)
    except (OSError, json.JSONDecodeError, ResetGuardError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return EXIT_FAILURE
    emit_scenario(scenario)
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
