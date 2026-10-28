---
name: wl-subagent-driven-development
description: Execute an approved plan with per-task isolated workers and specification/quality reviews only when the user or project explicitly selects this route. Not the default for ordinary development or parallel work; wl-ticket-run owns normal work-package execution. Delegation must be authorized.
---

# WL Subagent-Driven Development

Execute a reviewed plan while keeping the controller responsible for context, sequencing, integration, and final verification.

## 使用边界

这是非默认的逐任务隔离执行路线，仅用户或项目规则显式选择这种执行粒度时启用；“开始开发”“并行处理”不代表选择。普通任务按 [wl-auto-delivery](../../workbench/wl-auto-delivery/SKILL.md) 交给 `wl-ticket-run`，不叠加两套任务循环或审查门禁。沿本路线时保留下文逐任务规格/质量审查，真实批准和已有任务不重建；委派统一按 [wl-herdrs](../../workbench/wl-herdrs/SKILL.md)，无可用获准通道时由负责人本地执行同等门禁，不冒充独立审查；任务明确要求独立结论时仍须记阻塞。

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
