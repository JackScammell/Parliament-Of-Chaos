# Summon Specialist

Directly invoke a specialist agent on the current task.

**Argument**: Specialist name (e.g., `security-knight`)

## Valid Specialists

api-keeper, backend-goblin, config-curator, data-warlock, dependency-detective, doc-bard, migration-monk, observability-oracle, package-wizard, pipeline-engineer, refactor-ranger, resilience-tamer, security-knight, system-architect, test-prophet, ui-ux-guru

## Process

1. Validate $ARGUMENTS is a valid specialist (not grumpy-*, orchestrator, or planner)
2. Load the specialist's prompt
3. Execute as that specialist on the user's current task/context
4. Provide specialist-style output

## Validation

**Reject if**:
- Agent is grumpy-* (use `/parliament-review` instead)
- Agent is senior-council (use `/summon-council` instead)
- Agent is planner (project-oracle, scope-weaver, task-executor)
- Agent does not exist

**On rejection**: Explain why and suggest correct command.

## Output

Specialist-formatted response per the agent's defined output structure.
