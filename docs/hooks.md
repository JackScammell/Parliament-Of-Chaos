# Hooks Configuration Guide

This guide explains how to set up Claude Code hooks to extend the Parliament of Chaos system with automated actions.

## Overview

Hooks are scripts that Claude Code executes automatically when certain events occur during your session. They enable:

- Notifications when Claude is waiting for input
- Alerts when tasks complete
- Custom automation workflows
- Integration with external services (Slack, Teams, etc.)

---

## Configuration File Locations

Claude Code supports hooks configuration at three levels, each serving different purposes:

### Project-Level (Shared)

```
.claude/settings.json
```

- **Purpose**: Hooks shared with the entire team
- **Version Control**: Committed to the repository
- **Use Case**: Standard team workflows, shared notifications

### Project-Level (Local)

```
.claude/settings.local.json
```

- **Purpose**: Personal hooks for this project only
- **Version Control**: Automatically gitignored
- **Use Case**: Personal notification preferences, local testing

### User-Level (Global)

```
~/.claude/settings.json
```

- **Purpose**: Hooks that apply to all your Claude Code projects
- **Version Control**: Not in any repository
- **Use Case**: Personal preferences across all projects

### Precedence

When the same hook event is configured at multiple levels, hooks from all levels are executed. User-level hooks run first, then project-level shared, then project-level local.

---

## Hook Configuration Structure

Hooks are configured in the `hooks` section of your settings file:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "optional_matcher_pattern",
        "hooks": [
          {
            "type": "command",
            "command": "path/to/script.sh"
          }
        ]
      }
    ]
  }
}
```

### Available Hook Events

| Event | Trigger | Common Uses |
|-------|---------|-------------|
| `Notification` | Claude displays a notification | Alert when waiting for input |
| `Stop` | Claude stops executing | Alert when task completes |
| `PreToolUse` | Before a tool is executed | Validation, logging |
| `PostToolUse` | After a tool completes | Auditing, notifications |

### Matcher Patterns

Matchers filter which specific events trigger the hook:

| Matcher | Event | Description |
|---------|-------|-------------|
| `idle_prompt` | Notification | Claude is waiting for user input |
| `Bash` | PreToolUse/PostToolUse | Before/after bash commands |
| `Write` | PreToolUse/PostToolUse | Before/after file writes |
| `Edit` | PreToolUse/PostToolUse | Before/after file edits |

---

## Example: Teams Notification Hook

Parliament of Chaos includes a ready-to-use Microsoft Teams notification hook. Here's how to set it up:

### Step 1: Configure the Webhook URL

Edit `.claude/hooks/.env`:

```bash
TEAMS_WEBHOOK_URL="https://your-org.webhook.office.com/webhookb2/..."
APP_NAME="My Project"
```

### Step 2: Configure the Hook

Add to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/notify_teams.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/notify_teams.sh"
          }
        ]
      }
    ]
  }
}
```

### How It Works

1. When Claude waits for input or completes a task, the hook fires
2. The script reads the event payload from stdin (JSON format)
3. It formats and sends a message to your Teams channel
4. If `TEAMS_WEBHOOK_URL` is not set, the script exits silently

---

## Writing Custom Hook Scripts

### Hook Payload

Claude passes event data to your script via stdin as JSON:

```json
{
  "hook_event_name": "Notification",
  "cwd": "/path/to/project",
  "session_id": "abc123"
}
```

### Environment Variables

These variables are available in hook scripts:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Path to the project directory |
| `TEAMS_WEBHOOK_URL` | (If configured) Teams webhook URL |
| `APP_NAME` | (If configured) Application identifier |

### Example: Debug Hook Script

A simple hook that logs all events for debugging:

```bash
#!/usr/bin/env sh
set -eu

LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/hook_debug.log"

{
  echo "====== HOOK RUN at $(date) ======"
  echo "Event payload:"
  cat
  echo
  echo "Environment:"
  echo "CLAUDE_PROJECT_DIR=${CLAUDE_PROJECT_DIR:-<unset>}"
  echo "PWD=$(pwd)"
  echo "================================="
  echo
} >> "$LOG_FILE" 2>&1

exit 0
```

Save this to `.claude/hooks/debug_hook.sh` and make it executable:

```bash
chmod +x .claude/hooks/debug_hook.sh
```

### Example: Slack Notification Hook

```bash
#!/usr/bin/env bash
set -euo pipefail

SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
[ -z "$SLACK_WEBHOOK_URL" ] && exit 0

HOOK_JSON="$(cat)"

if command -v jq >/dev/null 2>&1; then
  EVENT="$(printf '%s' "$HOOK_JSON" | jq -r '.hook_event_name // "Unknown"')"
  PROJECT="$(printf '%s' "$HOOK_JSON" | jq -r '.cwd // ""' | xargs basename)"
else
  EVENT="Unknown"
  PROJECT=""
fi

case "$EVENT" in
  Notification)
    MESSAGE="Claude is waiting for input"
    ;;
  Stop)
    MESSAGE="Claude has completed the task"
    ;;
  *)
    MESSAGE="Event: $EVENT"
    ;;
esac

[ -n "$PROJECT" ] && MESSAGE="$MESSAGE (Project: $PROJECT)"

curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$MESSAGE\"}" \
  "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 || true

exit 0
```

---

## Hooks for Parliament of Chaos Workflows

### Council Session Notifications

Get notified when the Senior Council completes a review cycle:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/council_complete.sh"
          }
        ]
      }
    ]
  }
}
```

### Pre-Implementation Safety Check

Run validation before file modifications during `/implement-task-list`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/pre_write_check.sh"
          }
        ]
      }
    ]
  }
}
```

### Audit Trail Hook

Log all tool usage for compliance:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/audit_log.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Project File Structure

The Parliament of Chaos hooks setup uses this structure:

```
.claude/
  settings.json           # Shared hooks (committed)
  settings.local.json     # Personal hooks (gitignored)
  hooks/
    .env                  # Webhook URLs and secrets (gitignored)
    notify_teams.sh       # Teams notification script
    debug_hook.sh         # Debug logging script
    hook_debug.log        # Debug output (gitignored)
```

### Files Included with Parliament of Chaos

| File | Purpose |
|------|---------|
| `hooks/notify_teams.sh` | Microsoft Teams webhook notifications |
| `hooks/debug_hook.sh` | Event logging for debugging |
| `hooks/.env` | Environment variables template |

---

## Best Practices

### Keep Hook Scripts Fast

Hooks run synchronously. Long-running scripts delay Claude's response.

```bash
# Good: Fire and forget
curl -sS -X POST "$WEBHOOK_URL" -d "$PAYLOAD" >/dev/null 2>&1 &

# Bad: Wait for response
response=$(curl -sS -X POST "$WEBHOOK_URL" -d "$PAYLOAD")
process_response "$response"
```

### Handle Missing Dependencies Gracefully

```bash
# Check for jq before using it
if command -v jq >/dev/null 2>&1; then
  EVENT="$(echo "$JSON" | jq -r '.hook_event_name')"
else
  EVENT="Unknown"
fi
```

### Always Exit Successfully

Failing hooks can disrupt Claude's workflow:

```bash
# Good: Always succeed
curl "$WEBHOOK_URL" || true
exit 0

# Bad: Let errors propagate
curl "$WEBHOOK_URL"
```

### Protect Secrets

Never commit webhook URLs or API keys:

1. Store secrets in `.claude/hooks/.env`
2. Add `.env` patterns to `.gitignore`
3. Use environment variables in scripts

---

## Troubleshooting

### Hook Not Firing

1. Verify the settings file is valid JSON
2. Check the event name is spelled correctly
3. Ensure the script is executable (`chmod +x script.sh`)
4. Use the debug hook to confirm events are triggering

### Script Errors

1. Check the debug log at `.claude/hooks/hook_debug.log`
2. Run the script manually with test input:
   ```bash
   echo '{"hook_event_name":"Test"}' | ./your_hook.sh
   ```
3. Verify required commands are installed (`jq`, `curl`, etc.)

### Webhook Not Receiving Messages

1. Verify the webhook URL is correct
2. Test the webhook directly:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"text":"Test"}' "$WEBHOOK_URL"
   ```
3. Check firewall/network restrictions

---

## Next Steps

- Review the [Usage Guide](usage.md) for Parliament of Chaos commands
- See [Safe Progress Assurance](safe-progress-assurance.md) for implementation safety
- Explore the example hooks in `.claude/hooks/`
