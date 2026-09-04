---
title: GH-300 GitHub Copilot Demo Kit
description: Modular hands-on demonstrations covering every objective in the GH-300 study guide
ms.date: 2026-09-04
ms.topic: tutorial
---

## GH-300 GitHub Copilot demo kit

A modular, hands-on workshop aligned with the
[GH-300 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-300)
effective August 7, 2026. The target is complete objective coverage plus a
curated 60-minute presentation route.

The implementation is in progress. The
[coverage matrix](docs/gh300-coverage.md) records all 41 study-guide bullets,
their planned evidence, and verification state. Run
`uv run python scripts/validate_coverage.py` to detect missing or stale rows.
The stricter `--release` gate remains intentionally red until all labs have
been implemented and manually verified.

## Workshop routes

| Route | Purpose | Current entry point |
|---|---|---|
| 60-minute core | Highest-value demonstration from every exam domain | This page |
| Full workshop | Independent labs for exhaustive hands-on coverage | `docs/labs/` |
| Presenter preparation | Entitlements, checkpoints, fallbacks, and timing | Planned in `docs/presenter-guide.md` |

Start with the [responsible AI lab](docs/labs/01-responsible-ai.md), then use
the feature demonstrations below. Each demonstration is being converted into
an independent checkpoint so a prior generated edit cannot affect a later lab.

## Current implementation status

* All 41 objectives are mapped to artifacts and verification evidence
* Responsible AI scenarios cover the previously missing 15-20% domain
* Coverage validation has automated tests and a stale-review gate
* The immutable starter tag and guarded reset tool isolate JavaScript and
   Python demonstrations
* IDE, CLI, review, agent, MCP, architecture, prompting, productivity, and
   safeguard scripts remain available below while they are split into labs
* Fixtures, CI, presenter guidance, and hosted-flow fallbacks are the next
   implementation milestone

## Reset a demonstration

Inspect a reset before changing files:

```bash
scripts/demo-reset.sh --dry-run javascript
```

After reviewing the allowlist, restore the scenario:

```bash
scripts/demo-reset.sh javascript
```

Use `python`, `javascript`, or `starter`. The command refuses to run if the
working tree contains changes outside that scenario's allowlist. See the
[checkpoint guide](docs/demo-checkpoints.md) before creating or replacing
checkpoint tags.

---

## 0. Setup (5 min, do before the audience arrives)

1. Open this folder in VS Code (or a JetBrains IDE / Visual Studio for the IDE-parity talking point).
2. Sign in: Command Palette > `GitHub Copilot: Sign In`. Confirm the Copilot icon in the status bar
   shows an active state.
3. Install the CLI: `npm install -g @github/copilot`, then run `copilot` once and `/login`.
4. Optional: set a personal access token if you want the GitHub MCP server in `.vscode/mcp.json` to start.
5. Keep `src/cart.js` and `src/inventory_legacy.py` closed — you will open them live.

**Files in this kit**

| Path | What it demonstrates |
|---|---|
| `src/cart.js` | Off-by-one bug, logged card number, no tests — inline suggestions, `/fix`, review, tests |
| `src/inventory_legacy.py` | SQL injection, no types, no docs — modernization, refactor, security, docs |
| `.github/copilot-instructions.md` | Repository-wide custom instructions |
| `.github/instructions/python.instructions.md` | Path-scoped instructions via `applyTo` |
| `.github/prompts/*.prompt.md` | Reusable prompt files for consistent responses |
| `.vscode/settings.json` | Enabling / disabling Copilot per language, instruction-file opt-in |
| `.vscode/mcp.json` | MCP servers for agent mode |
| `admin/content-exclusion-example.yml` | Content exclusion syntax |

---

## Part A — Use GitHub Copilot in the IDE

### Demo 1 — Enable and scope Copilot (2 min)
Open `.vscode/settings.json` and walk the `github.copilot.enable` map.
Flip `"plaintext": false` to `true`, open a `.txt` file, and show suggestions appear.
Point at the status-bar icon as the per-file enablement indicator.

**Says:** enablement is global, per-language, and per-workspace.

### Demo 2 — Inline suggestions and Next Edit Suggestions (3 min)
In `src/cart.js`, put the cursor at the end of the file and type:

```js
// Returns the cart total in integer cents, including tax
export function totalWithTax(cart, taxRate)
```

Accept with `Tab`, cycle alternatives with `Alt+]` / `Alt+[`, accept word-by-word with `Ctrl+->`.
Then rename `subtotal` to `cartSubtotal` and let Next Edit Suggestions propose the follow-on edits.

**Says:** ghost text, partial accept, and edit-aware suggestions are different features.

### Demo 3 — Inline chat and the chat panel (4 min)
Select the `subtotal` function, press `Ctrl+I` and ask:

> Why does this throw on the last iteration? Fix it and keep the same signature.

Then open the chat panel and run, in order:
- `/explain` on the selection
- `/fix` on `checkout`
- `/tests` for `cart.js`
- `@workspace where is the discount percentage validated?`
- `#file:src/cart.js summarise the public API in a table`

**Says:** slash commands, chat participants (`@workspace`, `@terminal`, `@vscode`, `@github`),
and context variables (`#file`, `#selection`, `#codebase`) are the three chat building blocks.
Mention the limits out loud: chat has no memory of other sessions, a bounded context window,
and per-plan rate limits; use the thumbs-up/down control to send feedback.

### Demo 4 — Copilot Edits (4 min)
Open Copilot Edits, add both `src/cart.js` and `src/inventory_legacy.py` to the working set, and ask:

> Money must be handled as integer cents across both files. Update the code and any callers,
> and keep the public function names unchanged.

Review the diff per file, accept one, discard the other, then undo.

**Says:** Edits is multi-file, diff-first, and reversible — the middle ground between chat and agent mode.

### Demo 5 — Agent mode (5 min)
Switch the chat to **Agent**, then ask:

> Add a pytest suite for src/inventory_legacy.py, create the tests directory layout if needed,
> run the tests, and fix anything that fails.

Let it plan, edit files, and request terminal approval. Point out the tool-approval prompt.

**Says:** agent mode chooses its own files and tools, iterates on failures, and asks before running commands.

### Demo 6 — MCP in agent mode (3 min)
Open `.vscode/mcp.json`, start the servers, then in agent mode ask:

> Using the GitHub tools, list the open issues on this repository and draft a fix plan for the oldest one.

Show the tool picker listing MCP-provided tools.

**Says:** MCP extends agent mode with external systems using one open protocol; servers are configured
per workspace or per user, and each tool call is approval-gated.

### Demo 7 — Agent sessions and delegation (3 min)
On github.com, open the Agents panel (or assign an issue to Copilot) and delegate:

> Fix the off-by-one bug in subtotal() and open a pull request.

Show the session log, the branch it creates, and the draft PR. Mention sub-agents: the session
delegates focused units of work so the main context window is not consumed by side quests.

**Says:** delegated sessions run on GitHub-hosted compute; you review the PR like any other contributor.

### Demo 8 — Copilot CLI (5 min)
In a terminal at the repo root:

```bash
copilot                       # interactive session
```

Then, inside the session:
- `/help`, `/model`, `/clear`, `/session`, `/exit`
- ask: `explain what src/inventory_legacy.py does and list its risks`
- ask: `write a bash script that backs up every .py file into backups/ with a timestamp, then run it`
- ask: `rename src/cart.js to src/cart.mjs and update the imports`

And non-interactively:

```bash
copilot -p "generate a .gitignore for a python and node project"
```

**Says:** the CLI brings Copilot to the terminal for people who do not live in an IDE — it can
explain commands, generate scripts, and act on files, and it asks for approval before changing anything.

---

## Part B — Code review, collaboration, and organization settings

### Demo 9 — Code review and custom review standards (4 min)
Select `checkout` in `src/cart.js` > right-click > **Copilot** > **Review and Comment**.
Then open `.github/copilot-instructions.md`, show the *Review standards* section, and re-run the review
to demonstrate that the guidance changes the comments.
On github.com, request a review from Copilot on a pull request.

**Says:** review standards are instructions-file driven, so review output is consistent across the team.

### Demo 10 — PR summaries, Spaces, and Spark (3 min)
- On an open PR, use **Copilot > Generate summary** and show the walkthrough it writes.
- Open a **Copilot Space**, attach this repo plus the study guide link, and ask a question that needs both.
- In **Spark**, describe a tiny inventory dashboard and let it build and deploy the app.

**Says:** Spaces are curated, shareable context; Spark goes from prompt to running app.

### Demo 11 — Prompt files for consistent responses (3 min)
Run `/unit-tests` and `/security-review` from the chat box — both come from `.github/prompts/`.
Run the security one twice to show the response shape is stable.

**Says:** prompt files version-control your best prompts so everyone gets the same quality.

### Demo 12 — Organization settings, audit log, and the REST API (4 min)
In organization settings > Copilot:
- Policies: enable/disable Copilot in the IDE vs on github.com, Copilot code review policy,
  suggestions matching public code, and MCP availability.
- Access: assign seats by team or user.
- Audit log: filter on `copilot` events (policy changes, seat assignment, content-exclusion updates).

Then show the API:

```bash
gh api /orgs/CONTOSO/copilot/billing
gh api /orgs/CONTOSO/copilot/billing/seats
gh api --method POST /orgs/CONTOSO/copilot/billing/selected_teams -f 'selected_teams[]=platform'
```

**Says:** everything in the UI is scriptable, and every change is auditable.

---

## Part C — Data, architecture, and the suggestion lifecycle (whiteboard, 4 min)

No code for this one. Draw the path and narrate it while a suggestion is being generated:

1. IDE gathers context: current file, neighbouring open tabs, path and language.
2. The Copilot extension builds the prompt and sends it over TLS to the Copilot proxy.
3. The proxy applies filters — content exclusions, toxicity, and the public-code match filter.
4. The model returns candidate completions; post-processing drops low-quality or filtered results.
5. The IDE renders ghost text. Nothing is retained as training data for business and enterprise plans;
   prompts and suggestions are discarded after the response for Copilot in the IDE.

Close on limitations: the model can be confidently wrong, has a training cutoff, has no knowledge of
your private runtime state, and cannot guarantee that generated code is licensed the way you assume.
Every suggestion needs human validation, tests, and review.

---

## Part D — Prompt engineering and context crafting (5 min)

Run these three prompts back to back against `src/inventory_legacy.py` and compare the answers.

**Vague (zero context):**
> make this better

**Zero-shot, well structured** — goal, context, constraints, output format:
> Refactor `reorder_report` for readability. Keep the function name and return type. Use a dataclass
> for each row, add type hints, and return a list of formatted strings unchanged in content.
> Show only the new function.

**Few-shot** — give it a pattern to imitate:
> Rewrite the remaining functions in the style of this example:
> ```python
> def get_stock(conn: sqlite3.Connection, sku: str) -> int:
>     """Return the on-hand quantity for a SKU, or 0 when unknown."""
>     row = conn.execute("SELECT qty FROM stock WHERE sku = ?", (sku,)).fetchone()
>     return row[0] if row else 0
> ```

Then show context crafting: open a second relevant file, keep it in a tab, and re-ask — the answer
improves because open tabs are part of the context. Point at `.github/copilot-instructions.md`
as the durable version of the same idea, and at chat history as the per-session version.

**Says:** prompt = goal + context + constraints + output format; iterate rather than restating.

---

## Part E — Developer productivity (6 min)

Run these in one pass over `src/inventory_legacy.py`:

| Ask | Objective it demonstrates |
|---|---|
| `/explain this module to someone who has never seen the codebase` | Accelerate learning, reduce context switching |
| `Add Google-style docstrings to every public function` | Documentation |
| `Modernize this to Python 3.11: type hints, dataclasses, parameterised SQL, pathlib` | Legacy modernization + refactoring |
| `Generate 20 rows of realistic sample stock data as CSV` | Sample data generation |
| `Generate a pytest suite` (use `/unit-tests`) | Unit tests |
| `List the edge cases this module does not handle, then write assertions for each` | Edge cases and assertions |
| `Write an integration test that runs against a temporary sqlite database` | Integration tests |
| `/security-review` | Security improvements |
| `bulk_import opens a cursor per row — optimise it and explain the trade-off` | Performance optimization |

**Says:** the value is the loop — generate, read, validate, test — not the first answer.

---

## Part F — Privacy, content exclusions, and safeguards (5 min)

### Demo 13 — Content exclusions
Open `admin/content-exclusion-example.yml` and read the syntax, then configure a real one:
repository **Settings > Copilot > Content exclusion**, add `/src/cart.js`, save.
Reload the window, open `src/cart.js`, and show that the Copilot status icon reports the file as
excluded and inline suggestions no longer appear. Ask chat about the file and show the reduced answer.

Troubleshooting talking points: changes take up to ~30 minutes to propagate, reload the window to force
a refresh, patterns are `fnmatch`-style, exclusions apply to suggestions and chat context but do not
retroactively remove anything already committed, and a file excluded in one repository is still visible
if it is duplicated in another.

### Demo 14 — Public code matching filter
In organization settings, enable **Suggestions matching public code: blocked**. Back in the IDE, type a
prompt likely to reproduce a well-known snippet and show the suggestion being withheld.

### Demo 15 — Ownership and validation
State it plainly: you own the code you accept, you are responsible for validating it, the model does not
guarantee licence provenance, and duplication detection reduces but does not eliminate that risk.

---

## Closing (2 min)

Recap against the exam weights: features 25-30%, data and architecture 10-15%, prompt engineering 10-15%,
productivity 10-15%, privacy and safeguards 10-15%. Point the audience at GitHub Copilot Fundamentals
Parts 1 and 2 on Microsoft Learn for the guided path.
