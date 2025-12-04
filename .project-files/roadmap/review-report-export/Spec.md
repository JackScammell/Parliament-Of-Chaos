# Specification: review-report-export

## Overview

**Item**: review-report-export
**Phase**: 4 (Quality of Life Features)
**Dependencies**: None

## Problem Statement

Council and review outputs are currently displayed in the conversation but not persisted. Users cannot:
1. Share review results with team members
2. Reference previous reviews
3. Track review history over time
4. Include review outputs in PRs or documentation

## Goals

1. **Export reviews** to markdown files
2. **Configurable output** - choose format and destination
3. **Automatic naming** - timestamp and context-based filenames
4. **Non-intrusive** - opt-in, not default behaviour

## Non-Goals

- Database storage of reviews
- Review diffing or comparison tools
- Integration with external services (GitHub, Jira)

## Technical Approach

### Export Trigger

Add optional `scribe: on` parameter to review commands:

```
/summon-council
scribe: on

Design an authentication system...
```

### Output Location

Create `.parliament-of-chaos/` directory in project root:

```
.parliament-of-chaos/
  reviews/
    2025-12-04-auth-system-design.md
    2025-12-04-pr-review-123.md
```

### File Format

```markdown
# Parliament Review: [Task Summary]

**Date**: 2025-12-04 14:32
**Command**: /summon-council
**Duration**: ~5 minutes

## Task
[Original user request]

## Agents Consulted
- security-knight: Authentication design
- backend-goblin: Performance review
...

## Review Summary
[Grumpy reviewer feedback and iterations]

## Final Output
[The approved solution]

## Trade-offs
[Documented compromises]
```

### Commands to Update

| Command | Change |
|---------|--------|
| `/summon-council` | Add scribe parameter parsing, file export |
| `/parliament-review` | Add scribe parameter parsing, file export |
| `/summon-grumpy-reviewer` | Add scribe parameter parsing, file export |

## Acceptance Criteria

- [ ] `scribe: on` parameter recognised by review commands
- [ ] Reviews exported to `.parliament-of-chaos/reviews/`
- [ ] Filename includes date and task summary
- [ ] File contains all review sections (task, agents, summary, output, trade-offs)
- [ ] Export is opt-in (default: no export)
- [ ] Documentation updated

## Risks

| Risk | Mitigation |
|------|------------|
| Large files bloating repo | Add `.parliament-of-chaos/` to .gitignore suggestion |
| Filename collisions | Include timestamp with seconds |
| Sensitive data in exports | User discretion; warn in docs |

## Open Questions

1. Should there be a `/export-last-review` command for retroactive export?
2. JSON format option for programmatic consumption?
3. Should exports include the full conversation or just the summary?
