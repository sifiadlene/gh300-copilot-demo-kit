#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
"""Validate completeness and freshness of the GH-300 coverage matrix."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = PROJECT_ROOT / "docs" / "gh300-coverage.md"
DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "gh300-objectives.json"
MAX_REVIEW_AGE_DAYS = 180
VALID_STATUSES = {"mapped", "implemented", "verified"}


class CoverageValidationError(ValueError):
    """Raised when the coverage matrix does not satisfy its release contract."""


@dataclass(frozen=True)
class ObjectiveRow:
    """Represent one parsed GH-300 objective row."""

    identifier: str
    cells: tuple[str, ...]
    domain: str
    statement: str
    artifact: str
    status: str
    reviewed: dt.date


def parse_rows(matrix_path: Path) -> list[ObjectiveRow]:
    """Parse objective rows from a Markdown coverage matrix.

    Args:
        matrix_path: Path to the Markdown matrix.

    Returns:
        Parsed objective rows.

    Raises:
        FileNotFoundError: If the matrix does not exist.
        CoverageValidationError: If a row has invalid columns or a review date.
    """
    content = matrix_path.read_text(encoding="utf-8")
    rows: list[ObjectiveRow] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        if not line.startswith("| GH300-"):
            continue
        cells = _split_markdown_row(line)
        rows.append(_parse_row(cells, line_number))
    return rows


def _split_markdown_row(line: str) -> tuple[str, ...]:
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in line.strip()[1:-1]:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    current.append("\\" if escaped else "")
    cells.append("".join(current).strip())
    return tuple(cells)


def _parse_row(cells: tuple[str, ...], line_number: int) -> ObjectiveRow:
    if len(cells) != 12:
        raise CoverageValidationError(
            f"line {line_number}: expected 12 columns, found {len(cells)}"
        )
    try:
        reviewed = dt.date.fromisoformat(cells[11])
    except ValueError as error:
        raise CoverageValidationError(
            f"line {line_number}: invalid review date {cells[11]!r}"
        ) from error
    return ObjectiveRow(
        cells[0], cells, cells[1], cells[2], cells[5], cells[10], reviewed
    )


def load_manifest(manifest_path: Path) -> dict[str, tuple[str, str]]:
    """Load the versioned objective contract keyed by objective ID.

    Args:
        manifest_path: Path to the canonical objective JSON snapshot.

    Returns:
        Mapping from ID to expected domain and statement.

    Raises:
        OSError: If the manifest cannot be read.
        CoverageValidationError: If the manifest shape or IDs are invalid.
    """
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    objectives = data.get("objectives")
    if not isinstance(objectives, list):
        raise CoverageValidationError("manifest objectives must be a list")
    contract = _manifest_contract(objectives)
    if len(contract) != len(objectives):
        raise CoverageValidationError("manifest contains duplicate objective IDs")
    return contract


def _manifest_contract(objectives: list[object]) -> dict[str, tuple[str, str]]:
    contract: dict[str, tuple[str, str]] = {}
    for objective in objectives:
        if not isinstance(objective, dict):
            raise CoverageValidationError("manifest objective must be an object")
        identifier = objective.get("id")
        domain = objective.get("domain")
        statement = objective.get("statement")
        fields = (identifier, domain, statement)
        if not all(isinstance(value, str) and value for value in fields):
            raise CoverageValidationError("manifest objective fields must be strings")
        contract[identifier] = (domain, statement)
    return contract


def validate_coverage(
    matrix_path: Path,
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    repository_root: Path = PROJECT_ROOT,
    release: bool = False,
    today: dt.date | None = None,
) -> list[ObjectiveRow]:
    """Validate IDs, required values, statuses, and review freshness.

    Args:
        matrix_path: Path to the Markdown matrix.
        manifest_path: Path to the canonical objective snapshot.
        repository_root: Root used to resolve artifact paths.
        release: Require every objective to have verified status.
        today: Date used for deterministic freshness checks.

    Returns:
        Validated objective rows.

    Raises:
        CoverageValidationError: If any matrix contract is violated.
    """
    rows = parse_rows(matrix_path)
    contract = load_manifest(manifest_path)
    errors = _collect_errors(
        rows, contract, repository_root, today or dt.date.today(), release
    )
    if errors:
        raise CoverageValidationError("\n".join(errors))
    return rows


def _collect_errors(
    rows: list[ObjectiveRow],
    contract: dict[str, tuple[str, str]],
    repository_root: Path,
    today: dt.date,
    release: bool,
) -> list[str]:
    identifiers = [row.identifier for row in rows]
    identifier_set = set(identifiers)
    errors: list[str] = []
    duplicates = sorted(
        {item for item in identifiers if identifiers.count(item) > 1}
    )
    if duplicates:
        errors.append(f"duplicate IDs: {', '.join(duplicates)}")
    expected_ids = set(contract)
    if missing := sorted(expected_ids - identifier_set):
        errors.append(f"missing IDs: {', '.join(missing)}")
    if unexpected := sorted(identifier_set - expected_ids):
        errors.append(f"unexpected IDs: {', '.join(unexpected)}")
    errors.extend(_row_errors(rows, contract, repository_root, today, release))
    return errors


def _row_errors(
    rows: list[ObjectiveRow],
    contract: dict[str, tuple[str, str]],
    repository_root: Path,
    today: dt.date,
    release: bool,
) -> list[str]:
    errors: list[str] = []
    for row in rows:
        if any(not cell for cell in row.cells):
            errors.append(f"{row.identifier}: contains an empty required field")
        if row.status not in VALID_STATUSES:
            errors.append(f"{row.identifier}: invalid status {row.status!r}")
        if expected := contract.get(row.identifier):
            if (row.domain, row.statement) != expected:
                errors.append(
                    f"{row.identifier}: domain or statement differs from manifest"
                )
        if row.status in {"implemented", "verified"}:
            artifact = repository_root / row.artifact.strip("`")
            if not artifact.exists():
                errors.append(
                    f"{row.identifier}: artifact does not exist: {row.artifact}"
                )
        if release and row.status != "verified":
            errors.append(f"{row.identifier}: release requires verified status")
        age = (today - row.reviewed).days
        if age < 0:
            errors.append(f"{row.identifier}: review date is in the future")
        elif age > MAX_REVIEW_AGE_DAYS:
            errors.append(f"{row.identifier}: review is stale at {age} days")
    return errors


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", nargs="?", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--release", action="store_true")
    return parser


def main() -> int:
    """Run coverage validation and return a process exit code.

    Returns:
        Zero for a valid matrix, otherwise one.
    """
    args = create_parser().parse_args()
    try:
        rows = validate_coverage(
            args.matrix, manifest_path=args.manifest, release=args.release
        )
    except (CoverageValidationError, OSError, json.JSONDecodeError) as error:
        print(f"Coverage validation failed:\n{error}", file=sys.stderr)
        return EXIT_FAILURE
    gate = "release" if args.release else "structural"
    print(f"Coverage validation passed: {len(rows)} objectives, {gate} gate.")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())