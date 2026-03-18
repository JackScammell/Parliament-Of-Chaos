#!/usr/bin/env bash
set -euo pipefail

# Log debate completion events for /debate-analytics
# Writes JSONL entries to .project-files/debate-logs/completions.jsonl

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

LOG_DIR="$PROJECT_DIR/.project-files/debate-logs"
mkdir -p "$LOG_DIR"

jq -n --arg event "$EVENT" --arg session "$SESSION" --arg ts "$TIMESTAMP" \
  '{"event":$event,"session":$session,"timestamp":$ts,"type":"debate_completion"}' >> "$LOG_DIR/completions.jsonl"

exit 0
