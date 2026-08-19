---
description: Validate runtime environment — plugin data dir, hook locations, tool availability, and fallback behaviour
effort: low
argument-hint: "[--fix-permissions] [--strict] [--check-orphans] [--prune]"
---

# Env Doctor

Runtime sanity check. Distinct from `/settings-audit` (which inspects configuration files): this command checks that the **live environment** the plugin runs in is correctly set up.

Closes the `feedback_hooks_location.md` footgun — if a hook script has drifted out of `src/hooks/`, Parliament silently loses that hook. This command makes the drift loud.

## Usage

```
/env-doctor [--fix-permissions] [--strict] [--check-orphans] [--prune]
```

**Examples**:
```
/env-doctor                        # Report environment health
/env-doctor --strict               # Exit non-zero on any warning (for CI)
/env-doctor --fix-permissions      # chmod any hook scripts missing executable bit (with diff preview)
/env-doctor --check-orphans        # Also list orphaned auto-installed plugin dependencies
/env-doctor --prune                # Run `claude plugin prune` after confirmation (Claude Code v2.1.121+)
```

## Options

- `--fix-permissions`: Apply minimal permission fixes (chmod +x on hook scripts). Shows a diff of intended changes before applying.
- `--strict`: Exit non-zero if any check fails. Intended for release gates.
- `--check-orphans`: Run `claude plugin list --orphaned` (Claude Code v2.1.121+) and surface auto-installed plugin dependencies that no longer have a dependent. Read-only.
- `--prune`: After `--check-orphans`, prompt to run `claude plugin prune`. Requires explicit confirmation; never invoked under `--strict`.

## Checks

### Plugin data directory

- `${CLAUDE_PLUGIN_DATA}` is set → resolve and confirm writable
- If unset → verify fallback `<project>/.project-files/.telemetry/` exists or can be created
- Warn if plugin data dir contains user-curated content that belongs in `.project-files/` (separation violation per `agent-standards.md`)
- Warn if `.project-files/.telemetry/` is not gitignored

### Hook scripts

- Each hook wired in settings.json must resolve to an existing file under `src/hooks/`
- Each hook script must be executable
- Each hook script must have a valid shebang (`#!/usr/bin/env bash` or language-appropriate)
- `_common.sh` must be sourced correctly
- `CLAUDE_PLUGIN_DATA` fallback must be present in scripts that log — check for the pattern `${CLAUDE_PLUGIN_DATA:-`

### settings.json resilience (Claude Code v2.1.121 / v2.1.122)

As of upstream v2.1.121 a malformed legacy enum value in `settings.json` no longer invalidates
the entire file, and v2.1.122 extends the same defensive parsing to a malformed `hooks` block.
`/env-doctor` mirrors this: a single broken hook entry is reported as a **targeted warning**
that names the specific event and hook index, never as a blanket "settings.json is invalid"
fatal. Errors elsewhere in the file are reported separately so a single bad hook does not mask
unrelated config issues.

When a hook entry fails to parse, `/env-doctor` reports:
- the event name (e.g. `PostToolUse`)
- the array index (e.g. `hooks[2]`)
- the parse error (truncated to one line)
- a remediation hint pointing at the entry

Other hooks are still validated — one bad entry does not short-circuit the rest of the report.

### External tools

- `git` — required for almost everything
- `jq` — required by hook scripts for structured logging
- `bash` / `zsh` — shell availability
- Project-specific tools inferred from `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`

### Concurrency (fan-out floor)

Read-only. Confirms the live environment can actually run the reviewer panel in parallel
rather than serialising it — a serialised panel starves floor members behind the concurrency
cap, which the fan-out policy treats as a security concern (a queued floor member must be
waited for, never dropped).

- Report whether `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` is set and, if so, its value.
- **WARN if it is set below 9** — the full grumpy-reviewer panel is 9 members, so a cap under 9
  serialises the panel and can starve floor members (security, code review). If unset, note that
  Claude Code's default (20) is above the panel size, so no warning.
- **Confirm Claude Code ≥ v2.1.128** — the parallel-fan-out floor (single-sourced in
  `.claude/rules/fan-out-policy.md` → *Parallel fan-out version floor*). Older versions cannot fan
  the panel out in parallel regardless of the env var; WARN with the detected version if below.
- **Cross-check against the fan-out policy.** Per `.claude/rules/fan-out-policy.md`, there is **no
  fixed batch-width constant** — batching engages only when the selected-set size would exceed the
  live cap. So WARN when `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` is **below the selected-set size
  the review would dispatch** (up to the 9-member full panel); below that, members queue and can
  appear hung. If the rule file is absent, skip the cross-check with a one-line note rather than
  failing.

This check never sets or mutates the env var — Parliament's no-policy stance means
`CLAUDE_CODE_MAX_*` env vars are the user's own to set (see `/settings-audit` for a
confirmation-gated opt-in snippet). `/env-doctor` only reports the divergence.

### Plugin orphans (Claude Code v2.1.121+)

When `--check-orphans` is passed, `/env-doctor` shells out to `claude plugin list
--orphaned` to identify plugins that were auto-installed as dependencies and now have
no dependent. v2.1.121 introduced `claude plugin prune` to remove them safely.

Behaviour:

- Without `--prune`: orphans are listed as `WARN — orphaned auto-installed plugin: <name>`. The check is read-only.
- With `--prune`: `/env-doctor` prints the `claude plugin prune` plan, asks for explicit confirmation, then invokes the upstream command. The plugin's own version-sync flow is unaffected — pruning only touches auto-installed dependencies.
- On Claude Code versions older than v2.1.121, both flags are no-ops with a one-line note explaining why.

Pairs with `/plugin-upgrade`: after a major upgrade, run `/env-doctor --check-orphans`
to see if any auto-installed companions can be removed cleanly.

### File locations per convention

- Agents: `agents/*.md` (not `src/agents/`, not `.claude/agents/`)
- Commands: `commands/*.md` (not `src/commands/`)
- Rules: `.claude/rules/*.md`
- Hooks: `src/hooks/*.sh`

### Directory separation

- `${CLAUDE_PLUGIN_DATA}/` contains only telemetry and plugin state
- `.project-files/` contains only user-curated planning artefacts
- Flag any cross-contamination (e.g. `.project-files/activity.jsonl` would be wrong)

## Process

1. Run each check; collect results with severity (`ok`, `warn`, `fail`).
2. If `--check-orphans`, query `claude plugin list --orphaned` and append warnings.
3. Render a single-screen report.
4. If `--fix-permissions`, propose diffs and request confirmation.
5. If `--prune`, after the report and explicit confirmation, run `claude plugin prune`.
6. Exit 0, or non-zero if `--strict` and any `fail` present. `--strict` never auto-invokes pruning.

## Output

```
# Env Doctor Report

## Plugin data directory
OK   — ${CLAUDE_PLUGIN_DATA} = /Users/jack/Library/Claude/plugin-data/chaos (writable)
OK   — .project-files/.telemetry/ is gitignored

## Hook scripts (4 wired in settings.json)
OK   — src/hooks/log_event.sh (executable, valid shebang)
OK   — src/hooks/notify_teams.sh (executable, valid shebang)
OK   — src/hooks/_common.sh (not directly wired; sourced by others)
OK   — src/hooks/log_debate_completion.sh (executable, valid shebang)
FAIL — src/hooks/log_event.sh does not contain CLAUDE_PLUGIN_DATA fallback pattern
       expected: ${CLAUDE_PLUGIN_DATA:-...}
       (see feedback_hooks_location.md)
WARN — settings.json: hooks.PostToolUse[2] failed to parse
       reason: "command" key is not a string
       remediation: edit that single entry; the rest of settings.json was loaded successfully

## External tools
OK   — git 2.47.0
OK   — jq 1.7.1
OK   — bash 5.2.32

## Concurrency (fan-out floor)
OK   — Claude Code v2.1.140 (≥ v2.1.128 parallel-fan-out floor)
WARN — CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS = 4 (below panel size 9)
       effect: serialises the 9-reviewer panel; can starve floor members behind the cap
       note: unset would default to 20 (safe); set it ≥ 9 or leave it unset
WARN — CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS (4) is below the selected-set size a --all review
       would dispatch (up to 9); members beyond the cap queue and can appear hung
       remediation: raise the cap to the panel size you run, or leave it unset (defaults to 20)

## Conventions
OK   — agents/ contains 33 files, all .md
OK   — commands/ contains 54 files, 1 manifest
OK   — .claude/rules/ contains 4 files

## Summary
5 warnings, 1 failure.

## Next steps
- Fix log_event.sh to use ${CLAUDE_PLUGIN_DATA:-$HOOK_PROJECT_DIR/.project-files/.telemetry} fallback
- Exit code: 1 (strict mode would have failed)
```

## Notes

- Read-only by default; `--fix-permissions` is the only mutating option and requires confirmation.
- Works on older Claude Code versions that don't set `CLAUDE_PLUGIN_DATA` — the fallback path check becomes the primary signal.
- Run as part of `/pre-commit-check` for belt-and-braces before pushing hook changes.
- Complements `/settings-audit` — this checks the runtime, that checks the config.
- `--strict` is the recommended mode for CI.
