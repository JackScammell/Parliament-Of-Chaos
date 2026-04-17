#!/usr/bin/env bash
set -euo pipefail

# Load .env file next to this script, if present
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
  # Only source .env if owned by the current user and not group- or world-writable.
  # Sourcing a .env is inherently trust-based — these guards prevent accidental exposure only.
  if [ "$(stat -f %u "$ENV_FILE" 2>/dev/null || stat -c %u "$ENV_FILE" 2>/dev/null)" = "$(id -u)" ] \
     && ! stat -f %Sp "$ENV_FILE" 2>/dev/null | grep -q '..w$' \
     && ! stat -c %a "$ENV_FILE" 2>/dev/null | grep -q '[2367]$'; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
  fi
fi

# Note: This script sends webhooks only and does not write to CLAUDE_PLUGIN_DATA.
# Log-writing hooks use _common.sh for shared state resolution.

# Teams webhook URL must be in the environment of the Claude process
TEAMS_WEBHOOK_URL="${TEAMS_WEBHOOK_URL:-}"

# If webhook isn't set, exit silently
[ -z "$TEAMS_WEBHOOK_URL" ] && exit 0
# Validate URL scheme
case "$TEAMS_WEBHOOK_URL" in https://*) ;; *) exit 1 ;; esac

# Read JSON from stdin (hook payload)
HOOK_JSON="$(cat)"

# Require jq for JSON parsing and safe payload construction
if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

HOOK_EVENT_NAME="$(printf '%s' "$HOOK_JSON" | jq -r '.hook_event_name // "UnknownEvent"')"
CWD="$(printf '%s' "$HOOK_JSON" | jq -r '.cwd // ""')"
SESSION_ID="$(printf '%s' "$HOOK_JSON" | jq -r '.session_id // "unknown-session"')"

PROJECT_NAME="$(basename "$CWD")"
APP_NAME="${APP_NAME:-}"

case "$HOOK_EVENT_NAME" in
  Notification)
    TITLE="Claude Code: waiting for input"
    BASE_TEXT="I am waiting for some input!"
    ;;
  Stop)
    TITLE="Claude Code: task complete"
    BASE_TEXT="I have completed my task."
    ;;
  TaskCompleted)
    TITLE="Claude Code: agent task completed"
    BASE_TEXT="An agent has completed its task."
    ;;
  SubagentStart)
    TITLE="Claude Code: agent spawned"
    BASE_TEXT="A new sub-agent has been started."
    ;;
  TeammateIdle)
    TITLE="Claude Code: teammate idle"
    BASE_TEXT="A teammate agent is idle and available for work."
    ;;
  StopFailure)
    TITLE="Claude Code: API failure"
    BASE_TEXT="Parliament session interrupted by an API error (rate limit or auth failure)."
    ;;
  PostCompact)
    TITLE="Claude Code: context compacted"
    BASE_TEXT="Context window was compacted during a Parliament session."
    ;;
  InstructionsLoaded)
    TITLE="Claude Code: rules reloaded"
    BASE_TEXT="CLAUDE.md or rules files were reloaded during session."
    ;;
  PermissionDenied)
    TITLE="Claude Code: tool call denied"
    BASE_TEXT="Auto mode denied a tool call during a Parliament session."
    ;;
  *)
    # Reject unknown events — only allowlisted events produce webhook payloads
    exit 0
    ;;
esac

EXTRA=""
[ -n "$APP_NAME" ] && EXTRA="${EXTRA}**Instance**: \`$APP_NAME\`\n"
[ -n "$PROJECT_NAME" ] && EXTRA="${EXTRA}**Project**: \`$PROJECT_NAME\`\n"
[ -n "$SESSION_ID" ] && EXTRA="${EXTRA}**Session**: \`$SESSION_ID\`\n"

TEXT="$BASE_TEXT"
[ -n "$EXTRA" ] && TEXT="$TEXT\n\n$EXTRA"

PAYLOAD=$(jq -n \
  --arg title "$TITLE" \
  --arg text "$TEXT" \
  '{
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    summary: $title,
    themeColor: "0076D7",
    title: $title,
    text: $text
  }')

# Send silently to Teams
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$TEAMS_WEBHOOK_URL" >/dev/null 2>&1 || true

exit 0
