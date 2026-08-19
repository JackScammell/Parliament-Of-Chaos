---
description: Interactive dependency update with changelog review and test verification
effort: medium
argument-hint: "[--all] [--patch] [--minor] [--major] [--security]"
---

# Update Dependencies

Interactive dependency update workflow: show outdated packages, review changelogs for breaking changes, update incrementally, and run tests between each update to catch breakage early.

## Usage

```
/update-dependencies [--all] [--patch] [--minor] [--major] [--security]
```

**Examples**:
```
/update-dependencies                 # Show outdated packages and update interactively
/update-dependencies --patch         # Apply all patch updates automatically
/update-dependencies --security      # Update only packages with known vulnerabilities
/update-dependencies --major         # Show and walk through major version updates
```

## Options

- `--all` (optional): Update all outdated packages in one pass (with tests between each)
- `--patch` (optional): Auto-apply all patch version updates (assumed safe)
- `--minor` (optional): Auto-apply all minor version updates
- `--major` (optional): Include major version updates (shown individually with changelog review)
- `--security` (optional): Only update packages with known security vulnerabilities

## Process

1. **Detect Package Manager**
   - Identify from lock files: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Pipfile.lock`, `poetry.lock`, `go.sum`, `Cargo.lock`, `Gemfile.lock`, `composer.lock`
   - Support monorepo structures (workspaces)

2. **List Outdated Packages**
   - Run the appropriate outdated command (`npm outdated`, `pip list --outdated`, etc.)
   - Categorise updates by semver level: patch, minor, major
   - Flag packages with known vulnerabilities
   - Show current version, latest version, and update type for each

3. **Update Incrementally**
   - For each update (or batch if `--patch`/`--minor`):
     1. Show the package, current version, target version
     2. For minor/major updates: fetch and summarise the changelog or release notes
     3. Apply the update
     4. Run the project's test suite
     5. If tests pass: keep the update, move to next
     6. If tests fail: roll back the update, report the failure, continue with remaining packages

4. **Report Results**
   - Packages successfully updated
   - Packages that failed (with test failure details)
   - Packages skipped (user chose not to update)
   - Remaining outdated packages

## Output

```
# Update Dependencies

**Package manager**: npm (from package-lock.json)
**Outdated packages**: 12 (3 patch, 6 minor, 3 major)
**Vulnerabilities**: 2 packages

## Update Plan

### Patch Updates (auto-applied)
| Package | From | To | Status |
|---------|------|----|--------|
| lodash | 4.17.20 | 4.17.21 | Updated (tests pass) |
| axios | 1.6.2 | 1.6.8 | Updated (tests pass) |
| dayjs | 1.11.10 | 1.11.13 | Updated (tests pass) |

### Minor Updates
| Package | From | To | Status |
|---------|------|----|--------|
| react-query | 5.17.0 | 5.24.1 | Updated (tests pass) |
| zod | 3.22.0 | 3.24.2 | Updated (tests pass) |
| vite | 5.1.0 | 5.4.3 | FAILED (3 test failures in build config) — rolled back |

### Major Updates (require review)
| Package | From | To | Breaking Changes |
|---------|------|----|-----------------|
| next | 14.1.0 | 15.0.3 | App Router changes, React 19 required |
| eslint | 8.56.0 | 9.0.0 | Flat config required, many rule changes |

## Summary: 7 updated, 1 failed (rolled back), 2 major updates deferred, 2 already at latest
```

## Notes

- Patch updates are applied as a batch for speed; minor/major are applied individually
- Test suite must be detected and runnable for the incremental safety check to work
- If no test suite exists, updates are applied but with a warning that they are unverified
- Rolled-back packages are restored to their exact previous version including lock file
- For major updates, summarises breaking changes from the package's CHANGELOG or GitHub releases
