# Implement Task List

You are implementing a roadmap item's tasks using the **senior-council** orchestrator, which coordinates specialists and grumpy reviewers to ensure quality.

## Agent

**Delegated to: senior-council**

## Purpose

Systematically implement all tasks for a roadmap item with full Parliament oversight:
- Specialists handle implementation
- Grumpy reviewers validate quality
- Iterate until all reviewers approve

## Arguments

**Optional**: `<item-name>` - The roadmap item to implement

- If provided: Implement tasks for that specific item
- If omitted: Show available items with pending tasks and ask user to choose

Example:
- `/implement-task-list user-authentication`
- `/implement-task-list` (interactive selection)

## Process

### Phase 1: Safety & Planning (Task-Executor Role)

1. **Safety Check**:
   - Scan `.project-files/roadmap/*/work_complete.md`
   - Build "Do Not Break" list from previous work
   - Report potential overlaps to user

2. **Load Tasks**:
   - Read `.project-files/roadmap/<item>/tasks.md`
   - Read `.project-files/roadmap/<item>/Spec.md` for context
   - Identify task dependencies and execution order

### Phase 2: Council Orchestration (Senior-Council Role)

For each task:

1. **Analyse Task**: Determine relevant domains (backend, database, security, UI, etc.)

2. **Summon Specialists**: Invoke appropriate agents:
   | Domain | Agent |
   |--------|-------|
   | Architecture | system-architect |
   | Database | data-warlock |
   | API | api-keeper |
   | Security | security-knight |
   | Performance | backend-goblin |
   | Tests | test-prophet |
   | UI/UX | ui-ux-guru |
   | Docs | doc-bard |
   | Dependencies | package-wizard |
   | Resilience | resilience-tamer |
   | CI/CD | pipeline-engineer |

3. **Grumpy Review**: Route specialist output through ALL grumpy reviewers:
   - grumpy-code-reviewer
   - grumpy-standards-enforcer
   - grumpy-architecture-skeptic
   - grumpy-maintainability-curmudgeon
   - grumpy-security-nag
   - grumpy-performance-troll

4. **Iterate**: Address objections, re-route to specialists, repeat until grumps approve

5. **Mark Complete**: Update tasks.md after grumpy approval

### Phase 3: Documentation (Task-Executor Role)

Create `.project-files/roadmap/<item>/work_complete.md`:
- Summary of what was accomplished
- All files modified/created
- Agents consulted and review rounds
- Decisions made with trade-offs
- Follow-up items identified

## Pre-conditions

- `.project-files/roadmap/<item>/tasks.md` must exist
- Run `/roadmap-item-scope <item>` first if tasks.md is missing

## Error Handling

- **No tasks.md**: Suggest running `/roadmap-item-scope <item>` first
- **All tasks complete**: Inform user and show work_complete.md summary
- **Regression risk detected**: Stop and ask user how to proceed
- **Grumps won't approve**: Document trade-offs, get user decision

## Output

For each completed task:
1. **Task Summary** – What was implemented
2. **Agents Consulted** – Which specialists contributed
3. **Review Summary** – Grumpy objections raised and resolved
4. **Final Implementation** – Approved code/changes
5. **Trade-offs** – Any compromises made

## Safety Rules

1. Always perform safety check first
2. Never skip grumpy review for implementation tasks
3. Document all trade-offs when grumps disagree
4. Keep tasks atomic and reversible
5. Update tasks.md only after grumpy approval
