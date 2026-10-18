---
name: wl-subagent-driven-development
description: Execute an approved implementation plan task by task with isolated workers, test-first development, specification review, quality review, and completion evidence. Use only when subagent delegation is available and authorized; otherwise execute the same gates locally.
---

# WL Subagent-Driven Development

Execute a reviewed plan while keeping the controller responsible for context, sequencing, integration, and final verification.

Read `references/worker-prompts.md` when delegating implementer or reviewer work.

## Preconditions and impact check

1. Read repository instructions and the complete plan once.
2. Reconfirm affected modules, contracts, data, security, performance, and operations against the current working tree.
3. If the plan is stale, architecturally inconsistent, changes more than ten files without decomposition, or lacks measurable acceptance and E2E criteria, stop and repair the plan before implementation.
4. Inspect Git status. Do not overwrite unrelated work. Use the existing workspace unless isolation is materially needed; if using a worktree, verify repository conventions and choose a safe ignored location.
5. Create or mirror the task DAG, including dependencies and verification gates.

## Task loop

For each unblocked task:

```text
Provide bounded task context
        ↓
Implementer: RED → verify failure → GREEN → REFACTOR
        ↓
Specification review
        ↓
Code-quality and risk review
        ↓
Fix findings and re-run affected tests
        ↓
Integrate only after both reviews pass
```

- Delegate only bounded, self-contained work with explicit write scope. Parallelize only tasks with disjoint state and write sets.
- Do not delegate an immediate blocker when the controller's next action depends on its result.
- For a bug, require a reproducing failing test before the fix.
- The implementer must run the specified focused tests and report changed files, commands, outputs, assumptions, and remaining risks.
- The specification reviewer checks requirements and scope before style or polish.
- The quality reviewer checks architecture consistency, extension-point use, correctness, contracts, security, performance, maintainability, and test quality.
- Block integration on unresolved Blocker or Major findings. Re-review material fixes.

## Embedded TDD rule

No production behavior change precedes its failing automated test unless testing is technically impossible. If impossible, record why and add the nearest executable characterization, integration, or E2E check.

```text
RED: new test fails for the intended reason
GREEN: minimum implementation makes it pass
REFACTOR: improve structure without changing behavior
VERIFY: focused test remains green
```

## Completion verification

Before claiming completion, run fresh evidence appropriate to the repository:

- focused tests for each task;
- full relevant regression suite;
- lint, type-check, build, or static analysis;
- migration or compatibility checks where applicable;
- security and performance checks identified by the plan;
- an end-to-end test of the final user scenario;
- `git diff` and `git status` review for unintended changes.

Never infer success from earlier output or worker claims. If a required check cannot run, state the exact limitation and provide a reproducible user test path.

## Final review and delivery

Invoke `wl-requesting-code-review` against the complete change and approved plan. Resolve all Blocker and Major findings, then repeat affected and final verification. Report:

- implemented scope and changed files;
- regression-impact result;
- test and E2E evidence;
- unresolved Minor findings or limitations;
- working-tree or branch state;
- safe delivery options such as commit, PR, merge, or cleanup without performing external mutations that lack authorization.
