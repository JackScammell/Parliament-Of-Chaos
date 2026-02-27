#!/usr/bin/env bash
set -euo pipefail

# Load .env file next to this script, if present
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
  # Export all variables defined in .env
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

# Teams webhook URL must be in the environment of the Claude process
TEAMS_WEBHOOK_URL="${TEAMS_WEBHOOK_URL:-}"

# If webhook isn't set, exit silently
[ -z "$TEAMS_WEBHOOK_URL" ] && exit 0

# Read JSON from stdin (hook payload)
HOOK_JSON="$(cat)"

# Extract metadata if jq is available
if command -v jq >/dev/null 2>&1; then
  HOOK_EVENT_NAME="$(printf '%s' "$HOOK_JSON" | jq -r '.hook_event_name // "UnknownEvent"')"
  CWD="$(printf '%s' "$HOOK_JSON" | jq -r '.cwd // ""')"
  SESSION_ID="$(printf '%s' "$HOOK_JSON" | jq -r '.session_id // "unknown-session"')"
else
  HOOK_EVENT_NAME="UnknownEvent"
  CWD=""
  SESSION_ID="unknown-session"
fi

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
  *)
    TITLE="Claude Code: $HOOK_EVENT_NAME"
    BASE_TEXT="Event: $HOOK_EVENT_NAME"
    ;;
esac

EXTRA=""
[ -n "$APP_NAME" ] && EXTRA="${EXTRA}**Instance**: \`$APP_NAME\`\n"
[ -n "$PROJECT_NAME" ] && EXTRA="${EXTRA}**Project**: \`$PROJECT_NAME\`\n"
[ -n "$SESSION_ID" ] && EXTRA="${EXTRA}**Session**: \`$SESSION_ID\`\n"

TEXT="$BASE_TEXT"
[ -n "$EXTRA" ] && TEXT="$TEXT\n\n$EXTRA"

PAYLOAD=$(cat <<EOF
{
  "@type": "MessageCard",
  "@context": "http://schema.org/extensions",
  "summary": "$TITLE",
  "themeColor": "0076D7",
  "title": "$TITLE",
  "text": "$TEXT"
}
EOF
)

# Send silently to Teams
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$TEAMS_WEBHOOK_URL" >/dev/null 2>&1 || true

exit 0
