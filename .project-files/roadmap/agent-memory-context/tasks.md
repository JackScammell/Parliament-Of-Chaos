# Tasks: agent-memory-context

## Task List

### 1. Design context file format
- [ ] Define `.parliament-of-chaos/context.md` structure
- [ ] Establish sections (decisions, preferences, etc.)
- [ ] Set size limits and pruning rules

**Depends on**: None
**Agents**: system-architect, doc-bard

---

### 2. Update senior-council.md with context loading
- [ ] Add context loading step to responsibilities
- [ ] Reference project-outline.md and work_complete.md
- [ ] Keep additions minimal

**Depends on**: Task 1
**Agents**: doc-bard, scope-weaver

---

### 3. Update summon-council.md with remember parameter
- [ ] Add `remember:` parameter documentation
- [ ] Explain how flagged decisions are stored

**Depends on**: Task 2
**Agents**: doc-bard

---

### 4. Create /remember command
- [ ] Create `.claude/commands/parliament-of-chaos/remember.md`
- [ ] Append user decision to context.md
- [ ] Include timestamp

**Depends on**: Task 1
**Agents**: doc-bard

---

### 5. Create /forget command
- [ ] Create `.claude/commands/parliament-of-chaos/forget.md`
- [ ] Remove specified decision from context.md
- [ ] Confirm removal to user

**Depends on**: Task 4
**Agents**: doc-bard

---

### 6. Update implement-task-list.md with context awareness
- [ ] Reference previous work_complete.md files
- [ ] Use context when making implementation decisions

**Depends on**: Task 2
**Agents**: doc-bard

---

### 7. Document memory system in usage.md
- [ ] Explain context loading
- [ ] Document /remember and /forget commands
- [ ] Provide examples

**Depends on**: Tasks 4, 5, 6
**Agents**: doc-bard

---

### 8. Update README.md
- [ ] Add memory/context feature description
- [ ] Update command count (12 → 14)
- [ ] Add /remember and /forget to command tables

**Depends on**: Task 7
**Agents**: doc-bard

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 8 |
| Files to modify | 4 (senior-council.md, summon-council.md, implement-task-list.md, usage.md, README.md) |
| Files to create | 2 (/remember.md, /forget.md commands) |
| Complexity | Medium-High |
| Primary agents | doc-bard, scope-weaver |

## Progress

- [ ] Task 1: Design context file format
- [ ] Task 2: Update senior-council.md
- [ ] Task 3: Update summon-council.md
- [ ] Task 4: Create /remember command
- [ ] Task 5: Create /forget command
- [ ] Task 6: Update implement-task-list.md
- [ ] Task 7: Document in usage.md
- [ ] Task 8: Update README.md

**Status**: Not Started
