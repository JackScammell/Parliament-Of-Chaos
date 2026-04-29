---
description: Validate runtime environment — plugin data dir, hook locations, tool availability, and fallback behaviour
effort: low
---

# Env Doctor

Runtime sanity check. Distinct from `/settings-audit` (which inspects configuration files): this command checks that the **live environment** the plugin runs in is correctly set up.

Closes the `feedback_hooks_location.md` footgun — if a hook script has drifted out of `src/hooks/`, Parliament silently loses that hook. This command makes the drift loud.

## Usage

```
/env-doctor [--fix-permissions] [--strict]
```

**Examples**:
```
/env-doctor                        # Report environment health
/env-doctor --strict               # Exit non-zero on any warning (for CI)
/env-doctor --fix-permissions      # chmod any hook scripts missing executable bit (with diff preview)
```

## Options

- `--fix-permissions`: Apply minimal permission fixes (chmod +x on hook scripts). Shows a diff of intended changes before applying.
- `--strict`: Exit non-zero if any check fails. Intended for release gates.

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
2. Render a single-screen report.
3. If `--fix-permissions`, propose diffs and request confirmation.
4. Exit 0, or non-zero if `--strict` and any `fail` present.

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

## Conventions
OK   — agents/ contains 33 files, all .md
OK   — commands/ contains 54 files, 1 manifest
OK   — .claude/rules/ contains 3 files

## Summary
3 warnings, 1 failure.

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
