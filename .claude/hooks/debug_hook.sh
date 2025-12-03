#!/usr/bin/env sh
set -eu

LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/hook_debug.log"

{
  echo "====== HOOK RUN at $(date) ======"
  echo "HOOK_EVENT_NAME (raw JSON):"
  cat
  echo
  echo "Env snapshot:"
  echo "TEAMS_WEBHOOK_URL=${TEAMS_WEBHOOK_URL:-<unset>}"
  echo "APP_NAME=${APP_NAME:-<unset>}"
  echo "CLAUDE_PROJECT_DIR=${CLAUDE_PROJECT_DIR:-<unset>}"
  echo "PWD=$(pwd)"
  echo "================================="
  echo
} >> "$LOG_FILE" 2>&1

exit 0
