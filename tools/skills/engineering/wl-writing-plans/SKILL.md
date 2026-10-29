---
name: wl-writing-plans
description: Create a detailed test-first implementation plan only when the user or project explicitly requests this planning format. Not the default execution entry; ordinary approved-design work uses wl-ticket-run. Do not use with unresolved requirements or architecture.
---

# WL Writing Plans

Create an executable implementation plan. Do not implement it.

## 使用边界

这是非默认的详细实施计划路线，仅用户或项目规则显式选择时使用；普通开发沿 [wl-auto-delivery](../../workbench/wl-auto-delivery/SKILL.md) 进入 `wl-ticket-run`。已有方案和任务清单原位复用，不叠加第二套业务预期、方案或任务清单；只补本次要求的测试优先施工细节。未决业务/架构问题回实际来源阶段，不因发现缺口自动开启另一套设计流程。

## Preconditions

- Locate repository instructions and the approved design or stable requirements.
- If material product or architecture decisions remain unresolved, return to the owning requirement/design stage. Use `wl-brainstorming` only if that route was explicitly selected.
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

计划交付后按本次范围停止，不自动串接另一条执行路线。需要继续实施且授权已覆盖时，默认交给 [wl-ticket-run](../wl-ticket-run/SKILL.md)，先核对该入口所需的需求/用例和本版方案决策，再复用本计划按耦合分组，不重写同一清单；缺前置只反馈实际缺口，不把实施计划冒充方案批准或自动补造整套文档。仅用户或项目规则显式选择逐任务隔离执行时使用 `wl-subagent-driven-development`。不得引用或依赖 Superpowers 命名空间。
