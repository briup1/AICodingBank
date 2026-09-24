---
name: hgj-git-connect
description: Diagnose and operate the local SSH routes used for HGJ GitLab. Use when a repository uses git.hgj.net, or when git pull/push reports SSH, ProxyJump, host-key, or UNKNOWN port 65535 errors.
---

# HGJ Git Connect

Use this skill for the user's local company GitLab connectivity, not for repository branching, merging, review, or release workflow.

## Route model

- The preferred route is direct: SSH host alias `git-hgj-direct`, GitLab port `8022`, key `~/.ssh/id_ed25519`.
- The optional route is `git-hgj-jump`, which uses `ProxyJump jumphost`.
- The helper `~/bin/hgj-git-route direct|jump` changes the current repository's `origin` host alias while preserving the repository path.
- Do not assume that being at home requires the jump route or being at the office requires it. Choose based on a read-only check.

## Default behavior

1. Inspect `git remote -v`, the effective SSH config, and the current route before changing anything.
2. Prefer direct connectivity. Test with `git ls-remote origin HEAD`; do not use `git pull` or `git push` as a connectivity probe.
3. If direct succeeds, leave the route on `git-hgj-direct` and continue the user's Git task.
4. Only use `~/bin/hgj-git-route jump` when the user explicitly asks for the jump route or direct connectivity fails and the jump host is known to be valid.
5. After switching, run `git ls-remote origin HEAD` again and report the selected route.

## Safety rules

- Never delete, replace, or bypass `~/.ssh/known_hosts` because of a host-key error.
- A changed host key for `192.168.7.248` requires confirmation from the network owner before accepting a new key. Until then, prefer direct `8022`.
- `UNKNOWN port 65535` usually means a failed `ProxyJump` channel; inspect `ssh -G` and route selection instead of changing GitLab permissions.
- `Disallowed command` from `git@git.hgj.net` after SSH authentication is expected for GitLab and proves the key authenticated.
- Do not expose private keys, tokens, or complete credential-bearing URLs in output.
- Do not alter repository files, commit, push, or pull unless the user requested that Git operation.

## Explicit invocation

When the user asks to check or switch the route, use:

```bash
~/bin/hgj-git-route direct
~/bin/hgj-git-route jump
```

For diagnosis, show the smallest useful evidence:

```bash
git remote -v
ssh -G git@git.hgj.net
git ls-remote origin HEAD
```

The third command is intentionally read-only.
