---
description: Review new Claude Code changelog entries since last review and propose Parliament features
effort: medium
context: fork
background: false
agent: deliberation-conductor
argument-hint: "[--mode fast|consensus|deep] [--focus <area>] [--full]"
---

# Changelog Review

Fetch the Claude Code changelog, identify **only new entries since the last review**, and run a structured deliberation to propose implementation plans for Parliament of Chaos.

## Usage

```
/changelog-review [--mode fast|consensus|deep] [--focus <area>] [--full]
```

**Examples**:
```
/changelog-review                          # Only new entries since last review
/changelog-review --full                   # Review entire changelog (first run or reset)
/changelog-review --mode deep              # Deep analysis of new entries
/changelog-review --focus hooks            # Only hook-related new entries
```

## Options

- `--mode` (optional): Deliberation mode for evaluating features
  - `fast`: Quick 3-round assessment (default)
  - `consensus`: Balanced 5-round evaluation
  - `deep`: Thorough 7-10 round analysis

- `--focus` (optional): Filter to a specific area
  - `hooks`: New hook events and capabilities
  - `agents`: Agent system changes (frontmatter, teams, isolation)
  - `plugins`: Plugin system enhancements
  - `commands`: New CLI commands and features
  - `performance`: Performance and token optimisations
  - `all`: Everything (default)

- `--full` (optional): Ignore the last-reviewed marker and review the entire changelog. Useful for first run or to reset the review state.

## State Tracking

The command maintains a state file at `${CLAUDE_PLUGIN_DATA}/changelog-review/last-reviewed.json`:

```json
{
  "last_reviewed_version": "v2.1.78",
  "last_reviewed_date": "2026-03-18",
  "parliament_version": "1.4.0",
  "entries_reviewed": 45,
  "features_proposed": 12,
  "features_implemented": 8
}
```

This file is updated after each review so that subsequent runs only process **new changelog entries**.

## Process

1. **Load Review State**
   - Read `${CLAUDE_PLUGIN_DATA}/changelog-review/last-reviewed.json`
   - If file does not exist or `--full` is passed, treat as first run (review everything)
   - Extract `last_reviewed_version` to determine the cutoff point

2. **Fetch Changelog**
   - Fetch https://code.claude.com/docs/en/changelog using WebFetch
   - Extract all entries with dates and version numbers
   - **Filter to only entries newer than `last_reviewed_version`**
   - If no new entries found, report "No new Claude Code releases since last review" and exit

3. **Categorise New Features**
   Group new capabilities into:
   - **Agent & Team Features**: frontmatter, memory, isolation, teams
   - **Plugin System**: persistent state, settings, variables
   - **Hook System**: new events, HTTP hooks, hook context
   - **Commands & UX**: new slash commands, effort levels
   - **Performance & Config**: model overrides, memory, token optimisation

4. **Compare Against Current State**
   - Read current `CHANGELOG.md` to identify what Parliament already implements
   - Read `.claude/rules/agent-standards.md` for current agent standards
   - Read `hooks/hooks.json` for current hook configuration
   - Identify gaps between new Claude Code capabilities and Parliament features
   - Skip features already implemented in previous reviews

5. **Deliberation** (only if new relevant features found)
   Run a structured debate with relevant Parliament agents:
   - **system-architect**: Evaluate architectural impact
   - **config-curator**: Evaluate configuration implications
   - **pipeline-engineer**: Evaluate deployment/CI implications
   - **refactor-ranger**: Evaluate code quality opportunities
   - **grumpy-architecture-skeptic**: Challenge proposals
   - **grumpy-maintainability-curmudgeon**: Challenge complexity

6. **Update State and Produce Plan**
   - Write updated `last-reviewed.json` with the newest version reviewed
   - Save review results to `${CLAUDE_PLUGIN_DATA}/changelog-review/reviews/YYYY-MM-DD.md`
   - Generate implementation proposal

## Output

```markdown
# Claude Code Changelog Review

**New entries**: [version range, e.g. v2.1.79 — v2.1.82]
**Previous review**: v2.1.78 on 2026-03-18
**Current Parliament Version**: 1.4.0
**New features found**: N relevant / M total in new entries

## New Entries Reviewed

### v2.1.82 (2026-03-25)
- [feature 1]
- [feature 2]

### v2.1.81 (2026-03-24)
- [feature 1]

## Relevance Assessment

### Relevant to Parliament (N features)
| Feature | Version | Category | Impact |
|---------|---------|----------|--------|
| ... | v2.1.82 | hooks | High |

### Not Relevant (M features)
- [brief list of skipped features with reason]

## Deliberation Summary
[condensed debate results — only runs if relevant features found]

## Proposed Changes
### Priority 1 (implement now)
- [specific changes]

### Priority 2 (next release)
- [specific changes]

### Deferred
- [features to revisit later]

## Next Steps
- Run `/roadmap-add-item` for approved items
- Run `/roadmap-item-scope` to detail specifications

## Review State Updated
- Last reviewed version: v2.1.82
- Review saved to: ${CLAUDE_PLUGIN_DATA}/changelog-review/reviews/2026-03-25.md
```

## Review History

Past reviews are saved to `${CLAUDE_PLUGIN_DATA}/changelog-review/reviews/` with one file per review date. This provides:

- **Audit trail**: What was reviewed and when
- **Decision history**: Why features were accepted, deferred, or rejected
- **Trend tracking**: How frequently Claude Code adds relevant features

## Integration

This command is designed to be run regularly to keep Parliament of Chaos aligned with Claude Code:

1. **Incremental by default** — only reviews new entries since the last run
2. **State-tracked** — remembers what has been reviewed via `last-reviewed.json`
3. **History-preserving** — saves each review for future reference
4. **Actionable output** — produces items ready for `/roadmap-add-item`

## Notes

- Requires internet access to fetch the changelog via WebFetch
- First run (or `--full`) reviews the entire changelog and establishes the baseline
- Subsequent runs only process new entries — fast and focused
- The deliberation is skipped entirely if no relevant new features are found
- State file lives in `${CLAUDE_PLUGIN_DATA}/` which persists across plugin updates
- Run `/parliament-loop 1w /changelog-review --mode fast` for weekly automated checks
- Use `--full` to reset and re-evaluate everything (e.g., after a major Parliament release)
