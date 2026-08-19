---
description: Manage background monitoring agents for continuous code oversight
effort: medium
argument-hint: "[action] [agents...]"
---

# Parliament Monitor

Manage background monitoring agents that provide continuous oversight of your codebase during development sessions.

## Usage

```
/parliament-monitor [action] [agents...]
```

**Actions**:
- `start` — Start background monitoring agents (default)
- `stop` — Stop running background agents
- `status` — Show which monitors are active
- `list` — List available monitoring agents

## Available Monitoring Agents

These agents have `background: true` in their frontmatter, enabling persistent background execution:

| Agent | Focus Area | Trigger |
|-------|-----------|---------|
| `grumpy-code-reviewer` | Code quality, readability | File changes |
| `grumpy-standards-enforcer` | Coding standards compliance | File changes |
| `grumpy-architecture-skeptic` | Architectural decisions | Structural changes |
| `grumpy-maintainability-curmudgeon` | Technical debt, maintainability | File changes |
| `grumpy-security-nag` | Security vulnerabilities | Security-sensitive changes |
| `grumpy-performance-troll` | Performance bottlenecks | Performance-sensitive changes |
| `grumpy-accessibility-auditor` | WCAG compliance | UI/UX changes |
| `grumpy-documentation-pedant` | Documentation completeness | Doc changes |
| `grumpy-testing-tyrant` | Test coverage gaps | Test/source changes |

## Process

### Start Monitors

1. **Select agents**: Use specified agents or default set
2. **Launch as background tasks**: Spawn each agent with `background: true` and `run_in_background: true`
3. **Configure monitoring scope**: Set agents to watch for relevant file changes
4. **Confirm activation**: Display list of active monitors

**Default set** (recommended for most projects):
- `grumpy-code-reviewer` — General quality
- `grumpy-security-nag` — Security oversight
- `grumpy-testing-tyrant` — Test coverage

**Full set** (`/parliament-monitor start --all`):
- All 9 grumpy reviewers

### Stop Monitors

1. Use Ctrl+F (two-press) to kill background agents
2. Or specify agents: `/parliament-monitor stop grumpy-security-nag`

### Status

Display currently active background monitoring agents and their last activity.

## Output

### Start
```markdown
# Parliament Monitors Active

**Active Monitors**: 3/9

| Agent | Status | Focus |
|-------|--------|-------|
| grumpy-code-reviewer | Running | Code quality |
| grumpy-security-nag | Running | Security |
| grumpy-testing-tyrant | Running | Test coverage |

Monitors will review changes as you work. Use Ctrl+F to stop all.
```

### Status
```markdown
# Monitor Status

| Agent | Status | Last Activity |
|-------|--------|--------------|
| grumpy-code-reviewer | Running | 2m ago |
| grumpy-security-nag | Idle | 5m ago |
| grumpy-testing-tyrant | Running | 1m ago |
```

## Notes

- Background agents use `effort: low` and `maxTurns: 5` for minimal resource consumption
- All monitoring agents are read-only (`disallowedTools: [Edit, Write, NotebookEdit, Bash]`)
- Monitors leverage the `TeammateIdle` and `TaskCompleted` hooks for event tracking
- Use `StopFailure` hook to detect and recover from API failures during monitoring
- Ctrl+C or Ctrl+F (two-press within 3s) kills all background agents
- Requires Claude Code v2.1.49+ for `background: true` agent support
- **Claude Code v2.1.140+**: when a background monitor is driven on an interval via `/parliament-loop`, `/loop` no longer redundantly wakes for a self-notifying background task — the monitor's own completion signal drives cadence, not the loop tick. Size the loop interval as a staleness ceiling, not an exact polling period. See `/parliament-loop` Notes for the full behaviour.
