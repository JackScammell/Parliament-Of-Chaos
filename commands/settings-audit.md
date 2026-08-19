---
description: Unified audit of settings.json, permissions, scope-diff, secret leakage, and feature flags
effort: medium
argument-hint: "[--scope user|project|local|all] [--fix] [--focus permissions|secrets|flags|hooks|diff]"
---

# Settings Audit

Unified settings-hygiene command. Merges the four original proposals from the toolset-gaps debate (`/settings-diff`, `/permission-audit`, `/secrets-rotate`, `/feature-flag-list`) into one report to avoid command-count bloat.

## Usage

```
/settings-audit [--scope user|project|local|all] [--fix] [--focus permissions|secrets|flags|hooks|diff]
```

**Examples**:
```
/settings-audit                         # Full audit, all scopes
/settings-audit --scope project         # Only .claude/settings.json
/settings-audit --focus permissions     # Permission drift only
/settings-audit --focus secrets         # Secret leakage scan only
/settings-audit --fix                   # Propose remediations with diff preview
```

## Options

- `--scope <kind>`: Which settings files to include — `user` (`~/.claude/settings.json`), `project` (`.claude/settings.json`), `local` (`.claude/settings.local.json`), or `all` (default).
- `--fix`: Propose minimal remediations with a diff preview. Never applies without confirmation.
- `--focus <kind>`: Limit to a single pillar.

## Pillars

### 1. Permissions

- Compare project vs local permission grants — flag permissions only present in `local` that should be promoted to `project`.
- Flag overly broad wildcards (`Bash(*)`, `WebFetch(*)`) in any scope.
- Flag denied permissions that never trigger (stale from past workflows).

### 2. Secrets

- Scan all settings files for regex matches against common secret patterns (API keys, tokens, webhook URLs with embedded credentials).
- Cross-reference `.env` and `.env.*` files referenced from settings — warn if they are not gitignored.
- Detect webhook URLs in `notify_teams.sh` config that should live in environment variables instead of settings.

### 3. Feature flags

- Enumerate feature flags from `${CLAUDE_PLUGIN_DATA}/feature-flags.json` if present.
- List every flag, its value, its last-modified timestamp, and whether any code references it.
- Flag "dead" flags — defined but not read anywhere in the codebase.

### 4. Hooks

- Verify every hook script referenced by settings actually exists under `src/hooks/`.
- Verify scripts are executable and use the expected shebang.
- Warn if any hook script has world-writable permissions.
- Addresses the `feedback_hooks_location.md` footgun from user memory.

### 5. Scope diff

- Show what differs between `user`, `project`, and `local` scopes.
- Identify settings that contradict each other across scopes (e.g. `user` enables a hook that `project` disables).

## Process

1. **Locate settings** — `~/.claude/settings.json`, `<project>/.claude/settings.json`, `<project>/.claude/settings.local.json`.
2. **Parse and validate JSON** — surface syntax errors prominently.
3. **Run each selected pillar** — collect findings with severity.
4. **Delegate to `security-knight`** for the secrets pillar verdict.
5. **Delegate to `grumpy-security-nag`** for critique.
6. **Report**.

## Output

```
# Settings Audit

**Scopes checked**: user, project, local
**Findings**: 2 Critical, 4 High, 9 Medium

## Critical (2)
| Scope | Issue | Remediation |
|-------|-------|-------------|
| local | Bash(*) wildcard grants unrestricted shell | Replace with specific allowed commands |
| project | Plaintext GitHub token in hook config | Move to TEAMS_WEBHOOK_URL env var |

## High (4)
| Scope | Pillar | Issue |
|-------|--------|-------|
| project | hooks | Hook script handle_post_compact.sh referenced but file deleted in v1.9.0 |
| project | hooks | log_event.sh is not executable (mode 644) |
| local | permissions | Bq(*) permission granted but never used in last 30 days |
| user | permissions | WebFetch(*) overly broad — narrow to specific hosts |

## Medium (9)
[collapsed — use --severity medium to expand]

## Scope diff
project grants permission `Bash(npm test)`; local overrides with `Bash(bun test)`. Consider consolidating.

## Security verdict
REJECT — 2 Critical issues block sign-off.

## Next steps
- /settings-audit --fix (preview remediations)
- /summon-specialist security-knight for secret rotation
```

## Fix mode

With `--fix`:
- Generates a unified diff showing proposed edits to each settings file.
- Never writes until the user confirms.
- Refuses to auto-fix secret leakage — that requires explicit rotation via `security-knight`.

## Notes

- Read-only by default.
- Secrets scan is regex-based and heuristic. False positives on random-looking strings are expected; real secrets are triaged by `security-knight`.
- The hooks pillar closes the gap identified by `feedback_hooks_location.md` — hook scripts must live under `src/hooks/` to survive plugin cache.
- Coordinate with `/env-doctor` — this command audits *settings files*, `/env-doctor` audits *runtime environment*.
