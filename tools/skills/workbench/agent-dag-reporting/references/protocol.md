# agent-dag/v1 Reporting Reference

## Common Envelope

Each event is one compact JSON line prefixed with `###AGENT_DAG###` and contains:

- `protocol`: always `agent-dag/v1`
- `phase`: `PLAN`, `STATE`, `ARTIFACT`, `CHECKPOINT`, or `PLAN_UPDATE`
- `task_id`: stable task identifier, preferably branch/change/feature oriented
- `timestamp`: ISO 8601 date-time, preferably UTC
- `session_id`: current Agent session ID when available
- `worktree`: current absolute worktree path when available

## PLAN

Required fields: `revision`, `source`, and complete `dag`.

```text
###AGENT_DAG###{"protocol":"agent-dag/v1","phase":"PLAN","task_id":"feat-rate-limiter","session_id":"session-001","worktree":"/home/you/project","timestamp":"2026-08-19T02:00:00Z","revision":1,"source":"AGENT_TODO","dag":{"structure":"SEQUENTIAL","nodes":[{"id":"analyze","label":"Analyze existing implementation","status":"RUNNING","dependencies":[]},{"id":"implement","label":"Implement rate limiter","status":"PENDING","dependencies":[]},{"id":"verify","label":"Run verification","status":"PENDING","dependencies":[]}]}}
```

A node requires `id`, `label`, and `dependencies`. Optional node fields include `description`, `type`, `estimated_duration`, `outputs`, `review_policy`, `success_criteria`, `status`, and `progress`.

Node `type`: `CODE`, `TEST`, `RESEARCH`, `SHELL`, `REVIEW`, or `DECISION`.

## STATE

Emit when a node starts, finishes, becomes blocked/reviewable/skipped, or has a meaningful coarse progress update.

```text
###AGENT_DAG###{"protocol":"agent-dag/v1","phase":"STATE","task_id":"feat-rate-limiter","session_id":"session-001","worktree":"/home/you/project","timestamp":"2026-08-19T02:01:00Z","node_id":"implement","status":"RUNNING","progress":0.5,"log":"Implementing the core policy"}
```

Required: `node_id`, `status`. Optional: `progress` from 0 to 1 and concise `log`.

## ARTIFACT

```text
###AGENT_DAG###{"protocol":"agent-dag/v1","phase":"ARTIFACT","task_id":"feat-rate-limiter","session_id":"session-001","worktree":"/home/you/project","timestamp":"2026-08-19T02:05:00Z","node_id":"implement","artifacts":[{"type":"FILE","path":"src/rate-limiter.ts","change_type":"MODIFIED","diff_summary":"Implemented request throttling"}]}
```

Artifact shapes:

- `FILE`: `path`, `change_type` (`CREATED`, `MODIFIED`, `DELETED`); optional `diff_summary`, `content_hash`
- `TEST_RESULT`: `command`, `exit_code`; optional `summary`
- `SHELL_OUTPUT`: `command`; optional `exit_code`, `summary`
- `DIFF`: `path`; optional `summary`
- `SUMMARY`: `content`
- `URL`: `url`; optional `title`

## CHECKPOINT

Use only for user-relevant interruption or review. Also report the corresponding node status when appropriate.

```text
###AGENT_DAG###{"protocol":"agent-dag/v1","phase":"CHECKPOINT","task_id":"feat-rate-limiter","session_id":"session-001","worktree":"/home/you/project","timestamp":"2026-08-19T02:06:00Z","node_id":"implement","subtype":"BLOCKED","severity":"HIGH","message":"Redis configuration is unavailable","context":"Need a configured REDIS_URL before integration verification"}
```

Required: `node_id`, `subtype`, `message`. Subtypes: `BLOCKED`, `REVIEW`, `QUESTION`, `APPROVAL`. Severity: `LOW`, `MEDIUM`, `HIGH`. Optional `context` and `options` (`id`, `label`, optional `description`).

## PLAN_UPDATE

This is a complete snapshot replacement, never a patch. Increment `revision`; include the full DAG and an explicit `status` on every node. New node IDs may differ from the prior revision.

```text
###AGENT_DAG###{"protocol":"agent-dag/v1","phase":"PLAN_UPDATE","task_id":"feat-rate-limiter","session_id":"session-001","worktree":"/home/you/project","timestamp":"2026-08-19T02:15:00Z","revision":2,"source":"AGENT_TODO","reason":"Split verification into unit and integration checks","dag":{"structure":"DEPENDENCY","nodes":[{"id":"implement","label":"Complete implementation","status":"DONE","dependencies":[]},{"id":"unit-tests","label":"Run unit tests","status":"RUNNING","dependencies":["implement"]},{"id":"integration-tests","label":"Run integration tests","status":"PENDING","dependencies":["implement"]}]}}
```

## Success Criteria Shape

When useful, a node may include:

```json
{"success_criteria":{"description":"Verification passes","checks":[{"type":"TEST_PASSES","command":"uv run pytest"}]}}
```

Check types:

- `FILE_EXISTS` requires `path`
- `TEST_PASSES` requires `command`
- `OUTPUT_CONTAINS` and `OUTPUT_NOT_CONTAINS` require `path` and `pattern`
- `COMMAND_SUCCEEDS` requires `command`

## Noise Control

Report these transitions:

```text
plan established       → PLAN
meaningful work begins → STATE RUNNING
observable output      → ARTIFACT
completion verified    → STATE DONE
blocked/review/input   → STATE + CHECKPOINT
plan materially changes → PLAN_UPDATE
```

Do not emit heartbeats, token-level progress, every shell command, repeated unchanged states, or speculative artifacts.
