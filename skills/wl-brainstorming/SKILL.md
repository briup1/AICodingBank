---
name: wl-brainstorming
description: Turn an unclear software idea or behavior change into an approved, testable design before implementation. Use for new features, components, workflows, or meaningful behavior changes; do not use for executing an already approved design.
---

# WL Brainstorming

Produce an approved design, not implementation.

## Workflow

1. Read repository instructions, relevant files, documentation, tests, and recent changes before proposing a design.
2. Perform a regression-impact scan covering existing modules, data models, interface contracts, security, performance, operations, and backward compatibility.
3. Clarify purpose, users, constraints, exclusions, and measurable success criteria. Ask one focused question at a time only when the answer cannot be discovered safely.
4. Present two or three viable approaches with trade-offs. Recommend the approach that best fits the existing architecture and favors extension points over isolated new logic.
5. Present the proposed architecture, components, data flow, failure handling, compatibility, rollout or rollback needs, and test strategy. Scale detail to complexity and use ASCII flowcharts for flows.
6. Obtain explicit user approval before implementation begins.
7. Save the approved design to `docs/wl-ai-skills/specs/YYYY-MM-DD-<topic>-design.md` unless the project specifies another location.
8. Review the document for ambiguity, contradictions, placeholders, unjustified scope, and unverifiable acceptance criteria.
9. When implementation planning is requested, hand off to `wl-writing-plans` with the approved design path.

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
