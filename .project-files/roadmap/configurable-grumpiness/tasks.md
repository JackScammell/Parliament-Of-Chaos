# Tasks: configurable-grumpiness

## Task List

### 1. Define grumpiness level semantics
- [ ] Finalise 3-level system (strict/moderate/lenient)
- [ ] Document what each level means for issue handling
- [ ] Create behaviour matrix (level x severity)

**Depends on**: None
**Agents**: system-architect, doc-bard

---

### 2. Update grumpy reviewer agents (all 9)
- [ ] Add grumpiness level handling to each grumpy-*.md
- [ ] Keep additions minimal (~3 lines each)
- [ ] Ensure consistent interpretation across all reviewers

**Depends on**: Task 1
**Agents**: doc-bard

Files:
- grumpy-code-reviewer.md
- grumpy-standards-enforcer.md
- grumpy-architecture-skeptic.md
- grumpy-maintainability-curmudgeon.md
- grumpy-security-nag.md
- grumpy-performance-troll.md
- grumpy-accessibility-auditor.md
- grumpy-documentation-pedant.md
- grumpy-testing-tyrant.md

---

### 3. Update summon-council.md
- [ ] Add grumpiness parameter documentation
- [ ] Pass level to grumpy review step

**Depends on**: Task 2
**Agents**: doc-bard

---

### 4. Update parliament-review.md
- [ ] Add grumpiness parameter documentation
- [ ] Adjust output format for non-strict levels

**Depends on**: Task 2
**Agents**: doc-bard

---

### 5. Update summon-grumpy-reviewer.md
- [ ] Add grumpiness parameter documentation

**Depends on**: Task 2
**Agents**: doc-bard

---

### 6. Document in usage.md
- [ ] Add grumpiness section explaining levels
- [ ] Provide examples for each level
- [ ] Explain when to use each

**Depends on**: Tasks 3, 4, 5
**Agents**: doc-bard

---

### 7. Update README.md
- [ ] Add grumpiness option to command descriptions
- [ ] Brief mention in "How It Works"

**Depends on**: Task 6
**Agents**: doc-bard

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 7 |
| Files to modify | 13 (9 agents, 3 commands, README.md) |
| Files to create | 0 |
| Complexity | Medium |
| Primary agents | doc-bard |

## Progress

- [ ] Task 1: Define grumpiness level semantics
- [ ] Task 2: Update grumpy reviewer agents (all 9)
- [ ] Task 3: Update summon-council.md
- [ ] Task 4: Update parliament-review.md
- [ ] Task 5: Update summon-grumpy-reviewer.md
- [ ] Task 6: Document in usage.md
- [ ] Task 7: Update README.md

**Status**: Not Started
