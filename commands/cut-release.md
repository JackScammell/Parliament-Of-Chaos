---
description: Automate version bumping, changelog generation, tagging, and release notes
effort: medium
argument-hint: "[--version <semver>] [--dry-run] [--no-tag]"
---

# Cut Release

Orchestrate the full release ceremony: determine next version, generate changelog entries, bump version across all relevant files, create git tag, and draft release notes.

## Usage

```
/cut-release [--version <semver>] [--dry-run] [--no-tag]
```

**Examples**:
```
/cut-release                         # Auto-detect next version from commits
/cut-release --version 2.0.0         # Explicit version
/cut-release --dry-run               # Preview changes without modifying files
```

## Options

- `--version` (optional): Explicit semver version. If omitted, auto-detect from conventional commits (`feat:` = minor, `fix:` = patch, `BREAKING CHANGE:` = major)
- `--dry-run` (optional): Show what would change without modifying any files
- `--no-tag` (optional): Skip git tag creation

## Process

1. **Detect Current Version**
   - Read version from `package.json`, `pyproject.toml`, `Cargo.toml`, `plugin.json`, `marketplace.json`, or equivalent
   - If multiple version files exist, verify they agree

2. **Determine Next Version**
   - If `--version` provided, use it
   - Otherwise, parse commits since last tag using conventional commit prefixes
   - `BREAKING CHANGE:` or `!:` = major bump
   - `feat:` = minor bump
   - `fix:`, `perf:`, `refactor:` = patch bump

3. **Generate Changelog**
   - Delegate to `/release-notes-draft` (the single owner of changelog-generation
     logic — do not reimplement its git-log parsing/grouping here): parse
     `git log` since last tag, group by type (Added, Changed, Fixed, Removed),
     emit Keep a Changelog formatted entries
   - Prepend the result to `CHANGELOG.md`, and add the `[X.Y.Z]:` compare link
     at the bottom of the file (see RELEASE_INSTRUCTIONS.md — this was missed
     for 8 consecutive releases before v1.24)

4. **Bump Version**
   - Update version in ALL detected version-bearing files
   - Verify all version strings match after update

5. **Create Tag** (unless `--no-tag`)
   - Create annotated git tag `vX.Y.Z`
   - Tag message includes changelog entries

6. **Draft Release Notes**
   - Output markdown suitable for GitHub Releases
   - Include changelog entries, contributor mentions, and upgrade notes for breaking changes

## Output

```markdown
# Release vX.Y.Z

## Changes
- [changelog entries]

## Version Files Updated
- [list of files and old → new version]

## Next Steps
- Review changes and commit
- Push with tags: `git push origin main --tags`
- Create GitHub release from tag
```

## Notes

- Detects version files automatically — supports Node.js, Python, Rust, Go, and plugin.json/marketplace.json
- Version must be synced across ALL version-bearing files (learned from Parliament v1.3.0 incident)
- Use `--dry-run` first to preview before committing
