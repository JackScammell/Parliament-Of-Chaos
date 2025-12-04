# Implement Task List

You are executing a task list using the **task-executor** agent.

## Purpose

Systematically implement all tasks for a roadmap item while ensuring previous work is not broken.

## Arguments

**Optional**: `<item-name>` - The roadmap item to implement

- If provided: Implement tasks for that specific item
- If omitted: Show available items with pending tasks and ask user to choose

Example:
- `/implement-task-list user-authentication`
- `/implement-task-list` (interactive selection)

## Instructions

### Step 1: Safety Check (MANDATORY)

Before any implementation:

1. **Find all completed work**:
   - Scan `.project-files/roadmap/*/work_complete.md`
   - Extract files modified, components affected, and integration points

2. **Build "Do Not Break" list**:
   - Critical files from previous work
   - APIs and interfaces other work depends on
   - Data structures that must remain compatible

3. **Report to user**:
   - Number of completed roadmap items found
   - Key areas that must be preserved
   - Any potential overlap with current tasks

### Step 2: Load Tasks

1. Read `.project-files/roadmap/<item>/tasks.md`
2. Read `.project-files/roadmap/<item>/Spec.md` for context
3. Count pending vs completed tasks
4. Identify any task dependencies

### Step 3: Execute Tasks

For each uncompleted task:

1. Announce what you are about to do
2. Check if it affects any "Do Not Break" items
3. Execute the implementation
4. Verify completion
5. Mark task as done in tasks.md
6. Document what was changed

### Step 4: Generate Completion Report

Create `.project-files/roadmap/<item>/work_complete.md` containing:
- Summary of what was accomplished
- All files modified/created
- Decisions made and rationale
- Integration points established
- Regression checks performed
- Follow-up items identified

## Pre-conditions

- `.project-files/roadmap/<item>/tasks.md` must exist
- Run `/roadmap-item-scope <item>` first if tasks.md is missing

## Delegation

The task-executor may delegate specialized work to other Parliament agents:

| Task Type | Agent |
|-----------|-------|
| Architecture decisions | system-architect |
| Database changes | data-warlock |
| API design | api-keeper |
| Security concerns | security-knight |
| Performance work | backend-goblin |
| Test creation | test-prophet |
| Documentation | doc-bard |

## Error Handling

- **No tasks.md**: Suggest running `/roadmap-item-scope <item>` first
- **All tasks complete**: Inform user and show work_complete.md summary
- **Regression risk detected**: Stop and ask user how to proceed
- **Task blocked**: Report blocker, skip task, continue with others

## Safety Rules

1. Always perform the safety check first
2. Never skip documenting completed work
3. Stop and ask if you detect potential regressions
4. Keep tasks atomic and reversible
5. Update tasks.md after each task completion
