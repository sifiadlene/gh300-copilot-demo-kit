---
title: GH-300 Objective Coverage
description: Traceability matrix for the GH-300 skills measured as of August 7, 2026
ms.date: 2026-09-04
ms.topic: reference
---

## Scope and maintenance

This matrix is the release gate for the demo kit. It tracks every bullet in the
[official GH-300 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-300)
effective August 7, 2026. The guide remains authoritative if its wording or
weights change.

Review the source quarterly and whenever GitHub announces a material Copilot
product change. Update `data/gh300-objectives.json` first when the official
guide changes, then reconcile this matrix. Run
`uv run python scripts/validate_coverage.py` after editing it. A row reaches
`verified` only after its observable result has been reproduced using the
documented prerequisites.

Status values are `mapped`, `implemented`, and `verified`. Future artifacts are
listed as repository-relative paths so implementation work remains traceable.

## Coverage summary

| Domain | Weight | Objective rows | Core route | Full workshop |
|---|---:|---:|---|---|
| Responsible use | 15-20% | 5 | Scenario exercise | Full risk workshop |
| Copilot features | 25-30% | 15 | IDE, agent, CLI, review | All product labs |
| Data and architecture | 10-15% | 5 | Lifecycle activity | Lifecycle and data lab |
| Prompt and context engineering | 10-15% | 6 | Controlled comparison | Full context experiment |
| Developer productivity | 10-15% | 6 | Modernization loop | Python and JavaScript labs |
| Privacy and safeguards | 10-15% | 4 | Exclusion walkthrough | Admin and troubleshooting lab |
| Total | 100% | 41 | 60 minutes | Modular |

## Objective traceability

| ID | Domain | Study-guide statement | Mode | Lab | Artifact | Observable result | Prerequisite | Fallback | Verification | Status | Reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GH300-RAI-01 | Responsible use | Describe risks and limitations of Generative AI tools | guided | RAI scenarios | `docs/labs/01-responsible-ai.md` | Learner identifies hallucination, bias, security, privacy, IP, and overreliance risks | None | Presenter scenario cards | Completed risk rubric | implemented | 2026-09-04 |
| GH300-RAI-02 | Responsible use | Describe ethical and responsible AI usage | guided | RAI scenarios | `docs/labs/01-responsible-ai.md` | Learner applies fairness, reliability and safety, privacy and security, inclusiveness, transparency, and accountability | None | Presenter principle map | Completed principle mapping | implemented | 2026-09-04 |
| GH300-RAI-03 | Responsible use | Identify potential harms and mitigation strategies of AI usage | guided | RAI scenarios | `docs/labs/01-responsible-ai.md` | Learner connects affected stakeholders and harms to concrete mitigations | None | Prepared answer key | Completed mitigation table | implemented | 2026-09-04 |
| GH300-RAI-04 | Responsible use | Explain the need to validate AI output | live | Validate generated code | `src/cart.js` | Generated change is reviewed and tested before acceptance | VS Code and Copilot | Recorded diff and test output | Test and review evidence | mapped | 2026-09-04 |
| GH300-RAI-05 | Responsible use | Identify how to operate GitHub Copilot responsibly | guided | Responsible operation checklist | `docs/labs/01-responsible-ai.md` | Learner uses human approval, least privilege, redaction, tests, and escalation | None | Printable checklist | Checklist assessment | implemented | 2026-09-04 |
| GH300-FEA-01 | Copilot features | Enable Copilot in the IDE | live | IDE enablement | `.vscode/settings.json` | Copilot status and per-language enablement change are visible | Copilot entitlement and extension | Dated screenshots | Manual smoke test | mapped | 2026-09-04 |
| GH300-FEA-02 | Copilot features | Trigger Copilot through inline suggestions, chat, CLI, and agent mode | live | Interaction surfaces | `docs/labs/02-copilot-surfaces.md` | Learner invokes all four interaction surfaces | VS Code, Copilot CLI | Recorded surface tour | Surface checklist | mapped | 2026-09-04 |
| GH300-FEA-03 | Copilot features | Configure content exclusions for specific files or repositories | admin | Content exclusion | `admin/content-exclusion-example.yml` | Excluded file loses inline and chat context while control file remains available | Repository admin and supported plan | Dated screenshots | Positive and negative test | mapped | 2026-09-04 |
| GH300-FEA-04 | Copilot features | Define GitHub Copilot CLI and how it benefits developers | explain | CLI orientation | `docs/labs/06-copilot-cli.md` | Learner selects appropriate terminal use cases | Copilot CLI | Recorded terminal session | Knowledge check | mapped | 2026-09-04 |
| GH300-FEA-05 | Copilot features | Identify the steps for installing GitHub Copilot CLI | live | CLI setup | `docs/labs/06-copilot-cli.md` | Supported CLI installation and authentication are confirmed | Supported OS and account | Dated setup transcript | Prerequisite check | mapped | 2026-09-04 |
| GH300-FEA-06 | Copilot features | Describe key GitHub Copilot CLI features and commands | live | CLI commands | `docs/labs/06-copilot-cli.md` | Learner uses current help, model, session, clear, and exit commands | Authenticated Copilot CLI | Recorded terminal session | Command checklist | mapped | 2026-09-04 |
| GH300-FEA-07 | Copilot features | Use GitHub Copilot CLI interactively and in sessions | live | CLI sessions | `docs/labs/06-copilot-cli.md` | An interactive session is created, continued, and inspected | Authenticated Copilot CLI | Recorded terminal session | Session artifact | mapped | 2026-09-04 |
| GH300-FEA-08 | Copilot features | Generate scripts and manage files with GitHub Copilot CLI | live | CLI file operations | `docs/labs/06-copilot-cli.md` | CLI proposes a safe script and file change with approval | Clean demo checkpoint | Recorded terminal session | Diff and cleanup check | mapped | 2026-09-04 |
| GH300-FEA-09 | Copilot features | Use Agent Mode, Copilot Edits, and MCP for enhanced development and workflows; manage Agent Sessions and delegate tasks to Sub-Agents for optimized context usage | live | Agents, Edits, and MCP | `docs/labs/04-agents-edits-mcp.md` | Learner distinguishes modes, approves tools, inspects a session, and receives delegated findings | Copilot plan and MCP access | Dated recordings | Mode comparison checklist | mapped | 2026-09-04 |
| GH300-FEA-10 | Copilot features | Use Copilot for code review and coding assistance | live | Review and assistance | `src/cart.js` | Copilot produces actionable findings and a reviewed code change | Copilot code review | Saved sanitized review | Review rubric | mapped | 2026-09-04 |
| GH300-FEA-11 | Copilot features | Utilize Spaces, Spark, Pull Request summaries, and customizable review standards via instructions files | live | Collaboration features | `.github/copilot-instructions.md` | Learner observes grounded Space answers, a Spark app, a PR summary, and instruction-aware review | Enterprise access, Space, Spark, and PR | Dated recordings | Four-feature checklist | mapped | 2026-09-04 |
| GH300-FEA-12 | Copilot features | Understand the limits, options, feedback, and commands of GitHub Copilot Chat; include prompt file reuse for consistent responses | live | Chat controls | `.github/prompts/security-review.prompt.md` | Learner uses current commands, model/options, feedback, and a reusable prompt while identifying limitations | VS Code and Copilot | Dated screenshots | Chat checklist | mapped | 2026-09-04 |
| GH300-FEA-13 | Copilot features | Configure organization-wide policy management; enable Copilot Code Review policies and manage feature availability across IDEs and github.com | admin | Organization policies | `docs/labs/07-enterprise-administration.md` | Policy changes and affected surfaces are observed and rolled back | Organization owner in disposable organization | Redacted screenshots | Before and after policy check | mapped | 2026-09-04 |
| GH300-FEA-14 | Copilot features | Utilize audit log events | admin | Audit log | `docs/labs/07-enterprise-administration.md` | Learner filters Copilot events and connects them to an administrative action | Organization audit access | Redacted audit export | Event correlation | mapped | 2026-09-04 |
| GH300-FEA-15 | Copilot features | Manage subscriptions using the REST API | admin | Subscription API | `docs/labs/07-enterprise-administration.md` | Read-only billing and seat responses are inspected; mutations require confirmation and rollback | Organization owner and GitHub CLI | Redacted response fixtures | API response assertions | mapped | 2026-09-04 |
| GH300-ARC-01 | Data and architecture | Explain data usage, flow, and sharing | guided | Suggestion lifecycle | `docs/copilot-architecture.md` | Learner traces data actors and plan-specific handling without making blanket retention claims | None | Architecture diagram | Card ordering and knowledge check | mapped | 2026-09-04 |
| GH300-ARC-02 | Data and architecture | Describe input processing and prompt building | guided | Suggestion lifecycle | `docs/copilot-architecture.md` | Learner identifies prompt, cursor, nearby code, open-tab context, history, and instructions | None | Architecture diagram | Context classification | mapped | 2026-09-04 |
| GH300-ARC-03 | Data and architecture | Explain proxy filtering and post-processing | guided | Suggestion lifecycle | `docs/copilot-architecture.md` | Learner places service filters and post-processing in the correct lifecycle positions | None | Architecture diagram | Card ordering | mapped | 2026-09-04 |
| GH300-ARC-04 | Data and architecture | Visualize code suggestion lifecycle | guided | Suggestion lifecycle | `docs/copilot-architecture.md` | Learner orders collection, prompt construction, service, model, filtering, and rendering | None | Architecture diagram | Correct ordered flow | mapped | 2026-09-04 |
| GH300-ARC-05 | Data and architecture | Describe limitations of LLMs and Copilot | guided | Limitations review | `docs/labs/01-responsible-ai.md` | Learner explains probabilistic output, context bounds, knowledge limits, and variable language quality | None | Application card excerpts | Knowledge check | implemented | 2026-09-04 |
| GH300-PRM-01 | Prompt and context engineering | Describe prompt structure and context | live | Prompt experiment | `docs/labs/08-prompt-engineering.md` | Learner separates goal, context, constraints, examples, and output format | VS Code and Copilot | Prepared response set | Scored rubric | mapped | 2026-09-04 |
| GH300-PRM-02 | Prompt and context engineering | Understand how context is determined | live | Context experiment | `docs/labs/08-prompt-engineering.md` | Relevant and irrelevant open tabs and explicit attachments produce inspectable context references | VS Code and Copilot | Prepared response set | Reference inspection | mapped | 2026-09-04 |
| GH300-PRM-03 | Prompt and context engineering | Use zero-shot and few-shot prompting | live | Prompt experiment | `src/inventory_legacy.py` | Zero-shot and few-shot responses are compared against the same rubric | VS Code and Copilot | Prepared response set | Scored rubric | mapped | 2026-09-04 |
| GH300-PRM-04 | Prompt and context engineering | Apply best practices for prompt crafting | live | Prompt experiment | `docs/labs/08-prompt-engineering.md` | Learner removes ambiguity, decomposes work, supplies examples, and iterates | VS Code and Copilot | Prompt worksheet | Scored rubric | mapped | 2026-09-04 |
| GH300-PRM-05 | Prompt and context engineering | Explain prompt engineering principles | guided | Prompt debrief | `docs/labs/08-prompt-engineering.md` | Learner explains why specificity, grounding, examples, decomposition, and iteration affect results | None | Prompt worksheet | Knowledge check | mapped | 2026-09-04 |
| GH300-PRM-06 | Prompt and context engineering | Describe prompt process flow and chat history usage | live | History experiment | `docs/labs/08-prompt-engineering.md` | Clean and polluted threads demonstrate relevant-history management | VS Code and Copilot | Prepared response set | History comparison | mapped | 2026-09-04 |
| GH300-PRO-01 | Developer productivity | Use Copilot for code generation, refactoring, and documentation | live | Modernization loop | `src/inventory_legacy.py` | Generated code, refactor, and documentation changes are diff-reviewed | VS Code and Copilot | Saved diffs | Tests and review rubric | mapped | 2026-09-04 |
| GH300-PRO-02 | Developer productivity | Accelerate learning and reduce context switching | live | Codebase onboarding | `src/inventory_legacy.py` | Learner obtains a grounded module explanation and follows references without leaving the IDE | VS Code and Copilot | Prepared explanation | Accuracy checklist | mapped | 2026-09-04 |
| GH300-PRO-03 | Developer productivity | Generate sample data and modernize legacy code | live | Legacy modernization | `src/inventory_legacy.py` | Deterministic sample data and a typed, parameterized-SQL proposal are produced | VS Code and Copilot | Saved CSV and diff | Schema and test validation | mapped | 2026-09-04 |
| GH300-PRO-04 | Developer productivity | Generate unit and integration tests | live | Test generation | `.github/prompts/unit-tests.prompt.md` | Python unit and SQLite integration tests and JavaScript unit tests are generated | Python 3.11+, Node 24+ | Completed checkpoint tests | Test execution | mapped | 2026-09-04 |
| GH300-PRO-05 | Developer productivity | Identify edge cases and write assertions | live | Boundary analysis | `src/cart.js` | Empty, single-item, discount-boundary, invalid-input, and failure cases become assertions | Node 24+ | Completed checkpoint tests | Boundary coverage review | mapped | 2026-09-04 |
| GH300-PRO-06 | Developer productivity | Suggest security improvements and performance optimizations | live | Security and performance | `.github/prompts/security-review.prompt.md` | SQL injection, payment logging, input validation, and bulk insert performance receive evidence-backed changes | VS Code and Copilot | Saved review and benchmark | Security tests and benchmark | mapped | 2026-09-04 |
| GH300-PRV-01 | Privacy and safeguards | Configure content exclusions and editor settings | admin | Privacy controls | `admin/content-exclusion-example.yml` | Learner configures patterns and editor language scope, then tests excluded and control files | Repository admin and VS Code | Dated screenshots | Positive and negative test | mapped | 2026-09-04 |
| GH300-PRV-02 | Privacy and safeguards | Describe ownership and limitations of outputs | guided | Output responsibility | `docs/labs/09-privacy-safeguards.md` | Learner distinguishes applicable terms, user responsibility, code references, and lack of guaranteed provenance | None | Terms and application-card excerpts | Scenario knowledge check | mapped | 2026-09-04 |
| GH300-PRV-03 | Privacy and safeguards | Enable suggestions matching public code filtering | admin | Public code policy | `docs/labs/09-privacy-safeguards.md` | Learner distinguishes blocking from code referencing and inspects the policy location | Organization policy access | Dated screenshots | Policy-state check | mapped | 2026-09-04 |
| GH300-PRV-04 | Privacy and safeguards | Resolve issues with suggestions and content exclusions | live | Safeguard troubleshooting | `docs/labs/09-privacy-safeguards.md` | Learner checks entitlement, pattern, inheritance, propagation, reload, references, and the IDE agent-mode exception | Repository admin and VS Code | Troubleshooting decision tree | Fault-injection checklist | mapped | 2026-09-04 |

## Release criteria

Structural validation requires all 41 canonical IDs, exact domains and
statements, required fields, current review dates, and existing artifacts for
implemented rows. Run `uv run python scripts/validate_coverage.py --release`
for the release gate, which additionally requires every row to be `verified`.
A second reviewer must compare the canonical snapshot with the official guide,
and both workshop smoke tests must pass before release.