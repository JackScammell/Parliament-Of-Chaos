#!/usr/bin/env bash
set -euo pipefail

# Checkpoint state after context compaction
# Logs compaction events for monitoring context usage patterns

# shellcheck source=_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

LOG_DIR="$HOOK_DATA_DIR/agent-logs"
mkdir -p "$LOG_DIR"

jq -n --arg event "$HOOK_EVENT_NAME" --arg session "$HOOK_SESSION_ID" --arg ts "$HOOK_TIMESTAMP" \
  '{"event":$event,"session":$session,"timestamp":$ts,"type":"compaction"}' >> "$LOG_DIR/activity.jsonl"

exit 0
