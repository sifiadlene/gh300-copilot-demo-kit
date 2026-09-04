# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
"""Tests for the GH-300 coverage matrix validator."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from scripts.validate_coverage import (
    MAX_REVIEW_AGE_DAYS,
    PROJECT_ROOT,
    CoverageValidationError,
    parse_rows,
    validate_coverage,
)

MATRIX_PATH = PROJECT_ROOT / "docs" / "gh300-coverage.md"
REVIEW_DATE = dt.date(2026, 9, 4)


def test_repository_matrix_maps_every_objective() -> None:
    """Validate the checked-in source-of-truth matrix."""
    rows = validate_coverage(MATRIX_PATH, today=REVIEW_DATE)

    assert len(rows) == 41


@pytest.mark.parametrize(
    ("age_days", "is_valid"),
    [(MAX_REVIEW_AGE_DAYS, True), (MAX_REVIEW_AGE_DAYS + 1, False)],
)
def test_review_age_boundary(
    tmp_path: Path, age_days: int, is_valid: bool
) -> None:
    """Accept the age limit and reject the first stale date."""
    matrix = _copy_matrix(tmp_path)
    today = REVIEW_DATE + dt.timedelta(days=age_days)

    if is_valid:
        assert len(validate_coverage(matrix, today=today)) == 41
    else:
        with pytest.raises(CoverageValidationError, match="review is stale"):
            validate_coverage(matrix, today=today)


def test_duplicate_objective_is_rejected(tmp_path: Path) -> None:
    """Reject a duplicated objective even when all expected IDs exist."""
    matrix = _copy_matrix(tmp_path)
    first_row = parse_rows(matrix)[0]
    with matrix.open("a", encoding="utf-8") as matrix_file:
        matrix_file.write("\n| " + " | ".join(first_row.cells) + " |\n")

    with pytest.raises(CoverageValidationError, match="duplicate IDs"):
        validate_coverage(matrix, today=REVIEW_DATE)


def test_release_gate_requires_verified_rows() -> None:
    """Reject mapped and implemented rows at the explicit release gate."""
    with pytest.raises(CoverageValidationError, match="release requires verified"):
        validate_coverage(MATRIX_PATH, release=True, today=REVIEW_DATE)


def test_changed_study_guide_statement_is_rejected(tmp_path: Path) -> None:
    """Detect drift from the canonical study-guide objective snapshot."""
    matrix = _copy_matrix(tmp_path)
    content = matrix.read_text(encoding="utf-8").replace(
        "Describe risks and limitations of Generative AI tools",
        "Describe arbitrary replacement text",
        1,
    )
    matrix.write_text(content, encoding="utf-8")

    with pytest.raises(CoverageValidationError, match="differs from manifest"):
        validate_coverage(matrix, today=REVIEW_DATE)


def test_implemented_artifact_must_exist(tmp_path: Path) -> None:
    """Reject implemented coverage that points to a missing artifact."""
    matrix = _copy_matrix(tmp_path)
    content = matrix.read_text(encoding="utf-8").replace(
        "`docs/labs/01-responsible-ai.md`",
        "`docs/labs/missing.md`",
        1,
    )
    matrix.write_text(content, encoding="utf-8")

    with pytest.raises(CoverageValidationError, match="artifact does not exist"):
        validate_coverage(
            matrix, repository_root=PROJECT_ROOT, today=REVIEW_DATE
        )


def test_malformed_objective_row_is_rejected(tmp_path: Path) -> None:
    """Reject a recognized objective row with the wrong column count."""
    matrix = tmp_path / "coverage.md"
    matrix.write_text("| GH300-RAI-01 | too few |\n", encoding="utf-8")

    with pytest.raises(CoverageValidationError, match="expected 12 columns"):
        validate_coverage(matrix, today=REVIEW_DATE)


def test_missing_matrix_is_reported(tmp_path: Path) -> None:
    """Raise a specific error when the requested matrix is absent."""
    with pytest.raises(FileNotFoundError):
        validate_coverage(tmp_path / "missing.md", today=REVIEW_DATE)


def _copy_matrix(tmp_path: Path) -> Path:
    target = tmp_path / "coverage.md"
    target.write_text(MATRIX_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return target