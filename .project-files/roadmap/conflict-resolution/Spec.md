# Specification: conflict-resolution

## Overview

**Item**: conflict-resolution
**Phase**: 4 (Quality of Life Features)
**Dependencies**: senior-council agent (exists)

## Problem Statement

When multiple grumpy reviewers disagree on an issue, the current system has no structured way to:
1. Identify genuine conflicts vs. complementary concerns
2. Weigh competing trade-offs (e.g., performance vs. maintainability)
3. Reach a documented resolution
4. Escalate to the user when consensus is impossible

Currently, the senior-council agent says "iterate until all approve or trade-offs documented" but provides no specific protocol for handling disagreements.

## Goals

1. **Detect conflicts** - Identify when reviewers have opposing recommendations
2. **Categorize conflicts** - Distinguish between:
   - Genuine trade-offs (both valid, pick one)
   - Misunderstandings (clarification resolves it)
   - Scope disagreements (one reviewer overreaching)
3. **Resolution protocol** - Structured process to resolve or escalate
4. **Documentation** - Record decisions for future reference

## Non-Goals

- Automatic conflict resolution without user awareness
- Removing any grumpy reviewer's voice
- Voting systems that silence minority concerns

## Technical Approach

### Conflict Detection

Conflicts occur when reviewers recommend mutually exclusive actions:

| Conflict Type | Example |
|---------------|---------|
| **Direct contradiction** | Security says "add input validation", Performance says "remove validation overhead" |
| **Priority disagreement** | Architecture says "refactor first", Code Reviewer says "ship now, refactor later" |
| **Scope creep** | Documentation Pedant requests changes outside the PR scope |

### Resolution Hierarchy

1. **Clarification round** - Ask conflicting reviewers to explain rationale
2. **Trade-off analysis** - Document pros/cons of each position
3. **Domain authority** - Defer to domain expert (security issues → security-knight)
4. **User escalation** - Present options to user with recommendations

### Integration Points

| Component | Change Required |
|-----------|-----------------|
| `senior-council.md` | Add conflict detection and resolution protocol |
| `parliament-review.md` | Add "Reviewer Notes" section for conflicts |
| `summon-council.md` | Add conflict handling to iteration loop |

### Output Format

When conflicts are detected, output should include:

```markdown
## Conflict Resolution

### Conflict 1: [Title]
**Between**: [reviewer-a] vs [reviewer-b]
**Issue**: [description]
**Resolution**: [chosen approach]
**Rationale**: [why this was chosen]
**Trade-off accepted**: [what was sacrificed]
```

## Acceptance Criteria

- [ ] Conflicts between reviewers are automatically detected
- [ ] Each conflict is categorized (contradiction, priority, scope)
- [ ] Resolution protocol is documented and followed
- [ ] User is presented with trade-offs for genuine conflicts
- [ ] Conflict resolutions are recorded in output
- [ ] senior-council.md updated with conflict handling
- [ ] Documentation updated to explain conflict resolution

## Risks

| Risk | Mitigation |
|------|------------|
| Over-engineering simple disagreements | Start with manual detection, automate later |
| User fatigue from too many conflicts | Aggregate related conflicts, summarize |
| Grumpy reviewers gaming the system | Document expected behavior in agent prompts |

## Related Work

- `parliament-review.md` already has "Reviewer Notes: Notable disagreements or trade-offs"
- `senior-council.md` mentions "trade-offs documented" but lacks protocol
- Previous parliament review showed real conflicts (performance vs thoroughness)

## Open Questions

1. Should conflicts be weighted by severity? (Critical security > Low performance)
2. Should there be a "tiebreaker" agent or always escalate to user?
3. How verbose should conflict documentation be?
