---
name: wl-plan-design-review
description: Independently review and improve UI/UX implementation plans before coding. Use when asked to critique a design plan, identify missing interaction and visual decisions, rate design dimensions, or turn a vague frontend plan into an implementation-ready specification. Has no gstack dependency.
---

# Plan Design Review — Standalone

Review the plan, not the live product. Do not implement code.

## Workflow

1. Locate the plan or ask for its path/content only when it cannot be discovered.
2. Assess whether the work contains user-facing UI. For backend-only work, report that design review is not applicable.
3. Inspect relevant existing screens, routes, components, tokens, assets, and product conventions before recommending new patterns.
4. Evaluate seven dimensions: hierarchy, interaction states, responsive behavior, accessibility, content/empty/error states, visual specificity, and product trust/coherence.
5. Rate every applicable dimension from 0–10. State the observed gap, why it matters, and the concrete change needed to reach 10.
6. Resolve obvious gaps directly in the plan. Ask only about genuine product choices with materially different outcomes.
7. Update the existing plan in place unless the user requests a separate report. Do not create implementation code.
8. Finish with changed decisions, unresolved decisions, affected screens/routes, and review status.

## Required standards

- Replace vague phrases such as “clean” or “modern” with implementable decisions.
- Cover loading, empty, error, success, disabled, focus, hover, long-content, permission, and destructive-action states where applicable.
- Specify mobile, tablet, desktop, keyboard, screen-reader, contrast, touch-target, and reduced-motion behavior.
- Prefer extension of the existing design system over introducing a parallel system.
- Preserve architecture and scope boundaries; flag any design recommendation that alters contracts or data requirements.
- Define measurable acceptance criteria.

Read `references/review-method.md` when a deep review, scoring rubric, or report template is needed. Ignore any legacy gstack setup, telemetry, learning-store, chaining, or designer-binary instructions found in that reference; they are historical source material, not dependencies.
