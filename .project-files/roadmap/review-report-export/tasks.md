# Tasks: review-report-export

## Task List

### 1. Define export file format
- [ ] Finalise markdown template structure
- [ ] Define filename convention (date-slug format)
- [ ] Document format in usage.md

**Depends on**: None
**Agents**: doc-bard

---

### 2. Update summon-council.md with scribe parameter
- [ ] Add scribe parameter documentation
- [ ] Add export instructions to output section
- [ ] Keep within token optimisation targets

**Depends on**: Task 1
**Agents**: doc-bard, scope-weaver

---

### 3. Update parliament-review.md with scribe parameter
- [ ] Add scribe parameter documentation
- [ ] Add export instructions to output section

**Depends on**: Task 1
**Agents**: doc-bard

---

### 4. Update summon-grumpy-reviewer.md with scribe parameter
- [ ] Add scribe parameter documentation
- [ ] Add export instructions to output section

**Depends on**: Task 1
**Agents**: doc-bard

---

### 5. Document .parliament-of-chaos directory structure
- [ ] Add section to usage.md explaining export location
- [ ] Suggest .gitignore addition
- [ ] Provide example exported file

**Depends on**: Tasks 2, 3, 4
**Agents**: doc-bard

---

### 6. Update README.md
- [ ] Add export feature to command descriptions
- [ ] Mention scribe parameter in "How It Works"

**Depends on**: Task 5
**Agents**: doc-bard

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 6 |
| Files to modify | 5 (3 commands, usage.md, README.md) |
| Complexity | Low-Medium |
| Primary agents | doc-bard |

## Progress

- [ ] Task 1: Define export file format
- [ ] Task 2: Update summon-council.md
- [ ] Task 3: Update parliament-review.md
- [ ] Task 4: Update summon-grumpy-reviewer.md
- [ ] Task 5: Document directory structure
- [ ] Task 6: Update README.md

**Status**: Not Started
