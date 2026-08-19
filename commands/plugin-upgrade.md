---
description: Version-sync migration helper — bumps plugin.json, marketplace.json, and CHANGELOG together
effort: medium
argument-hint: "<next-version> [--check] [--from <current>] [--no-changelog] [--tag|--no-tag]"
---

# Plugin Upgrade

Version-sync enforcer for Parliament of Chaos. Addresses the `feedback_release_process.md` footgun: the version number must be identical across `plugin.json`, `marketplace.json`, and `CHANGELOG.md`, and it is easy to forget one.

This is a migration helper for **maintainers of the plugin**. End users do not run it.

## Usage

```
/plugin-upgrade <next-version> [--check] [--from <current>] [--no-changelog] [--tag|--no-tag]
```

**Examples**:
```
/plugin-upgrade 1.14.0                    # Bump everything to 1.14.0
/plugin-upgrade 1.14.0 --check            # Dry-run: report mismatches without fixing
/plugin-upgrade 1.14.0 --from 1.13.0      # Explicit current version
/plugin-upgrade 1.14.0 --no-changelog     # Skip CHANGELOG.md (assume already drafted)
/plugin-upgrade 1.14.0 --tag              # Also create a release git tag via `claude plugin tag`
```

## Options

- `<next-version>` (required, positional): Target semver. Must be strictly greater than current.
- `--check`: Report-only — show which files would change, never write.
- `--from <current>`: Explicit current version for diffing. Defaults to the value in `plugin.json`.
- `--no-changelog`: Skip CHANGELOG rewrite (use when `/release-notes-draft --apply` has already written the entry with the new version header).
- `--tag` / `--no-tag`: Run `claude plugin tag <next-version>` after a successful version bump to create a release git tag with upstream's version-validation logic. Defaults to **off** (`--no-tag`) until proven across a few releases. Requires Claude Code v2.1.118 or newer; older versions ignore the flag with a warning.

## Version-bearing files

| File | How version is stored |
|------|-----------------------|
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `.claude-plugin/marketplace.json` | `"version": "X.Y.Z"` in **both** the top-level `metadata` block and the `plugins[0]` block |
| `CHANGELOG.md` | `## [X.Y.Z] - YYYY-MM-DD` entry at the top of file (below the header) |
| `RELEASE_INSTRUCTIONS.md` (optional) | Referenced version strings |
| `README.md` (optional) | Referenced version in install snippets |

The command maintains the authoritative list in `${CLAUDE_PLUGIN_DATA}/version-sync-paths.json` — editable when the set of version-bearing files changes.

## Process

1. **Detect current version** — read `plugin.json`. Cross-check `marketplace.json` (both places) and the top CHANGELOG entry. Any mismatch is a **pre-existing drift** and surfaced before proceeding.
2. **Validate target** — must parse as semver; must be strictly greater than current; no skipping majors without `--allow-major-skip` (reserved).
3. **Compute edits**:
   - `plugin.json`: replace `"version":` value
   - `marketplace.json`: replace both `"version":` values
   - `CHANGELOG.md`: insert `## [X.Y.Z] - YYYY-MM-DD` stub, or verify one already exists (with `--no-changelog`)
4. **Preview diff** — render a unified diff across all target files.
5. **Apply** (unless `--check`) — write files atomically; stage them for the caller to commit.
6. **Post-conditions check** — re-read all files and confirm versions agree. If any file is out of sync after the write, abort with a loud error.
7. **Tag (optional)** — if `--tag` is set, invoke `claude plugin tag <next-version>` after the post-conditions check. The upstream command performs its own version validation; failures surface verbatim and abort before the next-step prompt. Skipped on Claude Code < v2.1.118 with a warning.
8. **Emit a next-step prompt** — suggests `/release-notes-draft --apply` (if changelog skipped) and `git commit` wording.

## Output

```
# Plugin Upgrade

**Current**: 1.13.0
**Target**:  1.14.0

## Pre-flight
OK — .claude-plugin/plugin.json reports 1.13.0
OK — .claude-plugin/marketplace.json (metadata) reports 1.13.0
OK — .claude-plugin/marketplace.json (plugins[0]) reports 1.13.0
OK — CHANGELOG.md top entry is [1.13.0]

No pre-existing drift.

## Proposed edits
--- .claude-plugin/plugin.json
-   "version": "1.13.0",
+   "version": "1.14.0",

--- .claude-plugin/marketplace.json  (metadata)
-     "version": "1.13.0"
+     "version": "1.14.0"

--- .claude-plugin/marketplace.json  (plugins[0])
-       "version": "1.13.0",
+       "version": "1.14.0",

--- CHANGELOG.md
+ ## [1.14.0] - 2026-04-24
+
+ ### Added
+ - TODO: fill in — prefer running /release-notes-draft --apply
+
  ## [1.13.0] - 2026-04-17

Apply these edits? [y/N]
```

## Post-upgrade verification

After applying, the command runs a mini version of `/parliament-doctor` focused on version-sync:

```
## Post-conditions
OK — All three files report 1.14.0
OK — CHANGELOG.md has an entry for 1.14.0
OK — No version downgrade or skip detected

Next:
- /release-notes-draft --apply --version 1.14.0     (if CHANGELOG was left as stub)
- git commit -am "v1.14.0: ..."
- git tag v1.14.0                                   (skip if --tag was used)
- git push && git push --tags
```

When invoked with `--tag`, the post-conditions block additionally reports:

```
## Tagging
OK — claude plugin tag 1.14.0 succeeded
     created tag: v1.14.0
     validated against: .claude-plugin/plugin.json (1.14.0)
```

## Notes

- Refuses to run inside a detached HEAD without an explicit `--force` flag (reserved).
- Refuses to run on a dirty tree by default — commit or stash first. Override with `--dirty` (reserved).
- Uses atomic writes so a crash mid-run never leaves files partially updated.
- Encodes the project rule from `feedback_release_process.md` — this command is the automation of that feedback note.
- `/cut-release` wraps this command plus tagging, pushing, and release-note generation. Use `/cut-release` end-to-end; use `/plugin-upgrade` for the version-bump step in isolation.
- After a successful bump, `/plugin-upgrade` suggests `/env-doctor --check-orphans` (Claude Code v2.1.121+) so any auto-installed plugin dependencies that became orphans during the upgrade can be reviewed and pruned. The suggestion is informational; pruning is never automatic.
