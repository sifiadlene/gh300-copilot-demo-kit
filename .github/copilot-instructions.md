# Copilot instructions — GH-300 demo repository

## Project context
This is a small demo repository used to showcase GitHub Copilot capabilities.
It contains a legacy Python inventory module and a JavaScript shopping-cart module,
both intentionally imperfect so that Copilot has real work to do.

## Coding standards
- Python: target 3.11+, use type hints on every public function, prefer `pathlib` over `os.path`,
  raise specific exceptions rather than returning error codes.
- JavaScript: ES modules only, `const`/`let` (never `var`), no default exports.
- Every public function needs a docstring / JSDoc block explaining parameters, return value and raised errors.
- Currency is always handled in integer cents, never floats.

## Testing standards
- Python tests use `pytest`, live in `tests/`, and are named `test_<module>.py`.
- JavaScript tests use `node:test` and `node:assert/strict`.
- Every test file must cover: the happy path, at least two boundary values, and one failure path.
- Never write a test that asserts on a private helper.

## Security expectations
- Never build SQL or shell commands with string concatenation.
- Validate and normalise all external input at the boundary.
- Never log secrets, tokens or full payment details.

## Review standards
When reviewing, comment only on correctness, security, and public-API clarity.
Do not comment on formatting — that is handled by the formatter.
