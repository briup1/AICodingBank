---
name: wl-brainstorming
description: Turn an unclear software idea into an approved, testable design only when the user or project explicitly selects this standalone design route. Not the default for new features; use wl-auto-delivery for ordinary lifecycle requests. Do not execute approved designs.
---

# WL Brainstorming

Produce an approved design, not implementation.

## 使用边界

这是非默认的独立设计路线，仅用户或项目规则显式选择时进入；普通新功能请求按 [wl-auto-delivery](../../workbench/wl-auto-delivery/SKILL.md) 路由。已存在需求/方案时复用真实批准及范围，不叠加 `wl-req-confirm` / `wl-design-doc` 重做同一阶段。显式选择后沿下文工作，不因兼容其他路线省略本路线的批准与验证。

## Workflow

1. Read repository instructions, relevant files, documentation, tests, and recent changes before proposing a design.
2. Perform a regression-impact scan covering existing modules, data models, interface contracts, security, performance, operations, and backward compatibility.
3. Clarify purpose, users, constraints, exclusions, and measurable success criteria. Ask one focused question at a time only when the answer cannot be discovered safely.
4. Present two or three viable approaches with trade-offs. Recommend the approach that best fits the existing architecture and favors extension points over isolated new logic.
5. Present the proposed architecture, components, data flow, failure handling, compatibility, rollout or rollback needs, and test strategy. Scale detail to complexity and use ASCII flowcharts for flows.
6. Obtain explicit user approval before implementation begins.
7. Save the approved design to `docs/wl-ai-skills/specs/YYYY-MM-DD-<topic>-design.md` unless the project specifies another location.
8. Review the document for ambiguity, contradictions, placeholders, unjustified scope, and unverifiable acceptance criteria.
9. Hand off the approved design to `wl-writing-plans` only when the user or project explicitly selects that detailed planning format. Otherwise deliver this stage and stop; choosing this design route does not automatically select another planning or execution route.

## Design gate

Do not write implementation code, scaffold files, or mutate product behavior before the design is approved. Small or urgent changes may use a short design, but still require explicit scope, impact, success criteria, and approval.

## Required design output

- Problem, users, goals, and non-goals.
- Existing architectural boundaries and extension points.
- Recommended approach and rejected alternatives.
- Affected modules, data, contracts, and non-functional characteristics.
- Failure modes, security and privacy considerations, migration and compatibility.
- Unit, integration, regression, and end-to-end test strategy.
- Quantifiable acceptance criteria and unresolved decisions.
