---
description: Audit agent definitions and recommend effort/model optimisation settings
---

# Parliament Optimize

Advisory command that audits all 30 agent definitions and recommends effort/model settings based on agent role. **Read-only** — does not modify any files.

## Process

1. Read all `agents/*.md` files
2. Extract frontmatter fields: `name`, `effort`, `maxTurns`, `memory`, `model`, `disallowedTools`, `isolation`, `background`
3. Classify each agent by role:
   - **Orchestrator**: has `tools` list with `Task()` entries
   - **Grumpy Reviewer**: name starts with `grumpy-`
   - **Planning Agent**: project-oracle, scope-weaver, task-executor
   - **Specialist**: all others
4. Read `.claude/rules/agent-standards.md` for the standard frontmatter requirements
5. Compare current frontmatter against standards and identify deviations

## Audit Checks

For each agent, verify:

| Field | Orchestrators | Specialists | Reviewers | Planning |
|-------|--------------|-------------|-----------|----------|
| effort | high | medium | low | medium |
| maxTurns | 30 | 15 | 5 | 20 |
| memory | project | project | user | project |
| disallowedTools | — | varies | required | — |
| isolation | — | worktree (impl) | — | — |
| background | — | — | true | — |

## Output

```markdown
# Parliament Agent Audit Report

## Summary
- Total agents: 30
- Compliant: N
- Non-compliant: N
- Warnings: N

## Compliance by Category

### Orchestrators (2)
| Agent | effort | maxTurns | memory | Status |
|-------|--------|----------|--------|--------|
| senior-council | high | 30 | project | OK |

### Specialists (16)
[table with status per agent]

### Grumpy Reviewers (9)
[table with status per agent]

### Planning Agents (3)
[table with status per agent]

## Recommendations
- [list of specific changes needed, if any]

## Cost Optimisation Estimate
- Current tier distribution: N high / N medium / N low
- Estimated token savings from effort tiers: ~40-60% on reviewer tasks
```

## Notes

- This command is advisory only — it reads and reports but never modifies agent files
- Run after adding new agents to verify they follow the standards in `.claude/rules/agent-standards.md`
- Use `/summon-specialist config-curator` if you want to apply recommended changes
