---
name: wl-investigate
description: Independently investigate and fix software defects using evidence-first root-cause analysis. Use for bugs, regressions, test failures, production symptoms, unexplained behavior, or requests to diagnose before changing code. Requires a failing reproduction before the fix and verification afterward. Has no gstack dependency.
---

# Investigate — Standalone

## Iron law

Do not change production code before obtaining a reliable failing reproduction or explicit evidence explaining why reproduction is impossible.

## Workflow

1. Capture the symptom, expected behavior, environment, scope, and last-known-good state.
2. Read repository instructions and assess impact across modules, models, contracts, performance, and security.
3. Reproduce the defect with the smallest deterministic test, script, or end-to-end path.
4. Trace the causal chain from entry point through data/control flow to the first incorrect state.
5. Form one falsifiable hypothesis at a time. Record evidence for and against it.
6. After three failed hypotheses, stop and present the evidence, architectural concern, and next diagnostic choices.
7. Once root cause is confirmed, add a regression test that fails without the fix.
8. Apply the smallest root-cause fix; avoid unrelated refactoring.
9. Run targeted tests, the relevant full suite, and the original end-to-end reproduction.
10. Report symptom, root cause, changed files/lines, evidence, regression test, residual risks, and status.

## Guardrails

- Never claim “should fix”; prove the outcome.
- Treat logs as context-bearing evidence, not keyword matches.
- If the fix spans more than five files, reassess whether the repair is at the wrong layer; if it exceeds ten files, stop and decompose.
- Preserve interface compatibility unless the verified root cause requires a contract change.
- For unavailable external systems, provide an exact manual verification path and mark the result as partially verified.

Read `references/investigation-method.md` for detailed hypothesis, verification, and report templates. Ignore legacy gstack setup, telemetry, freeze, learning-store, or chaining instructions in that reference.
