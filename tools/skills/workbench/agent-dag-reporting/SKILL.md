---
name: agent-dag-reporting
description: Report multi-step task plans and meaningful state changes to Personal Workbench through independent MCP tools. Use for tasks with at least two trackable steps or an existing TodoList.
---

# Agent DAG Reporting

Use the Personal Workbench MCP tools; never embed DAG protocol data in normal replies.

1. Call `report_plan` once when work starts. Prefer an existing TodoList; otherwise create a concise observation plan.
2. Call `report_state` only for meaningful node transitions or coarse progress.
3. Call `report_artifact` for user-relevant files, diffs, tests, shell summaries, summaries, or URLs.
4. Call `report_checkpoint` for blockers, reviews, questions, or approval needs. The Workbench is read-only; continue the conversation in the original terminal.
5. On material replanning, call `report_plan` with a higher revision and the complete replacement snapshot.
6. Never output `###AGENT_DAG###`, DAG JSON, or tool arguments in assistant text.
7. Reporting failure must not block the primary task and should not trigger repeated retries.

Use stable lowercase kebab-case node IDs. Mark a node DONE only after its completion condition is verified. Do not report heartbeats, every command, speculative artifacts, credentials, secrets, or unnecessary sensitive paths.
