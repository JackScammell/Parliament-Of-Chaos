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
| **Reserved** | `effort: xhigh` | _(none currently)_ | Opus 4.7 tier sitting between `high` and `max` (Claude Code v2.1.111). Reserved for future deliberation-conductor deep-mode runs if measurements justify the extra cost. Do not adopt without before/after benchmarks. |
| **High** | `effort: high` | Orchestrators (senior-council, deliberation-conductor) | Complex multi-agent coordination requiring deep reasoning |
| **Medium** | `effort: medium` | Specialists (16) and Planning agents (3) | Domain analysis, implementation, and scoping work |
| **Low** | `effort: low` | Grumpy reviewers (9) | Read-only critique with focused, concise output |

> **Note**: As of Claude Code v2.1.94 the global default `effort` is `high` (previously `medium`). Parliament sets `effort` explicitly on every agent, so this default never applies — but new contributors reading upstream docs should be aware the implicit fallback changed.

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

> **MCP inheritance (v2.1.101)**: Subagents now inherit MCP tools from the parent session automatically. Parliament specialists no longer need to re-declare MCP servers; any MCP tool available to the user is available to spawned agents unless explicitly listed in `disallowedTools`. Sandboxed subagents also now resolve worktree paths correctly.

## Isolation

| Field | Value | Agents | Purpose |
|-------|-------|--------|---------|
| `isolation: worktree` | Present | Implementation specialists | Work in isolated git branches without conflicts |
| Not present | — | Read-only agents, orchestrators | No isolation needed for analysis/coordination |

## Background Execution

| Field | Agents | Purpose |
|-------|--------|---------|
| `background: true` | Grumpy reviewers | Can run as background review tasks |

## Initial Prompts

| Field | Agents | Purpose |
|-------|--------|---------|
| `initialPrompt` | Planning agents (project-oracle, scope-weaver) | Auto-submit a first turn to start the interview/scoping workflow. Only for agents that drive conversation without needing input first. Not for orchestrators that react to a topic. |

## Effort for Slash Commands

Skills and slash commands also support `effort` frontmatter (since Claude Code v2.1.80). Assign based on command complexity:

| Tier | Effort | Commands | Rationale |
|------|--------|----------|-----------|
| **High** | `effort: high` | summon-council, debate-topic, parliament-review, implement-task-list | Multi-agent orchestration spawning multiple specialists and reviewers |
| **Medium** | `effort: medium` | plan-project, changelog-review, security-scan, summon-specialist, etc. (17 total) | Single-domain analysis, planning, or scoped implementation work |
| **Low** | `effort: low` | list-agents, version, readme, format-code, run-tests, etc. (13 total) | Simple display, single-tool execution, or delegating to an external tool |

## Plugin State Storage

Parliament maintains two distinct storage locations:

| Location | Contents | Lifecycle |
|----------|----------|-----------|
| `${CLAUDE_PLUGIN_DATA}/` | Plugin telemetry, logs, analytics, review state | Survives plugin updates, owned by the plugin |
| `.project-files/` | User-facing project artifacts (roadmaps, specs, outlines) | Owned by the user, lives with the project |

These are separate concerns. Never mix machine-generated telemetry with user-curated documents.

Hook scripts use a shared helper (`src/hooks/_common.sh`) that resolves the data directory with a fallback for older Claude Code versions where `CLAUDE_PLUGIN_DATA` is not set:

```bash
HOOK_DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOOK_PROJECT_DIR/.project-files/.telemetry}"
```

The fallback writes to `.project-files/.telemetry/` (not the `.project-files/` root) to maintain separation from user planning data.

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
