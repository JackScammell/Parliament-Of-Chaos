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
| `StopFailure` | Turn ends due to API error (rate limit, auth) | Error recovery, incident alerts |
| `TaskCompleted` | Agent finishes a task | Progress tracking |
| `SubagentStart` | New sub-agent spawned | Activity monitoring |
| `PostCompact` | Context window compacted | State checkpointing |
| `InstructionsLoaded` | CLAUDE.md or rules files loaded/reloaded | Detect stale rules in long sessions |
| `TeammateIdle` | Teammate agent is idle | Multi-agent coordination |
| `SessionStart` | Session begins/resumes/clears/compacts | **Heartbeat telemetry (v1.26.0)** — liveness signal for /env-doctor |
| `PermissionDenied` | Auto mode denies a tool call | Denial diagnostics |
| `TaskCreated` | Task created | Fan-out dispatch tracking |
| `PreToolUse` | Before a tool is executed | Validation, logging (not wired by Parliament) |
| `PostToolUse` | After a tool completes | Auditing, notifications |
| `PostToolUseFailure` | After a tool call fails | Failure-latency telemetry |

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

Parliament of Chaos includes a ready-to-use Microsoft Teams notification hook.

> **⚠️ As of v1.25.0 this hook is auto-registered by the plugin.** `hooks/hooks.json`
> (auto-loaded by Claude Code from that conventional path) already wires
> `notify_teams.sh` to `Notification`, `Stop`, `TaskCompleted`, `StopFailure`,
> `PermissionDenied`, and `TeammateIdle`. **You only need Step 1 (the webhook URL)** — do NOT also wire these
> events manually in your own settings, or every Teams message will arrive twice. The manual
> wiring in Step 2 below is only for (a) pre-v1.25.0 installs, where plugin hooks were never
> actually registered, or (b) a deliberately customised local copy replacing the plugin's.

### Step 1: Configure the Webhook URL

Edit the plugin's `.env` file:

```bash
# Location: ~/.claude/plugins/cache/chaos/chaos/*/src/hooks/.env
TEAMS_WEBHOOK_URL="https://your-org.webhook.office.com/webhookb2/..."
APP_NAME="My Project"
```

Or copy the hook to your project and configure locally:

```bash
mkdir -p .claude/hooks
cp ~/.claude/plugins/cache/chaos/chaos/*/src/hooks/notify_teams.sh .claude/hooks/
cp ~/.claude/plugins/cache/chaos/chaos/*/src/hooks/.env .claude/hooks/
# Edit .claude/hooks/.env with your webhook URL
```

### Step 2 (only if NOT using the plugin's auto-registration): Configure the Hook

Add to `.claude/settings.local.json`:

**Option A: Use plugin's hook directly**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/cache/chaos/chaos/*/src/hooks/notify_teams.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/cache/chaos/chaos/*/src/hooks/notify_teams.sh"
          }
        ]
      }
    ]
  }
}
```

**Option B: Use local copy (if you copied to your project)**
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

Save this to your project's `.claude/hooks/debug_hook.sh` and make it executable:

```bash
mkdir -p .claude/hooks
chmod +x .claude/hooks/debug_hook.sh
```

Note: You can save this script to your project's `.claude/hooks/` directory and reference it from your settings.

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

## File Locations

### Plugin Hooks (Marketplace Installation)

When installed via the marketplace, Parliament of Chaos hook scripts are stored in the centralised plugin cache:

```
~/.claude/plugins/cache/chaos/chaos/*/src/hooks/
  _common.sh                # Shared payload/env helpers (sourced by the others)
  log_event.sh              # Unified telemetry logger -> activity.jsonl
  notify_teams.sh           # Teams notification script
  log_debate_completion.sh  # Debate completion logging (agent-level Stop hook)
```

### Configuration Files

**The plugin's own hooks are auto-registered** from `hooks/hooks.json` in the plugin root —
Claude Code loads that path automatically (do not also reference it from `plugin.json`'s
`hooks` field, which is only for additional files and double-registers this one). This is the
only mechanism Claude Code honours for plugin hooks (a `hooks` block in a plugin-root `settings.json` is
silently ignored; that misconfiguration shipped from v1.9.0 to v1.24.0 and was fixed in
v1.25.0).

**Your own additional hooks** live in your project's settings files as usual:

```
.claude/
  settings.json           # Shared hooks (committed)
  settings.local.json     # Personal hooks (gitignored)
```

Avoid re-wiring events the plugin already registers (see the Teams example above) unless you
intend duplicates.

### Using Plugin Hooks in Configuration

When referencing the plugin's hook scripts, use the centralised path:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/cache/chaos/chaos/*/src/hooks/notify_teams.sh"
          }
        ]
      }
    ]
  }
}
```

**Or** copy the hook scripts to your project's `.claude/hooks/` directory for local customisation.

### Files Included with Parliament of Chaos

Hook scripts live in `src/hooks/` (so they survive plugin cache refreshes). As of v1.9.0 the four per-event scripts were consolidated into a single unified dispatcher:

| File | Location | Purpose |
|------|----------|---------|
| `_common.sh` | `src/hooks/` | Shared helper — payload parsing, path validation, data-directory resolution, log rotation (v1.7.0) |
| `log_event.sh` | `src/hooks/` | Unified event dispatcher — handles SessionStart (heartbeat), StopFailure, PostCompact, InstructionsLoaded, TaskCompleted, TaskCreated, SubagentStart, PermissionDenied, PostToolUse, PostToolUseFailure (10 events; `Stop`/`Notification`/`TeammateIdle` are notify-only) |
| `notify_teams.sh` | `src/hooks/` | Webhook notifications (Teams / Slack / Discord / custom HTTP endpoints) |
| `log_debate_completion.sh` | `src/hooks/` | Debate completion logging — wired as `deliberation-conductor`'s agent-level Stop hook |

Before v1.9.0 these were separate scripts (`log_agent_activity.sh`, `handle_stop_failure.sh`, `handle_post_compact.sh`, `handle_instructions_loaded.sh`). They have been removed; add a new logged event by adding a case to `log_event.sh`.

---

## Lifecycle Hook Events

All lifecycle events below are dispatched by the unified `log_event.sh` (v1.9.0+). Each event becomes one `case` branch inside that script — adding a new logged event is a one-line change. Notifications (Teams / Slack / Discord) are delegated to `notify_teams.sh`.

### StopFailure

Fires when a Parliament session is interrupted by an API error (rate limit or authentication failure).

**Dispatcher**: `log_event.sh` (case `StopFailure`) — Logs the failure with stop reason to `activity.jsonl`.

**Payload fields**:
- `hook_event_name`: "StopFailure"
- `stop_reason`: The reason for the failure (e.g., "rate_limit", "auth_error")
- `session_id`, `cwd`: Standard fields

### PostCompact

Fires after context window compaction completes during a long Parliament session.

**Dispatcher**: `log_event.sh` (case `PostCompact`) — Logs compaction events for monitoring context usage patterns.

**Use cases**:
- Track how often compaction occurs during council sessions
- Checkpoint state after compaction for recovery
- Monitor context pressure in long-running deliberations

### InstructionsLoaded

Fires when CLAUDE.md or `.claude/rules/*.md` files are loaded or reloaded during a session.

**Dispatcher**: `log_event.sh` (case `InstructionsLoaded`) — Logs rule reload events.

**Use cases**:
- Detect stale rules in long-running Parliament sessions
- Audit which rules files are active
- Track rule changes during a session

### PermissionDenied (v1.9.0)

Fires when auto mode denies a Parliament agent's tool call. Logs the denied tool name and reason for diagnosing silent agent failures in automated workflows. Wired to `notify_teams.sh` for optional team notification.

### TaskCreated / TaskCompleted (v1.9.0)

Completes the task lifecycle logging alongside the existing `TaskCompleted` hook — both are dispatched by `log_event.sh`.

### Webhook Configuration

Use `/parliament-webhook` to configure webhook notifications for all hook events. The command supports Teams, Slack, Discord, and custom HTTP endpoints. Webhook URLs are stored in `src/hooks/.env` (gitignored).

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
- Explore the bundled hooks in `src/hooks/` of the plugin repository
