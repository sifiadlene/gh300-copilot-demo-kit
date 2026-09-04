---
applyTo: "**/*.py"
---
# Python-specific instructions

- Use `dataclasses` for value objects instead of bare dictionaries.
- Prefer explicit `ValueError` / `KeyError` over silent `None` returns.
- Money is `int` cents. Never `float`.
- Log with the `logging` module, never `print`.
- Any function longer than 30 lines should be decomposed.
