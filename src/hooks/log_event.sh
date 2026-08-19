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
# The noclobber lock only serialises the rotation decision itself (so two
# concurrent invocations don't both mv the file). It does NOT cover the
# append at the bottom of this script: a write racing a rotation may land in
# the freshly-rotated .old file, which is acceptable — appends use O_APPEND
# and are small enough to be atomic on local filesystems, so no record is
# ever corrupted or lost, merely filed in the previous window.
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
  TaskCompleted)
    # Completion signal for the B4 member-reliability watchdog and the fan-out
    # reconcile loop (.claude/rules/fan-out-policy.md): lets a consumer tell
    # "returned a verdict / Done" from "still running" while tailing the log.
    # The per-member identifier is already surfaced additively as agent_id by
    # _common.sh, so it lands on the base envelope without extra work here.
    # status is captured best-effort: no Claude Code version is documented to
    # guarantee a .status field on the TaskCompleted payload, so we read it
    # opportunistically and omit it when absent (the `// empty` guard). This is
    # a shell-level guard (leave EXTRA_JSON as {} when empty), not the jq-level
    # conditional-merge the tool_use_id/duration_ms blocks below use — same
    # omit-when-empty outcome, simpler here since there is only one field.
    TASK_STATUS="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.status // empty')"
    if [ -n "$TASK_STATUS" ]; then
      EXTRA_JSON=$(jq -n --arg status "$TASK_STATUS" '{status: $status}')
    fi
    EVENT_TYPE="task_completed" ;;
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

# Build base JSON and merge any event-specific fields.
# effort_level / agent_id are additive: omitted when their source value is
# empty (older Claude Code, or a top-session hook for agent_id) so the
# activity.jsonl schema stays clean. Same conditional-merge idiom as the
# tool_use_id field above — no new control flow.
# -c (compact) is REQUIRED: this is the statement that appends to activity.jsonl,
# and jq pretty-prints by default. Without -c each record would span multiple
# lines and break every line-tailing consumer (the fan-out detection loop,
# /parliament-metrics, /telemetry-query) — the file must stay true JSONL.
jq -cn \
  --arg event "$HOOK_EVENT_NAME" \
  --arg session "$HOOK_SESSION_ID" \
  --arg ts "$HOOK_TIMESTAMP" \
  --arg type "$EVENT_TYPE" \
  --arg effort_level "$HOOK_EFFORT_LEVEL" \
  --arg agent_id "$HOOK_AGENT_ID" \
  --argjson extra "$EXTRA_JSON" \
  '{"event":$event,"session":$session,"timestamp":$ts,"type":$type}
   + (if $effort_level == "" then {} else {effort_level: $effort_level} end)
   + (if $agent_id == "" then {} else {agent_id: $agent_id} end)
   + $extra' \
  >> "$LOG_FILE"

exit 0
