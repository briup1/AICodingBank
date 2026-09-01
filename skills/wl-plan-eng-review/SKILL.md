---
name: wl-plan-eng-review
description: Independently perform a rigorous engineering review of an implementation plan before coding. Use to assess architecture, impact radius, interfaces, data changes, security, performance, migration, observability, rollback, testing, and delivery readiness. Has no gstack dependency.
---

# Plan Engineering Review — Standalone

Review and improve the implementation plan. Do not implement the feature.

## Workflow

1. Locate the plan and repository instructions.
2. Establish the base branch and inspect existing architecture, ownership boundaries, contracts, tests, and analogous implementations.
3. Trace the proposed change through entry points, domain logic, persistence, integrations, and user-visible effects.
4. Review: architecture consistency, extension points, data model/migrations, API compatibility, concurrency/idempotency, failure handling, security/privacy, performance/capacity, observability, rollout/rollback, and test strategy.
5. Identify assumptions and classify findings by critical/high/medium.
6. Fix clear omissions directly in the plan. Ask only about decisions that cannot safely be inferred.
7. Ensure every implementation step has a verifiable completion condition and owner-visible artifact.
8. End with affected modules/contracts, edge cases, critical paths, unresolved decisions, and readiness status.

## Required standards

- Prefer extending existing seams, strategies, hooks, and abstractions over creating isolated logic.
- Explicitly assess regression impact on modules, models, interfaces, performance, and security.
- Require unit, integration, regression, and end-to-end coverage for the final user scenario.
- Include migration compatibility, feature flags, rollback, monitoring, alerts, and failure recovery where applicable.
- Flag plans touching more than ten files and recommend decomposition before implementation.
- Define measurable success criteria and evidence required for completion.

Read `references/review-method.md` for the detailed review rubric and templates. Ignore any legacy gstack setup, telemetry, learning-store, review-log, or skill-chaining instructions found in that reference.
