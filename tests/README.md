---
title: GH-300 Demo Tests
description: Test layout for stable kit validation and tests generated during demonstrations
ms.date: 2026-09-04
ms.topic: reference
---

## Test layout

Stable repository tests validate workshop infrastructure:

* `test_validate_coverage.py` checks objective traceability and release gates
* `test_demo_reset.py` exercises reset dry runs, safety refusal, scenario
	validation, restoration, and generated-file cleanup

Tests generated during demonstrations also land here, but are isolated by the
checkpoint manifest.

Suggested demo order:

1. Generate `test_inventory_legacy.py` from the reusable prompt file.
2. Generate `cart.test.js` from Copilot Chat with `/tests`.

Reset the corresponding scenario before moving to another lab. Generated test
paths are removed only when they appear in that scenario's explicit allowlist.
