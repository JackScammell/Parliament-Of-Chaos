---
description: Auto-generate CHANGELOG entries from merged PRs and commits since the last release
effort: medium
argument-hint: "[--since <tag>] [--version <next>] [--style keepachangelog|simple] [--apply]"
---

# Release Notes Draft

Draft a CHANGELOG entry from git history and merged PRs since the last release. Addresses the `feedback_release_process.md` footgun: hand-writing release notes at release time is error-prone and the `version must be synced across plugin.json, marketplace.json, and CHANGELOG` rule is easy to miss.

## Usage

```
/release-notes-draft [--since <tag>] [--version <next>] [--style keepachangelog|simple] [--apply]
```

**Examples**:
```
/release-notes-draft                               # Since last tag, infer next version
/release-notes-draft --since v1.10.0               # Explicit since
/release-notes-draft --version 1.14.0              # Explicit next version
/release-notes-draft --apply                       # Write into CHANGELOG.md (with diff preview)
```

## Options

- `--since <tag>`: Git tag to start from. Defaults to the most recent tag matching `v*`.
- `--version <next>`: Next version number. Defaults to a semver bump inferred from change classification (feat → minor, fix → patch, BREAKING → major).
- `--style <format>`: `keepachangelog` (default, matches Parliament's CHANGELOG format) or `simple` (bulleted list).
- `--apply`: Insert the drafted entry at the top of `CHANGELOG.md` after showing a diff preview.

## Process

1. **Find the boundary** — resolve `--since` or auto-detect the latest tag via `git describe --tags --abbrev=0`.
2. **Enumerate commits** — `git log <since>..HEAD --no-merges --pretty=...` with commit subject, body, and associated PR number (parsed from merge commits or trailer lines).
3. **Classify** each commit/PR using conventional-commit heuristics and keyword scan:
   - `feat:`, `add:` → Added
   - `fix:`, `bug:` → Fixed
   - `change:`, `refactor:`, `update:` → Changed
   - `remove:`, `delete:` → Removed
   - `deprecate:` → Deprecated
   - `security:`, `CVE`, `vulnerability` → Security
   - `BREAKING CHANGE:` trailer → flagged under Added/Changed with a **BREAKING** prefix
4. **Deduplicate** — collapse commits that reference the same PR. Merge squashed-PR titles and body bullets.
5. **Cross-check manifest** — any new command files require a matching entry in `commands/manifest.yaml`. Flag misses.
6. **Invoke `doc-bard`** for wording cleanup and consistent tone.
7. **Render** in the requested style and print.
8. **`--apply`** — insert between the top-of-file header and the current most-recent release, showing a diff first.

## Output

```markdown
## [1.14.0] - 2026-04-24

### Added
- `/new-widget`: does a thing (PR #142)
- Hook `SubagentStart` wired to log_event.sh (PR #138)

### Changed
- `/parliament-review` now warns when running outside a git repo (PR #140)

### Fixed
- `/cost-report estimate` no longer divides by zero when telemetry is empty (PR #139)

### Security
- Upgraded `jq` advisory dep pin to ≥ 1.7.1 for CVE-2024-XXXX (PR #141)

### Unclassified (review manually)
- Commit abc1234: "misc tweaks" — no conventional-commit prefix

---

# Release Notes Draft Report

**Since**: v1.13.0 (2026-04-17)
**Proposed version**: 1.14.0 (minor bump — feat present, no BREAKING)
**Commits analysed**: 38 across 7 PRs
**Manifest sync check**: 1 new command file, 1 manifest entry — OK

## Next steps
- Review the "Unclassified" section
- Run /release-notes-draft --apply to commit the draft
- Run /cut-release to bump version files and tag
```

## Notes

- Read-only by default. `--apply` is the only mutating mode and always requires explicit confirmation with a diff preview.
- This command **drafts** notes; it never bumps version strings. That's `/cut-release`'s job. The two are designed to chain: draft → review → cut.
- Version inference follows semver:
  - Any BREAKING → major bump
  - Any `feat:` → minor bump
  - Only `fix:` / `chore:` → patch bump
- Manifest sync check prevents shipping a new command that isn't declared — ties into Tier 1's `/parliament-doctor`.
- For Parliament's own CHANGELOG, the "keepachangelog" style is mandatory — other projects can opt into `--style simple`.
