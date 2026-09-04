---
mode: agent
description: Generate a complete pytest suite for the selected module.
---
Generate a `pytest` suite for the module I have open.

Follow the repository standards in `.github/copilot-instructions.md`.

Structure the output as:
1. A short list of the behaviours you identified, before any code.
2. The test file itself, ready to save under `tests/`.
3. A table of the edge cases you deliberately covered and the ones you decided were out of scope.

Requirements:
- One test function per behaviour, named `test_<behaviour>`.
- Parametrise boundary values rather than copy-pasting cases.
- Include at least one test that asserts the exception type and message.
- Do not modify the module under test.
