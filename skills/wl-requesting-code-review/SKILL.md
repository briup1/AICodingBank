---
name: wl-requesting-code-review
description: Perform or request an evidence-based review of completed code against requirements, architecture, risk, and test results before delivery. Use after a task, major feature, or complete implementation; it has no dependency on other workflow skills.
---

# WL Requesting Code Review

Produce a review verdict grounded in the actual diff, requirements, and fresh verification evidence.

Read `references/reviewer-template.md` when dispatching a reviewer.

## Prepare review context

Collect:

- requirements, approved design, and implementation plan;
- base and head revisions, or the complete working-tree diff;
- changed-file list and affected modules or contracts;
- test, lint, type-check, build, migration, security, performance, and E2E commands with observed results;
- known deviations, assumptions, and unresolved risks.

If evidence is missing, run the safe local checks or mark the gap explicitly. Never present unexecuted commands as proof.

## Review dimensions

1. Requirement and acceptance-criteria coverage.
2. Architectural consistency, domain boundaries, and reuse of existing extension points.
3. Correctness, edge cases, failure handling, concurrency, and idempotency.
4. Data migration and compatibility of APIs, events, configuration, and persistence.
5. Security, privacy, performance, capacity, observability, rollout, and rollback.
6. Test quality: bug reproduction, unit, integration, regression, and final-scenario E2E.
7. Scope control, documentation, and unintended changes.

## Severity and gate

- **Blocker:** data loss, security exposure, broken core behavior, invalid migration, or release-stopping defect.
- **Major:** material requirement gap, architecture or compatibility defect, important untested path, or likely operational failure.
- **Minor:** bounded maintainability, clarity, documentation, or low-risk improvement.

Delivery is blocked by unresolved Blocker or Major findings. Every finding must include file and line where possible, impact, evidence, and a practical correction. Re-review material fixes.

## Output

```text
Verdict: PASS | PASS WITH MINOR FINDINGS | CHANGES REQUIRED

Strengths
Blockers
Major findings
Minor findings
Test and E2E evidence
Residual risks and limitations
```

Do not approve code you did not inspect. Do not inflate stylistic preferences into release blockers.
