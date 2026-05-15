#!/usr/bin/env bash
# Shared helpers for Parliament of Chaos hook scripts

# Read JSON payload from stdin
HOOK_PAYLOAD="$(cat)"

# Require jq for structured logging
if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

# Extract common fields
HOOK_EVENT_NAME="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.hook_event_name // "unknown"')"
HOOK_SESSION_ID="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.session_id // "unknown"')"
HOOK_CWD="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.cwd // ""')"
HOOK_TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Optional envelope enrichment fields. Both are additive and version-gated:
#   effort.level — present on hook payloads from Claude Code v2.1.133+; lets
#     /parliament-metrics --by-effort attribute hook-emitted events without an
#     OTel span or status-line event. Absent on older versions.
#   agent_id     — present when the hook fires inside a subagent (v2.1.139+);
#     enables per-agent token/event attribution. Absent for top-session hooks.
# Empty extractions are dropped at envelope-build time (// empty). Consumers
# MUST tolerate both fields being absent.
HOOK_EFFORT_LEVEL="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.effort.level // empty')"
HOOK_AGENT_ID="$(printf '%s' "$HOOK_PAYLOAD" | jq -r '.agent_id // empty')"

# Resolve project directory
HOOK_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$HOOK_CWD}"
[ -z "$HOOK_PROJECT_DIR" ] && exit 0
case "$HOOK_PROJECT_DIR" in *..* ) exit 1 ;; esac
[[ "$HOOK_PROJECT_DIR" != /* ]] && exit 1

# Resolve plugin data directory with fallback for older Claude Code versions.
# Telemetry/logs go here — separate from user-facing project data in .project-files/
HOOK_DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOOK_PROJECT_DIR/.project-files/.telemetry}"
