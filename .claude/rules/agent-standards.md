# Agent Frontmatter Standards

All Parliament of Chaos agents must include standardised frontmatter fields. This ensures consistent behaviour, cost optimisation, and proper resource allocation across the 30-agent fleet.

## Required Fields

Every agent must include:
- `name` — Unique identifier (kebab-case)
- `description` — One-line summary of the agent's role
- `model` — Model selection (`inherit` uses the parent session's model)
- `color` — Visual identifier for UI display
- `permissionMode` — Permission level (`default` for most agents)
- `effort` — Reasoning effort tier (see below)
- `maxTurns` — Maximum conversation turns before auto-stop

## Effort Tiers

Effort levels control reasoning depth and token cost. Assign based on agent role:

| Tier | Effort | Agents | Rationale |
|------|--------|--------|-----------|
| **High** | `effort: high` | Orchestrators (senior-council, deliberation-conductor) | Complex multi-agent coordination requiring deep reasoning |
| **Medium** | `effort: medium` | Specialists (16) and Planning agents (3) | Domain analysis, implementation, and scoping work |
| **Low** | `effort: low` | Grumpy reviewers (9) | Read-only critique with focused, concise output |

## maxTurns Guidelines

| Role | maxTurns | Rationale |
|------|----------|-----------|
| Orchestrators | 30 | Coordinate multiple specialists and reviewers across iterations |
| Planning agents | 20 | Interactive Q&A and scoping require extended dialogue |
| Specialists | 15 | Focused domain analysis and implementation |
| Grumpy reviewers | 5 | Concise critique: summary, issues, recommendations, verdict |

## Memory Scopes

| Scope | Agents | Purpose |
|-------|--------|---------|
| `memory: project` | Orchestrators, specialists, planning agents | Accumulate project-specific knowledge across sessions |
| `memory: user` | Grumpy reviewers | Accumulate review preferences and patterns across projects |

## Tool Restrictions

| Role | disallowedTools | Rationale |
|------|----------------|-----------|
| Grumpy reviewers | `[Edit, Write, NotebookEdit, Bash]` | Read-only: critique only, never modify code |
| system-architect | `[Edit, Write, NotebookEdit, Bash]` | Advisory: designs architecture, does not implement |
| All other specialists | None | Full tool access for implementation work |

## Isolation

| Field | Value | Agents | Purpose |
|-------|-------|--------|---------|
| `isolation: worktree` | Present | Implementation specialists | Work in isolated git branches without conflicts |
| Not present | — | Read-only agents, orchestrators | No isolation needed for analysis/coordination |

## Background Execution

| Field | Agents | Purpose |
|-------|--------|---------|
| `background: true` | Grumpy reviewers | Can run as background review tasks |

## Frontmatter Template

### Orchestrator
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: high
maxTurns: 30
tools:
  - Task(agent-name)
```

### Specialist (with implementation)
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: medium
maxTurns: 15
isolation: worktree
```

### Specialist (read-only advisory)
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: medium
maxTurns: 15
disallowedTools:
  - Edit
  - Write
  - NotebookEdit
  - Bash
```

### Grumpy Reviewer
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: user
background: true
effort: low
maxTurns: 5
disallowedTools:
  - Edit
  - Write
  - NotebookEdit
  - Bash
```

### Planning Agent
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: medium
maxTurns: 20
```
