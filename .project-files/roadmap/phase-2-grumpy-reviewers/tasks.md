# Tasks: Phase 2 - New Grumpy Reviewers

## Status: Complete

## Overview

Create 3 new grumpy reviewer agents, update senior-council and README.

**Completed**: 2024-12-04
**Dependencies**: None (Phase 0 and Phase 1 complete)

---

## Tasks

### Agent Creation

- [x] **Create grumpy-accessibility-auditor.md** (32 lines)
  - Path: `.claude/agents/parliament-of-chaos/grumpy-accessibility-auditor.md`
  - Color: cyan
  - Focus: WCAG compliance, ARIA, keyboard nav, color contrast, screen readers

- [x] **Create grumpy-documentation-pedant.md** (32 lines)
  - Path: `.claude/agents/parliament-of-chaos/grumpy-documentation-pedant.md`
  - Color: white
  - Focus: Missing docs, outdated comments, unclear READMEs, API docs

- [x] **Create grumpy-testing-tyrant.md** (32 lines)
  - Path: `.claude/agents/parliament-of-chaos/grumpy-testing-tyrant.md`
  - Color: brightBlue
  - Focus: Coverage gaps, weak assertions, flaky tests, missing edge cases

### Integration

- [x] **Update senior-council.md grumpy reviewer list**
  - Added: grumpy-accessibility-auditor, grumpy-documentation-pedant, grumpy-testing-tyrant
  - Now lists 9 grumpy reviewers

- [x] **Update README.md grumpy reviewer count**
  - Changed "6 Grumpy Reviewers" to "9 Grumpy Reviewers"
  - Changed "26 Agents" to "29 Agents"
  - Added 3 new rows to Grumpy Reviewers table

### Verification

- [x] **Verify line counts**
  - All 9 grumpy reviewers at exactly 32 lines

- [x] **Verify structure consistency**
  - Each agent has: YAML frontmatter, Focus Areas, Process, Output sections
  - Output follows: Summary, Issues/Violations, Recommendations, Verdict pattern

- [x] **Verify color uniqueness**
  - cyan, white, brightBlue - all unique, no conflicts

---

## Definition of Done

1. All 3 agent files created and line-count verified ✓
2. senior-council.md lists 9 grumpy reviewers ✓
3. README.md shows "9 Grumpy Reviewers" ✓
4. README.md Grumpy Reviewers table has 9 rows ✓
5. All colors are unique ✓
