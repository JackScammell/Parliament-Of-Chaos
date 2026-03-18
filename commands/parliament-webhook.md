---
description: Configure webhook notification endpoints for Parliament events
---

# Parliament Webhook

Configure HTTP webhook endpoints to receive notifications for Parliament of Chaos events. Supports Slack, Discord, Microsoft Teams, and custom webhook URLs.

## Usage

```
/parliament-webhook [action] [options]
```

**Actions**:
- `setup` — Interactive webhook configuration
- `test` — Send a test notification to configured endpoint
- `status` — Show current webhook configuration
- `disable` — Remove webhook configuration

## Setup Process

1. **Ask for webhook platform**:
   - Microsoft Teams (existing support via `notify_teams.sh`)
   - Slack (incoming webhook URL)
   - Discord (webhook URL)
   - Custom HTTP endpoint (POST JSON)

2. **Collect webhook URL** from user

3. **Configure the `.env` file** in `src/hooks/`:
   - Write `TEAMS_WEBHOOK_URL=<url>` for Teams
   - Write `SLACK_WEBHOOK_URL=<url>` for Slack
   - Write `DISCORD_WEBHOOK_URL=<url>` for Discord
   - Write `CUSTOM_WEBHOOK_URL=<url>` for custom endpoints

4. **Verify hooks are enabled** in `settings.json`:
   - Confirm all hook events have corresponding entries
   - List which events will trigger notifications

## Supported Events

| Event | Description |
|-------|-------------|
| `Notification` | Claude waiting for input |
| `Stop` | Task completed |
| `StopFailure` | API error (rate limit, auth failure) |
| `TaskCompleted` | Agent finished a task |
| `SubagentStart` | New sub-agent spawned |
| `PostCompact` | Context window compacted |
| `InstructionsLoaded` | Rules files reloaded |
| `TeammateIdle` | Teammate available for work |

## Test Action

Send a test message to the configured endpoint to verify connectivity:
```
/parliament-webhook test
```

## Status Action

Display current webhook configuration:
```
/parliament-webhook status
```

Shows:
- Configured platform and URL (masked)
- Enabled hook events
- Last notification timestamp (from activity log)

## Output

```markdown
# Webhook Configuration

**Platform**: [Teams/Slack/Discord/Custom]
**URL**: https://...****
**Status**: Active

## Enabled Events
- [list of hook events that trigger notifications]

## Recent Activity
- [last 5 notification events from agent-logs/activity.jsonl]
```

## Notes

- Webhook URLs are stored in `src/hooks/.env` which is gitignored
- The `.env` file is loaded by `notify_teams.sh` and future platform-specific hook scripts
- For HTTP hooks (Claude Code v2.1.63+), consider using native HTTP hook type instead of shell scripts for simpler integrations
- Never commit webhook URLs to version control
