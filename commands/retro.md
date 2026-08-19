---
description: Structured retrospective from git history and session activity
effort: medium
argument-hint: "[--since <date|tag>] [--focus <area>]"
---

# Retro

Run a structured retrospective by analysing recent git history, session logs, and project activity. Identifies patterns, recurring issues, and produces actionable improvements.

## Usage

```
/retro [--since <date|tag>] [--focus <area>]
```

**Examples**:
```
/retro                               # Retro since last tag/release
/retro --since 2026-03-01            # Retro for March
/retro --since v1.6.0                # Retro since a specific release
/retro --focus reviews               # Focus on review cycle patterns
```

## Options

- `--since` (optional): Start date or git tag (default: since last tag)
- `--focus` (optional): Focus area — `reviews`, `velocity`, `quality`, `incidents`, `all` (default)

## Process

1. **Gather Data**
   - Parse git log for the period: commits, authors, merge frequency, revert frequency
   - Read review/debate logs from `${CLAUDE_PLUGIN_DATA}/` if available
   - Analyse commit message patterns (fix frequency, feature velocity)

2. **Identify Patterns**
   - Repeated fix commits to the same files (instability hotspots)
   - Long-lived branches (merge pain indicators)
   - Revert frequency (release quality signal)
   - Commit clustering patterns (crunch vs. steady pace)

3. **Assess Quality**
   - Ratio of feature commits to fix commits
   - Files with highest churn (most changes in the period)
   - Test coverage trends if data available

4. **Produce Retrospective**
   - What went well (completed features, stable areas)
   - What went poorly (hotspots, reverts, repeated fixes)
   - Action items with specific owners and deadlines
   - Metrics summary

## Output

```markdown
# Retrospective: v1.6.0 → v1.7.0

## What Went Well
- 12 features shipped, 0 reverts
- src/hooks/ refactored with shared helper (reduced duplication)

## What Needs Attention
- commands/ had 34 files touched in one commit (high blast radius)
- 3 fix commits to the same auth module (instability hotspot)

## Action Items
- [ ] Add integration tests for auth module
- [ ] Split large command batches into smaller PRs

## Metrics
| Metric | Value |
|--------|-------|
| Commits | 47 |
| Features | 12 |
| Fixes | 8 |
| Reverts | 0 |
```
