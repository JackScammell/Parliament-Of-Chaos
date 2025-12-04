# Project Status

Display a dashboard showing the current state of the project.

## Purpose

Provide a quick overview of project progress including roadmap items, task completion, and recent work.

## Arguments

None required. This command reads the `.project-files/` directory.

## Instructions

1. **Check for project files**:
   - If `.project-files/` does not exist, inform user to run `/plan-project` first

2. **Read project overview**:
   - Parse `.project-files/project-outline.md` for project name and summary
   - Parse `.project-files/Roadmap.md` for roadmap items

3. **Scan roadmap items**:
   For each item in `.project-files/roadmap/`:
   - Check if `Spec.md` exists (scoped)
   - Check if `tasks.md` exists and count completed/pending tasks
   - Check if `work_complete.md` exists (done)

4. **Generate status report**:

```markdown
# Project Status: [Project Name]

## Overview
[Brief project description from project-outline.md]

## Roadmap Progress

| Item | Status | Tasks | Last Updated |
|------|--------|-------|--------------|
| [item-1] | Complete | 5/5 | 2025-01-15 |
| [item-2] | In Progress | 3/8 | 2025-01-14 |
| [item-3] | Scoped | 0/6 | - |
| [item-4] | Not Started | - | - |

## Summary
- **Total Items**: 4
- **Completed**: 1 (25%)
- **In Progress**: 1 (25%)
- **Scoped**: 1 (25%)
- **Not Started**: 1 (25%)

## Recent Activity
- [timestamp] Completed: [item-1]
- [timestamp] Tasks completed in [item-2]: 3

## Next Actions
- Continue work on: [item-2] (3 tasks remaining)
- Ready to scope: [item-4]
- Ready to implement: [item-3]
```

## Status Definitions

| Status | Meaning |
|--------|---------|
| **Not Started** | Listed in Roadmap.md but no folder in roadmap/ |
| **Scoped** | Has Spec.md and tasks.md but no tasks completed |
| **In Progress** | Has some tasks marked complete in tasks.md |
| **Complete** | Has work_complete.md |

## Output

Display the status report directly - do not create any files.

## Error Handling

- **No .project-files/**: "No project found. Run `/plan-project` to get started."
- **No Roadmap.md**: "Project exists but no roadmap. Run `/plan-project` to create one."
- **Parsing errors**: Report which file had issues, continue with available data
