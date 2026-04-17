---
description: Detect stale or fabricated documentation after code changes — symmetric to /onboard-codebase
effort: medium
---

# Docs Audit

`/onboard-codebase` generates documentation from code. This is its symmetric opposite: it checks that existing documentation still reflects the code. Catches stale references, renamed APIs, deleted files, and fabricated claims.

Identified in the toolset-gaps debate as a Tier 4 item: docs tooling was "generate but not audit".

## Usage

```
/docs-audit [--scope <path>] [--since <ref>] [--doc-globs <pattern>] [--severity <level>]
```

**Examples**:
```
/docs-audit                                       # Full project audit
/docs-audit --since v1.11.0                       # Only docs changed or affected since the tag
/docs-audit --scope docs/                         # Audit a single directory
/docs-audit --doc-globs "README.md,docs/**/*.md"  # Custom glob set
/docs-audit --severity high                       # Only High and Critical findings
```

## Options

- `--scope <path>`: Limit to a path (applies to both docs and code).
- `--since <ref>`: Git ref; restrict to docs whose code dependencies have changed since the ref.
- `--doc-globs <pattern>`: Comma-separated globs identifying documentation files. Default: `README.md,CHANGELOG.md,CONTRIBUTING.md,docs/**/*.md,**/*.mdx,.project-files/**/*.md`.
- `--severity <level>`: Minimum severity to surface (Low / Medium / High / Critical).

## Checks

### Stale references (High)
- File paths mentioned in docs that no longer exist
- Function / class / agent names mentioned that no longer exist
- Slash commands referenced that are not in `commands/manifest.yaml` or are `status: deprecated`
- CLI flags documented that no longer appear in the target code
- Environment variables documented that no longer appear in the code

### Fabricated claims (Critical)
- Code blocks in docs that reference nonexistent symbols
- Version numbers mentioned that never shipped (cross-check with `CHANGELOG.md`)
- Links to headings that no longer exist in the linked file

### Drift without breakage (Medium)
- Docs not modified since a related code file was substantially changed
- Changelog entries whose linked PR/issue is closed with "won't fix" or reverted

### Completeness gaps (Low)
- Public exports or agents/commands with no documentation anywhere
- README missing a section present in the project's documented structure

## Process

1. **Enumerate documentation** — expand `--doc-globs` within `--scope`.
2. **Extract claims** — for each doc, parse:
   - File paths and directory references
   - Code-fenced blocks and their languages
   - Cross-document links and heading anchors
   - Slash command invocations
   - Agent name references
3. **Cross-check against code and manifest**:
   - `ls` each referenced path
   - Parse source files for symbol existence
   - Consult `commands/manifest.yaml` for command validity
   - Parse `CHANGELOG.md` for version claims
4. **Check freshness** — for each doc, find the most recent commit touching related code; if the doc is older, flag as drift.
5. **Delegate to `doc-bard`** for the completeness-gap pass — the specialist applies judgement to what "needs documentation" means for this project.
6. **Invoke `grumpy-documentation-pedant`** for critique and verdict.

## Output

```
# Docs Audit

**Scope**: full project
**Docs scanned**: 42
**Claims checked**: 638

## Verdict
REJECT — 3 Critical and 7 High issues.

## Critical (3)
| Doc | Line | Claim | Reality |
|-----|------|-------|---------|
| README.md | 142 | `parliament-cli --debug` flag | Flag does not exist in any bin/*.ts |
| docs/agents.md | 88 | Agent `migration-guru` | No such agent; closest match `migration-monk` |
| CHANGELOG.md | 210 | v1.7.1 | Version never shipped (jumped 1.7.0 → 1.8.0) |

## High (7)
| Doc | Issue | Suggested action |
|-----|-------|------------------|
| docs/setup.md | References removed script src/hooks/handle_post_compact.sh | Update to log_event.sh |
| ...  | ...   | ...              |

## Medium (12)
[collapsed — use --severity medium to expand]

## Low (18)
[collapsed]

## Next steps
- /summon-specialist doc-bard to apply mechanical fixes
- /adr-new "Doc freshness SLO" if cadence needs formalising
```

## Notes

- Read-only — this command never edits docs. Use `/summon-specialist doc-bard` to apply fixes, or `/update-docs` for automated repair.
- Cross-language support: Python docstrings, JSDoc blocks, Go doc comments, and YARD/RDoc are all parsed best-effort.
- False positives are possible in docs that reference external systems — tune with `--scope` or a local `.docsignore` file.
- Run regularly via `/parliament-loop 1w /docs-audit --since 1w` to catch drift early.
- The `grumpy-documentation-pedant` verdict is authoritative — reviewer approval required before closing drift.
