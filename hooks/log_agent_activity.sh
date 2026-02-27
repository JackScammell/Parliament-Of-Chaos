#!/usr/bin/env bash
set -euo pipefail

# Log agent lifecycle events for observability and analytics
# Writes JSONL entries to .project-files/agent-logs/activity.jsonl

PAYLOAD="$(cat)"

# Require jq for structured logging
if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

EVENT="$(printf '%s' "$PAYLOAD" | jq -r '.hook_event_name // "unknown"')"
SESSION="$(printf '%s' "$PAYLOAD" | jq -r '.session_id // "unknown"')"
CWD="$(printf '%s' "$PAYLOAD" | jq -r '.cwd // ""')"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Use CLAUDE_PROJECT_DIR if available, fall back to cwd
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$CWD}"
[ -z "$PROJECT_DIR" ] && exit 0

LOG_DIR="$PROJECT_DIR/.project-files/agent-logs"
mkdir -p "$LOG_DIR"

printf '{"event":"%s","session":"%s","timestamp":"%s"}\n' \
  "$EVENT" "$SESSION" "$TIMESTAMP" >> "$LOG_DIR/activity.jsonl"

exit 0
