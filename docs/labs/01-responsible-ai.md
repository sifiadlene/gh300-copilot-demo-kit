---
title: Responsible Use of GitHub Copilot
description: Scenario-based GH-300 lab for generative AI risks, harms, mitigations, validation, and responsible operation
ms.date: 2026-09-04
ms.topic: tutorial
estimated_reading_time: 15
---

## Learning outcomes

By the end of this lab, you can:

* Describe common risks and limitations of generative AI development tools
* Apply Microsoft's six responsible AI principles to development scenarios
* Identify affected stakeholders, potential harms, and concrete mitigations
* Explain why generated output requires human validation
* Operate Copilot with appropriate data, permissions, review, and escalation

## Prerequisites

No Copilot entitlement is required. Use the scenario cards with a group, in
pairs, or as an individual exercise. For the optional live validation, open
`src/cart.js` in VS Code with Copilot enabled.

## Part 1: Understand the principles

Use these principles as lenses rather than as a checklist that guarantees a
system is responsible.

| Principle | Question to ask |
|---|---|
| Fairness | Could output quality or impact differ across groups, languages, or contexts? |
| Reliability and safety | What happens when the output is incorrect, incomplete, or used outside its intended scope? |
| Privacy and security | Does the prompt or output expose sensitive data, secrets, personal data, or vulnerable code? |
| Inclusiveness | Can people with different abilities, languages, tools, and experience levels use the result? |
| Transparency | Can users tell that AI contributed, what context was used, and where uncertainty remains? |
| Accountability | Which person reviews, approves, monitors, and owns the consequences of the result? |

## Part 2: Assess the scenarios

For each scenario, complete the rubric before opening the answer key.

| Field | Required response |
|---|---|
| Risk | The limitation or failure mode present |
| Stakeholder | The person or group that could be affected |
| Harm | A concrete negative outcome, not only a technical defect |
| Severity | Low, medium, or high, with one-sentence justification |
| Principles | One or more responsible AI principles involved |
| Mitigation | A preventive or detective control |
| Approval | The person who must approve use of the output |
| Evidence | A test, review, source, measurement, or audit record that validates the mitigation |

### Scenario A: Plausible but incorrect API

Copilot proposes a security-library method that does not exist in the installed
version. The code looks idiomatic, so the developer accepts it without checking
the library documentation or running the integration test.

### Scenario B: Uneven recommendation quality

A team asks Copilot to generate interview exercises. The examples are clear for
popular languages but contain outdated patterns and confusing terminology for
less represented languages. The same scoring threshold is used for everyone.

### Scenario C: Sensitive context

A developer pastes an access token, a customer's payment record, and an
unredacted production trace into chat to troubleshoot a failure.

### Scenario D: Insecure generated change

Copilot suggests constructing the inventory query with string concatenation.
The happy-path test passes, but an attacker-controlled SKU can change the SQL
statement.

### Scenario E: Public-code match

An accepted suggestion is annotated with references to matching public code.
The developer assumes that a Copilot suggestion automatically grants permission
to use the code and removes the reference without review.

### Scenario F: Agent overreach

An agent receives broad write tools and a vague request to clean up production.
It proposes deleting resources that appear unused. There is no dry run, owner
confirmation, rollback plan, or independent usage evidence.

## Part 3: Review the answer key

Several answers can be valid. The minimum acceptable analysis includes these
points.

| Scenario | Primary risks | Potential harms | Minimum mitigations and evidence |
|---|---|---|---|
| A | Hallucination, knowledge/version limits, overreliance | Broken build or disabled security control | Check installed version and official documentation; compile and run integration/security tests; require code review |
| B | Bias, uneven training representation, inappropriate automation | Unfair candidate assessment and exclusion | Use representative reviewers and samples; measure exercise quality by language; provide accommodations and an appeal path; keep a human decision maker |
| C | Privacy leakage and credential exposure | Account compromise, fraud, contractual or regulatory breach | Never submit secrets; redact personal and payment data; revoke exposed credentials; use approved data-handling policy and audit evidence |
| D | Insecure code and incomplete tests | Data disclosure or corruption through SQL injection | Use parameterized SQL; add malicious-input tests and security review; run static analysis where appropriate |
| E | Incorrect ownership or licensing assumption | Attribution failure, incompatible license use, or IP dispute | Inspect references and available license information; follow organizational legal policy; replace or attribute when required; retain the review decision |
| F | Excessive agency, ambiguous intent, and irreversible action | Production outage, data loss, or financial loss | Apply least privilege; start read-only; require a plan, dry run, owner approval, backup, rollback, and independently verified usage data |

## Part 4: Validate a generated change

Open `src/cart.js` and ask Copilot:

> Fix checkout security and return the updated function.

Do not accept the first answer immediately. Use this validation loop:

1. Confirm the proposed change addresses full card-number logging without
   adding another sensitive value.
2. Check whether it also notices input validation, predictable order IDs, money
   representation, and discount boundaries. Missing issues demonstrate that a
   plausible answer can still be incomplete.
3. Ask for assumptions and unsupported claims explicitly.
4. Review the diff against repository instructions.
5. Generate and inspect tests for success, boundaries, and failures.
6. Run the tests and relevant security checks.
7. Accept only the reviewed portion. Record unresolved risk for follow-up.

The person accepting the change remains accountable for its correctness,
security, suitability, and compliance with applicable terms and policies.

## Part 5: Responsible operation checklist

Before using Copilot output:

* Confirm that the task is an appropriate use of Copilot
* Remove secrets, credentials, personal data, and unnecessary sensitive context
* Supply accurate, relevant context and state important constraints
* Give agents only the tools and permissions required for the task
* Review references, assumptions, uncertainty, and public-code annotations
* Validate with authoritative sources, tests, linters, security checks, or data
* Require human approval for consequential or irreversible actions
* Preserve logs or review evidence required by organizational policy
* Escalate legal, security, privacy, safety, and sensitive-domain concerns
* Monitor the result after release and retain a rollback path

## Knowledge check

1. Why can syntactically valid generated code still be unsafe?
2. Which principle is most relevant when output quality differs by language?
3. What should happen immediately after a credential is pasted into chat?
4. Does a code reference prove that the suggested use is legally acceptable?
5. Which controls should precede an agent's irreversible production action?

Expected answers:

1. Syntax does not prove semantic correctness, security, suitability, or
   alignment with the intended architecture.
2. Fairness is primary, with inclusiveness and accountability also relevant.
3. Revoke or rotate the credential, follow incident policy, and remove or
   restrict exposed data where supported.
4. No. Review the reference, available license information, applicable terms,
   and organizational policy.
5. Least privilege, read-only discovery, independent evidence, dry run, named
   human approval, backup, rollback, and post-action verification.

## Official references

* [GH-300 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-300)
* [Application card for GitHub Copilot inline suggestions](https://docs.github.com/en/copilot/responsible-use/copilot-code-completion)
* [GitHub Copilot code referencing](https://docs.github.com/en/copilot/concepts/completions/code-referencing)
* [Microsoft responsible AI principles](https://www.microsoft.com/en-us/ai/principles-and-approach/)

Product behavior and terms can change. Revalidate these references before a
workshop rather than treating this lab as legal or compliance advice.