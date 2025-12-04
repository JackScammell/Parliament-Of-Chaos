# Tasks: conflict-resolution

## Task List

### 1. Design conflict detection logic
- [ ] Define conflict patterns (contradiction, priority, scope)
- [ ] Create examples of each conflict type
- [ ] Document detection heuristics

**Depends on**: None
**Agents**: system-architect, grumpy-architecture-skeptic

---

### 2. Update senior-council.md with conflict protocol
- [ ] Add "Conflict Detection" section to responsibilities
- [ ] Add "Resolution Hierarchy" (clarify → trade-off → authority → escalate)
- [ ] Add conflict output format to Output section
- [ ] Keep within token optimization targets (<35 lines if possible)

**Depends on**: Task 1
**Agents**: doc-bard, scope-weaver

---

### 3. Update parliament-review.md conflict handling
- [ ] Enhance "Reviewer Notes" section with conflict structure
- [ ] Add conflict categorization to output format
- [ ] Document when to escalate vs. resolve

**Depends on**: Task 1
**Agents**: doc-bard

---

### 4. Update summon-council.md iteration loop
- [ ] Add conflict detection to step 5 (Iterate)
- [ ] Add resolution attempt before re-routing to specialists
- [ ] Add user escalation path for unresolvable conflicts

**Depends on**: Task 2
**Agents**: doc-bard, scope-weaver

---

### 5. Create conflict resolution examples
- [ ] Document 3 example conflicts with resolutions
- [ ] Add to usage.md or create dedicated doc
- [ ] Include real examples from previous reviews

**Depends on**: Tasks 2, 3, 4
**Agents**: doc-bard

---

### 6. Test with real conflict scenario
- [ ] Run `/parliament-review` on code with known trade-offs
- [ ] Verify conflicts are detected and categorized
- [ ] Verify resolution protocol is followed
- [ ] Document results

**Depends on**: Tasks 2, 3, 4
**Agents**: test-prophet, grumpy-testing-tyrant

---

### 7. Update README.md
- [ ] Add conflict resolution to "How It Works" section
- [ ] Update any agent descriptions if needed

**Depends on**: Task 6
**Agents**: doc-bard

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 7 |
| Files to modify | 4 (senior-council.md, parliament-review.md, summon-council.md, README.md) |
| Files to create | 0-1 (optional examples doc) |
| Complexity | Medium |
| Primary agents | doc-bard, scope-weaver, system-architect |

## Progress

- [x] Task 1: Design conflict detection logic (minimal approach after grumpy review)
- [x] Task 2: Update senior-council.md
- [x] Task 3: Update parliament-review.md
- [x] Task 4: Update summon-council.md
- [x] Task 5: Create examples
- [x] Task 6: Test with real scenario
- [x] Task 7: Update README.md

**Status**: Complete
