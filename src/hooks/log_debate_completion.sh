#!/usr/bin/env bash
set -euo pipefail

# Log debate completion events for /debate-analytics
# Writes JSONL entries to ${CLAUDE_PLUGIN_DATA}/debate-logs/completions.jsonl

# shellcheck source=_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

LOG_DIR="$HOOK_DATA_DIR/debate-logs"
mkdir -p "$LOG_DIR"

jq -n --arg event "$HOOK_EVENT_NAME" --arg session "$HOOK_SESSION_ID" --arg ts "$HOOK_TIMESTAMP" \
  '{"event":$event,"session":$session,"timestamp":$ts,"type":"debate_completion"}' >> "$LOG_DIR/completions.jsonl"

exit 0
