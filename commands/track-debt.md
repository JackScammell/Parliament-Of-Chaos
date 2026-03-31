---
description: Scan, categorise, and track technical debt across the codebase
effort: medium
---

# Track Debt

Systematically scan the codebase for technical debt indicators, categorise and prioritise them, and maintain a living debt ledger that tracks trends over time.

## Usage

```
/track-debt [--category <type>] [--severity <level>] [--trend]
```

**Examples**:
```
/track-debt                          # Full scan and report
/track-debt --category security      # Only security-related debt
/track-debt --severity high          # Only high-severity items
/track-debt --trend                  # Compare against previous scan and show trends
```

## Options

- `--category` (optional): Filter by type — `security`, `performance`, `maintainability`, `test`, `dependency`
- `--severity` (optional): Filter by severity — `critical`, `high`, `medium`, `low`
- `--trend` (optional): Compare against previous scan to show new debt added and old debt resolved

## Process

1. **Scan for Debt Markers**
   - `TODO`, `FIXME`, `HACK`, `XXX`, `@deprecated` comments
   - Extract: location, content, author (git blame), age

2. **Analyse Code Quality Indicators**
   - Cyclomatic complexity hotspots
   - Duplicated code blocks
   - Long methods/functions exceeding reasonable thresholds
   - Deeply nested conditionals

3. **Check Coverage Gaps**
   - Identify critical paths without test coverage
   - Flag untested error handlers and edge cases

4. **Audit Dependencies**
   - Outdated packages with known vulnerabilities
   - Deprecated APIs still in use
   - Pinned versions that are multiple majors behind

5. **Categorise and Prioritise**
   - Category: security, performance, maintainability, test, dependency
   - Severity: based on age, location (hot path vs. cold path), and risk
   - Estimated effort: small/medium/large

6. **Store Results**
   - Save inventory to `${CLAUDE_PLUGIN_DATA}/tech-debt/inventory.json`
   - On subsequent runs with `--trend`, diff against previous inventory

## Output

```markdown
# Technical Debt Report

**Total items**: 47 (8 critical, 15 high, 18 medium, 6 low)
**Trend**: +3 new, -5 resolved since last scan

## Critical
| Location | Category | Age | Description |
|----------|----------|-----|-------------|
| src/auth.ts:42 | security | 90d | TODO: validate JWT expiry |

## Summary by Category
| Category | Count | Oldest |
|----------|-------|--------|
| Security | 8 | 120 days |
| Maintainability | 22 | 45 days |
```

## Notes

- Trend tracking requires previous scan data in `${CLAUDE_PLUGIN_DATA}/tech-debt/`
- Pairs well with `/roadmap-add-item` to schedule debt paydown sprints
- Does not modify code — report only
