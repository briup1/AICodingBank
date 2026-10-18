# Worker Prompt Contracts

Use these contracts as concise delegation templates. Supply exact repository paths, requirements, commands, and write scope.

## Implementer

```text
Implement only task <id> from <plan>.
Write scope: <paths>.
Dependencies already complete: <evidence>.
First create or run the specified failing test and confirm RED for the intended reason.
Then implement the minimum change, confirm GREEN, refactor safely, and rerun focused tests.
Follow repository instructions and existing architecture. Do not broaden scope or overwrite unrelated work.
Return: changed files, commands and observed results, assumptions, edge cases, and remaining risks.
```

## Specification reviewer

```text
Review task <id> implementation against the exact plan and requirements.
Inspect the diff and tests; do not trust the implementer's summary.
Find missing behavior, excess scope, contract incompatibility, and acceptance-criteria gaps.
Return Blocker, Major, and Minor findings with file:line evidence, or PASS.
Do not perform code-quality review until specification compliance is established.
```

## Quality reviewer

```text
Review the specification-compliant implementation for correctness, architecture consistency, extension-point use, errors, security, privacy, performance, operability, maintainability, and test quality.
Inspect actual code and test evidence.
Return Blocker, Major, and Minor findings with file:line evidence and a clear verdict.
```
