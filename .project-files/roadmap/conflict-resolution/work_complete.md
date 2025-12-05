# Complete: conflict-resolution

**Completed**: 2025-12-04

## Summary

Added conflict resolution protocol to the Parliament of Chaos review system. When grumpy reviewers disagree, conflicts are now resolved using a priority hierarchy. Out-of-scope recommendations are deferred rather than blocking approval.

## Results

| Metric | Value |
|--------|-------|
| Design approach | Minimal (per grumpy reviewer feedback) |
| Lines added | ~10 across 4 files |
| Token impact | Negligible |
| Grumpy approvals | 2/2 (after revision) |

## Tasks Done

- [x] Design conflict detection logic (minimal approach chosen after grumpy review)
- [x] Update senior-council.md with conflict resolution responsibility
- [x] Update parliament-review.md with Deferred output section
- [x] Update summon-council.md with conflict priority in iteration step
- [x] Create conflict resolution examples in usage.md
- [x] Test with real conflict scenario (validated in earlier parliament-review)
- [x] Update README.md with conflict resolution note

## Files Changed

### Modified
| File | Change | Lines |
|------|--------|-------|
| `.claude/agents/parliament-of-chaos/senior-council.md` | Added Conflict Resolution responsibility | +1 |
| `.claude/commands/parliament-of-chaos/parliament-review.md` | Added Deferred output section | +3 |
| `.claude/commands/parliament-of-chaos/summon-council.md` | Added conflict priority to Iterate step | +0 (inline) |
| `docs/usage.md` | Added Conflict Resolution section with example | +12 |
| `README.md` | Added conflict note to Council Workflow | +0 (inline) |

### Created
| File | Purpose |
|------|---------|
| `.project-files/roadmap/conflict-resolution/Spec.md` | Detailed specification |
| `.project-files/roadmap/conflict-resolution/tasks.md` | Task breakdown |
| `.project-files/roadmap/conflict-resolution/work_complete.md` | This file |

## Decisions

### 1. Minimal Design Chosen

**Original proposal**: ~25 lines, 4-step process, 9-level authority mapping

**Grumpy feedback**:
- Architecture Skeptic: "Fixed hierarchy is context-blind; over-engineered"
- Maintainability Curmudgeon: "Adds complexity after token optimization; will drift"

**Final design**: ~5 lines total
- Single priority line: `security > correctness > maintainability > performance > convenience`
- Scope handling: Defer out-of-scope items, don't block
- User escalation for genuine trade-offs

### 2. Priority Order

Chosen hierarchy: **security > correctness > maintainability > performance > convenience**

Rationale:
- Security vulnerabilities are existential risks
- Incorrect code invalidates everything else
- Maintainability enables future security/correctness fixes
- Performance matters but premature optimization is waste
- Convenience is lowest priority

### 3. Deferred Section

Added explicit "Deferred" output section to `parliament-review.md` for out-of-scope recommendations. This prevents scope creep from blocking reviews while still logging valid concerns for future work.

## Trade-offs Accepted

| Trade-off | Rationale |
|-----------|-----------|
| No domain authority mapping | Simpler; user decides genuine conflicts |
| No conflict categorization | Over-engineering for current needs |
| Single priority line vs. protocol | Maintainability over comprehensiveness |

## Agents Consulted

| Agent | Contribution |
|-------|--------------|
| system-architect | Initial conflict detection design |
| grumpy-architecture-skeptic | Rejected fixed hierarchy as context-blind |
| grumpy-maintainability-curmudgeon | Rejected complexity, recommended minimal approach |
| grumpy-code-reviewer | Approved final senior-council.md change |
| grumpy-standards-enforcer | Caught priority inconsistency (4 vs 5 levels) |

## Follow-up Items

- Consider adding conflict weighting by severity in future (Critical security > Low performance)
- Monitor if "Deferred" section is actually used
- Could add `/explain-conflict` command if users want more detail
