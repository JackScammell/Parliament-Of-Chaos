#!/usr/bin/env bash
set -euo pipefail

# Handle API failures (rate limits, auth errors) during Parliament sessions
# Logs the failure to activity.jsonl. Notification is handled by notify_teams.sh

PAYLOAD="$(cat)"

# Require jq for structured logging
if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

EVENT="$(printf '%s' "$PAYLOAD" | jq -r '.hook_event_name // "unknown"')"
SESSION="$(printf '%s' "$PAYLOAD" | jq -r '.session_id // "unknown"')"
CWD="$(printf '%s' "$PAYLOAD" | jq -r '.cwd // ""')"
STOP_REASON="$(printf '%s' "$PAYLOAD" | jq -r '.stop_reason // "unknown"')"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Use CLAUDE_PROJECT_DIR if available, fall back to cwd
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$CWD}"
[ -z "$PROJECT_DIR" ] && exit 0
# Validate path: must be absolute, no traversal sequences
case "$PROJECT_DIR" in *..* ) exit 1 ;; esac
[[ "$PROJECT_DIR" != /* ]] && exit 1

LOG_DIR="$PROJECT_DIR/.project-files/agent-logs"
mkdir -p "$LOG_DIR"

jq -n --arg event "$EVENT" --arg session "$SESSION" --arg ts "$TIMESTAMP" \
  --arg reason "$STOP_REASON" \
  '{"event":$event,"session":$session,"timestamp":$ts,"stop_reason":$reason,"type":"stop_failure"}' >> "$LOG_DIR/activity.jsonl"

exit 0
