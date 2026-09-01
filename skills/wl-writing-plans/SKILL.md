---
name: wl-writing-plans
description: Convert an approved specification or stable requirements into a detailed, test-first implementation plan before code changes. Use for multi-step engineering work; do not use when requirements or architecture are still undecided.
---

# WL Writing Plans

Create an executable implementation plan. Do not implement it.

## Preconditions

- Locate repository instructions and the approved design or stable requirements.
- If material product or architecture decisions remain unresolved, return to `wl-brainstorming`.
- Establish the current architecture, analogous implementations, testing conventions, and delivery constraints.

## Impact and scope gate

Before task decomposition, document expected impact on:

- modules and ownership boundaries;
- data models and migrations;
- API, event, configuration, and persistence contracts;
- backward compatibility;
- performance, security, privacy, and operations.

List every file expected to be created, modified, or deleted. If implementation is expected to modify more than ten files, stop and split it into independently valuable, testable sub-plans before proceeding.

## Plan construction

1. Map responsibilities and extension points; prefer extending established seams, hooks, strategies, and patterns.
2. Break work into ordered tasks with explicit dependencies and independently verifiable outcomes.
3. For each behavior change, specify:
   - the exact test file and failing test to add first;
   - the command proving the RED state and expected failure;
   - the exact implementation location and minimal change;
   - the command proving GREEN;
   - the refactoring and regression checks.
4. For bugs, the first implementation task must reproduce the defect with an automated failing test.
5. Include contract, migration, rollback, observability, security, and performance tasks when applicable.
6. End with full regression, static analysis, build, and an end-to-end test of the user's final scenario.
7. Define concrete evidence required before any task or plan can be marked complete.

## Plan format

Save to `docs/wl-ai-skills/plans/YYYY-MM-DD-<feature-name>.md` unless the project overrides the location. Include:

```text
Goal and non-goals
        ↓
Regression-impact assessment
        ↓
Architecture and file map
        ↓
Dependency-ordered tasks (RED → GREEN → REFACTOR)
        ↓
Integration and E2E verification
        ↓
Rollout, rollback, and completion evidence
```

Each task must identify exact paths or symbols, commands, expected results, edge cases, and completion criteria. Avoid speculative features and unnecessary abstractions.

## Handoff

After reviewing the plan for completeness and feasibility, offer execution through `wl-subagent-driven-development`. Do not reference or require any Superpowers skill or namespace.
