# Tasks: Phase 3 - New Commands + Command Optimization

## Status: Complete

## Overview

- **Total Tasks**: 14
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Phase 2 (grumpy reviewers) - COMPLETE

---

## Command Optimization (2 tasks)

### Optimize Existing Commands

- [x] **Optimize summon-grumpy-reviewer.md**
  - Current: 58 lines
  - Target: ~28 lines (~52% reduction)
  - Apply: Remove verbose preambles, consolidate angle lists, trust agent behavior
  - Test: Run command and verify output quality matches original
  - File: `.claude/commands/parliament-of-chaos/summon-grumpy-reviewer.md`

- [x] **Optimize summon-council.md**
  - Current: 89 lines
  - Target: ~35 lines (~61% reduction)
  - Apply: Reference agents instead of listing, consolidate process steps
  - Test: Run command and verify orchestration works
  - File: `.claude/commands/parliament-of-chaos/summon-council.md`

---

## New Command Creation (8 tasks)

### cmd-list-agents

- [x] **Create list-agents.md command**
  - Target: 25-30 lines
  - Behavior: List all agents grouped by category
  - Output: Formatted table with name and description
  - File: `.claude/commands/parliament-of-chaos/list-agents.md`

- [x] **Test list-agents command**
  - Verify all 29 agents appear
  - Verify grouping (Specialists, Grumpy, Orchestrators)
  - Verify descriptions extracted correctly

### cmd-explain-agent

- [x] **Create explain-agent.md command**
  - Target: 25-30 lines
  - Argument: Agent name via $ARGUMENTS
  - Behavior: Extract and present agent details
  - Handle: Invalid/missing agent names
  - File: `.claude/commands/parliament-of-chaos/explain-agent.md`

- [x] **Test explain-agent command**
  - Test with valid agent (e.g., `security-knight`)
  - Test with invalid agent name
  - Verify output includes focus areas and when to use

### cmd-summon-specialist

- [x] **Create summon-specialist.md command**
  - Target: 30-35 lines
  - Argument: Specialist name via $ARGUMENTS
  - Validation: Must be specialist (not grumpy-*, orchestrator)
  - Behavior: Load agent and execute on current task
  - File: `.claude/commands/parliament-of-chaos/summon-specialist.md`

- [x] **Test summon-specialist command**
  - Test with valid specialist (e.g., `api-keeper`)
  - Test with grumpy agent (should reject)
  - Test with invalid name (should error)

### cmd-parliament-review

- [x] **Create parliament-review.md command**
  - Target: 30-35 lines
  - Behavior: Run all 9 grumpy reviewers on target
  - Output: Severity-ranked issue list
  - File: `.claude/commands/parliament-of-chaos/parliament-review.md`

- [x] **Test parliament-review command**
  - Run on sample code/file
  - Verify all 9 reviewers contribute
  - Verify output format (severity-ranked)

---

## Documentation (3 tasks)

- [x] **Update README.md**
  - Add new commands section or update existing
  - Document command usage and arguments
  - Update any command counts

- [x] **Update Roadmap.md**
  - Mark 4 Phase 3 items as Complete
  - Update overall progress counter
  - Add change log entry

- [x] **Create work_complete.md**
  - Document results (line savings, task summary)
  - List files changed
  - Note any decisions made

---

## Verification (1 task)

- [x] **Final verification**
  - All 6 commands in `.claude/commands/parliament-of-chaos/` work
  - Total command lines reduced from 147 to ~120 (~18% overall)
  - New commands follow 30-35 line guideline
  - No regressions in existing functionality

---

## Task Order

Recommended execution order:

1. **Optimization first** - summon-grumpy-reviewer, summon-council
2. **Simple commands** - list-agents, explain-agent
3. **Complex commands** - summon-specialist, parliament-review
4. **Documentation** - README, Roadmap, work_complete
5. **Verification** - Final testing

---

## Notes

- `cmd-roadmap-add-item` already complete (skip)
- Parliament-review can now use all 9 grumpy reviewers (Phase 2 done)
- Test each command after creation before moving on
- Optimization: preserve behavior, reduce tokens
- New commands: follow patterns from optimized commands
