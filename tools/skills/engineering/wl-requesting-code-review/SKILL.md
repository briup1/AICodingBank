---
name: wl-requesting-code-review
description: Perform or request an evidence-based review of completed code against requirements, architecture, risk, and test results before delivery. Use after a task, major feature, or complete implementation; it has no dependency on other workflow skills.
---

# WL Requesting Code Review

Produce a review verdict grounded in the actual diff, requirements, and fresh verification evidence.

Read `references/reviewer-template.md` when dispatching a reviewer.

## Modes

Default **full** mode retains all dimensions, severities and output below. This Skill remains independently callable and does not depend on a workflow artifact.

Explicit **focused-delivery** mode (used by wl-auto-delivery / wl-ticket-run) reviews only:

```text
this requirement + executable design/version
  → actual diff/version → direct callers/dependencies/contracts
  → design conformity + defects blocking this delivery or causing direct regression
```

- Freeze base/head or working-tree snapshot, requirement/design/test-case versions and changed files. New changes invalidate affected findings; do not approve a later version using an earlier diff.
- Check only the actual diff, directly affected contracts and the minimum necessary regression path. Do not expand to unrelated modules, historical debt, global refactoring, style cleanup or full-repository tests.
- 只报**设计偏离**和**具体交付阻断问题**：有 file:line、实际影响、因果链和证据，直接导致本需求失败/回归的安全、数据或兼容性缺陷属于后者。建议可省略；不做泛化改进审查，不主动收集重构/风格/可维护性建议。偶遇需求外问题仅作可选观察，不扩审、不修复、不作为门禁。
- Missing critical evidence yields **EVIDENCE INSUFFICIENT / 证据不足，不能判定交付** and the smallest missing check, not a fabricated PASS. Do not infer failure of unrelated modules or keep widening review to fill the gap.
- Output: reviewed versions/scope, verdict, 设计偏离/具体交付阻断问题（无则明确无）, actual evidence and uncovered items; suggestions/observations may be omitted. Stop once these two focused checks are resolved or explicitly blocked; re-review only affected fixes.
- This mode does not claim broad architecture/security/performance/E2E coverage. Review precedes target-environment business acceptance. Only a real different session can be called independent review; if delegated, use Herdr Pi thinking=high, never claim independence when unavailable.
- The full-mode reviewer template below must not silently broaden a focused dispatch: supply the focused scope and output contract explicitly instead. No private total-workflow files are required.

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
