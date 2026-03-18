---
description: Set up recurring Parliament monitoring using /loop integration
---

# Parliament Loop

Set up recurring execution of Parliament commands on an interval using Claude Code's `/loop` command (v2.1.71+).

## Usage

```
/parliament-loop [interval] [command] [args]
```

**Examples**:
```
/parliament-loop 5m /project-status
/parliament-loop 10m /parliament-review
/parliament-loop 15m /summon-grumpy-reviewer
```

## Process

1. **Validate the command**: Ensure the target command is a valid Parliament command
2. **Set up the loop**: Invoke Claude Code's `/loop` with the specified interval and command
3. **Confirm activation**: Display the loop configuration

## Available Commands for Looping

| Command | Recommended Interval | Use Case |
|---------|---------------------|----------|
| `/project-status` | 5-10m | Monitor roadmap progress during implementation |
| `/parliament-review` | 15-30m | Periodic code review during active development |
| `/summon-grumpy-reviewer` | 10-15m | Continuous quality checks |
| `/debate-analytics` | 30m | Track deliberation patterns |

## Output

```markdown
# Parliament Loop Configured

**Command**: /project-status
**Interval**: Every 5 minutes
**Status**: Active

Use `/loop stop` to disable recurring execution.
```

## Integration

This command wraps Claude Code's native `/loop` functionality specifically for Parliament commands. It:

1. Validates the target is a Parliament command
2. Suggests appropriate intervals based on the command type
3. Delegates to `/loop [interval] /chaos:[command]`

## Notes

- Requires Claude Code v2.1.71+ for `/loop` support
- The `/loop` command runs within the current session — it stops when the session ends
- For persistent recurring tasks across sessions, consider using Claude Code's cron scheduling tools
- Heavy commands like `/parliament-review` should use longer intervals (15m+) to manage token usage
- Use `/loop stop` to cancel the recurring execution
