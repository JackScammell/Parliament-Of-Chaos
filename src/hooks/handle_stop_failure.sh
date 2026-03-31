#!/usr/bin/env bash
set -euo pipefail

# Handle API failures (rate limits, auth errors) during Parliament sessions
# Logs the failure to activity.jsonl. Notification is handled by notify_teams.sh

# shellcheck source=_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

STOP_REASON="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.stop_reason // "unknown"')"

LOG_DIR="$HOOK_DATA_DIR/agent-logs"
mkdir -p "$LOG_DIR"

jq -n --arg event "$HOOK_EVENT_NAME" --arg session "$HOOK_SESSION_ID" --arg ts "$HOOK_TIMESTAMP" \
  --arg reason "$STOP_REASON" \
  '{"event":$event,"session":$session,"timestamp":$ts,"stop_reason":$reason,"type":"stop_failure"}' >> "$LOG_DIR/activity.jsonl"

exit 0
