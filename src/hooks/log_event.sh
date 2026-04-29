#!/usr/bin/env bash
set -euo pipefail

# Unified event logger for Parliament of Chaos hook events
# Replaces individual logging scripts with a single dispatcher
# Writes JSONL entries to ${CLAUDE_PLUGIN_DATA}/agent-logs/activity.jsonl

# shellcheck source=_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

# Restrict permissions on log files and directories
umask 077

# Set up log directory and file
LOG_DIR="$HOOK_DATA_DIR/agent-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/activity.jsonl"

# Log rotation: rotate when >10MB. Timestamped backups accumulate and
# should be pruned externally if disk space is a concern.
# Uses a lock file to prevent race conditions under concurrent hook invocations.
if [ -f "$LOG_FILE" ]; then
  LOCK_FILE="${LOG_FILE}.lock"
  if ( set -o noclobber; echo $$ > "$LOCK_FILE" ) 2>/dev/null; then
    trap 'rm -f "$LOCK_FILE"' EXIT
    LOG_SIZE=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$LOG_SIZE" -gt 10485760 ]; then
      mv "$LOG_FILE" "${LOG_FILE}.$(date +%s).old"
    fi
    rm -f "$LOCK_FILE"
    trap - EXIT
  fi
fi

# Determine event type and extract event-specific fields as a JSON fragment
EXTRA_JSON="{}"
EVENT_TYPE=""

case "$HOOK_EVENT_NAME" in
  PermissionDenied)
    TOOL_NAME="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.tool_name // "unknown"')"
    REASON="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.reason // "unknown"')"
    EXTRA_JSON=$(jq -n --arg tool_name "$TOOL_NAME" --arg reason "$REASON" '$ARGS.named')
    EVENT_TYPE="permission_denied" ;;
  StopFailure)
    STOP_REASON="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.stop_reason // "unknown"')"
    EXTRA_JSON=$(jq -n --arg stop_reason "$STOP_REASON" '$ARGS.named')
    EVENT_TYPE="stop_failure" ;;
  SubagentStart)
    EVENT_TYPE="agent_start" ;;
  TaskCreated)
    EVENT_TYPE="task_created" ;;
  PostCompact)
    EVENT_TYPE="compaction" ;;
  InstructionsLoaded)
    EVENT_TYPE="instructions_loaded" ;;
  PostToolUse|PostToolUseFailure)
    # Claude Code v2.1.119+ includes duration_ms on PostToolUse and PostToolUseFailure.
    # Capture for /parliament-metrics latency panel. Falls back to omitting the field
    # on older versions; consumers MUST tolerate an absent duration_ms.
    TOOL_NAME="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.tool_name // "unknown"')"
    DURATION_MS="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.duration_ms // empty')"
    TOOL_USE_ID="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.tool_use_id // empty')"
    # Build EXTRA_JSON. Omit fields whose source value is empty rather than
    # emitting empty strings — keeps the activity.jsonl schema clean.
    if [ -n "$DURATION_MS" ]; then
      EXTRA_JSON=$(jq -n \
        --arg tool_name "$TOOL_NAME" \
        --arg tool_use_id "$TOOL_USE_ID" \
        --argjson duration_ms "$DURATION_MS" \
        '{tool_name: $tool_name}
         + (if $tool_use_id == "" then {} else {tool_use_id: $tool_use_id} end)
         + {duration_ms: $duration_ms}')
    else
      EXTRA_JSON=$(jq -n \
        --arg tool_name "$TOOL_NAME" \
        --arg tool_use_id "$TOOL_USE_ID" \
        '{tool_name: $tool_name}
         + (if $tool_use_id == "" then {} else {tool_use_id: $tool_use_id} end)')
    fi
    if [ "$HOOK_EVENT_NAME" = "PostToolUseFailure" ]; then
      EVENT_TYPE="tool_use_failure"
    else
      EVENT_TYPE="tool_use"
    fi ;;
  *)
    # Reject unknown events — only allowlisted events are logged
    exit 0 ;;
esac

# Build base JSON and merge any event-specific fields
jq -n \
  --arg event "$HOOK_EVENT_NAME" \
  --arg session "$HOOK_SESSION_ID" \
  --arg ts "$HOOK_TIMESTAMP" \
  --arg type "$EVENT_TYPE" \
  --argjson extra "$EXTRA_JSON" \
  '{"event":$event,"session":$session,"timestamp":$ts,"type":$type} + $extra' \
  >> "$LOG_FILE"

exit 0
