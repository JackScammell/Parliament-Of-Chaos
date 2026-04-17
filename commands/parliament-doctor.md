---
description: Reconcile the command manifest against commands/*.md and the skill registry — report orphans, ghosts, and drift
effort: medium
---

# Parliament Doctor

Hygiene command that checks consistency between three sources of truth:

1. `commands/manifest.yaml` — declared registry of slash commands
2. `commands/*.md` — actual command definitions on disk
3. The registered skill surface (the `/chaos:` list shown in session startup)

Drift between any of these three indicates either a command that ships without being announced (an **orphan**) or a manifest entry without a backing file (a **ghost**). This command finds them, reports them, and proposes a resolution.

## Usage

```
/parliament-doctor [--fix-manifest] [--strict] [--json]
```

**Examples**:
```
/parliament-doctor                  # Report drift
/parliament-doctor --strict         # Exit non-zero if any drift is present
/parliament-doctor --fix-manifest   # Propose manifest patches (always with diff preview)
/parliament-doctor --json           # Emit machine-readable report
```

## Options

- `--fix-manifest` (optional): Proposes manifest edits for clear-cut cases (e.g. a new command file with no manifest entry) and shows a diff before asking for confirmation. Never applies changes without approval.
- `--strict` (optional): Treat any drift as a failure. Suitable for CI / pre-release gates.
- `--json` (optional): Emit a structured report instead of markdown — useful for `/parliament-metrics` and other downstream tooling.

## Process

1. **Load manifest**
   - Parse `commands/manifest.yaml`
   - Collect declared command names, statuses, `skill_surface` flags, and effort levels

2. **Scan command files**
   - Enumerate `commands/*.md` (excluding `manifest.yaml` itself)
   - For each file, parse the frontmatter and record `name` (from filename) and `effort`

3. **Probe skill surface**
   - Inspect the skill registry available in the current session (the `/chaos:` list)
   - Record which declared commands are actually exposed as skills

4. **Reconcile**
   - **Orphans**: command file exists, not listed in manifest
   - **Ghosts**: manifest entry exists, no command file
   - **Hidden**: `skill_surface: true` in manifest, but command is missing from the `/chaos:` list
   - **Leaked**: `skill_surface: false` in manifest, but command appears in the `/chaos:` list
   - **Effort mismatch**: effort in frontmatter does not match manifest entry
   - **Driverless agents**: agents listed in `agents_requiring_driver` whose driver command is missing or not `active`

5. **Report**
   - Summarise counts per category
   - List each discrepancy with a clear resolution (expose, delete, update manifest, rename, etc.)
   - Apply the governance priority when resolutions conflict: security > correctness > maintainability > performance > convenience

## Output

```
# Parliament Doctor Report

**Manifest version**: 1 (updated 2026-04-17)
**Command files**: 48
**Manifest entries**: 48
**Skill-exposed**: 48

## Status
OK — zero drift between manifest, command files, and skill surface.

## Checks
- Orphans:            0
- Ghosts:             0
- Hidden skills:      0
- Leaked skills:      0
- Effort mismatches:  0
- Driverless agents:  0

## Notes
- Last orphan reconciliation: 2026-04-17 (Tier 1, v1.10.0)
- Previously orphaned commands now active: 12
```

If drift is detected, each category is rendered as a table:

```
## Orphans (command file with no manifest entry)
| File | Frontmatter effort | Suggested status | Suggested owner |
|------|--------------------|------------------|-----------------|
| commands/new-thing.md | medium | active | TBD — open a PR to assign |

## Ghosts (manifest entry with no file)
| Name | Declared status | Action |
|------|-----------------|--------|
| old-thing | deprecated | Remove from manifest or restore file |
```

## Exit Behaviour

- Default: always exits 0. Report is advisory.
- `--strict`: exits non-zero if any of orphans / ghosts / hidden / leaked / mismatches / driverless is non-zero. Use in release gates.

## Integration

- Run before `/cut-release` to prevent shipping with undeclared commands.
- Pair with `/parliament-optimize` — `/parliament-optimize` audits *agents*, `/parliament-doctor` audits *commands*.
- `/telemetry-query` can chart drift count over time once Tier 3 ships.

## Notes

- Read-only by default — never modifies files unless `--fix-manifest` is explicitly passed and confirmed.
- The manifest is the source of truth for `/list-commands` grouping and `/version` counts once Tier 1 is complete.
- If the skill surface cannot be probed (older Claude Code versions without the skill list), that check is skipped with a warning rather than treated as drift.
