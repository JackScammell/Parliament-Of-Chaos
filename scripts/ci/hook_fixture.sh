#!/usr/bin/env bash
# ============================================================================
# Parliament of Chaos — hook fixture-fire test ("The Gate", v1.26.0)
#
# Pure bash + jq; no claude CLI, no API key. For EVERY event wired to
# src/hooks/log_event.sh in hooks/hooks.json, pipes a fixture payload through
# the real script and asserts:
#   - exit 0, exactly ONE valid JSONL line appended
#   - correct `type` mapping (the table below is deliberate double-entry
#     bookkeeping against log_event.sh: wiring a new event without updating
#     BOTH fails this gate)
#   - envelope fields (schema_version, event, session, timestamp, additive
#     agent_id / effort_level) and event-specific fields survive the pipeline
#   - allowlist rejection: unknown events write NOTHING (exit 0)
#   - minimal rotation/permission safety: umask 077 effective (dir 700 /
#     file 600), >10MB log rotates to a .old file before append
#
# Not verified here: that Claude Code actually FIRES these hooks in a session
# (install-smoke covers registration; live firing needs a real keyed session),
# nor notify_teams.sh behaviour.
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_JSON="$REPO_ROOT/hooks/hooks.json"
LOG_EVENT="$REPO_ROOT/src/hooks/log_event.sh"

# jq is a hard requirement HERE even though log_event.sh soft-exits without it:
# a jq-less runner must fail the gate loudly, not pass it silently.
command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required" >&2; exit 2; }
[ -f "$HOOKS_JSON" ]  || { echo "ERROR: missing $HOOKS_JSON" >&2; exit 2; }
[ -f "$LOG_EVENT" ]   || { echo "ERROR: missing $LOG_EVENT" >&2; exit 2; }
jq empty "$HOOKS_JSON" || { echo "ERROR: hooks/hooks.json is not valid JSON" >&2; exit 2; }

# T3 (testing-tyrant): the heartbeat's plugin_version is deterministic in
# fixture context (BASH_SOURCE resolves to this repo's plugin.json), so assert
# the exact value — a regression hardcoding "unknown" must fail.
REPO_PLUGIN_VERSION="$(jq -r '.version' "$REPO_ROOT/.claude-plugin/plugin.json")"

FAILURES=0
fail() { echo "FAIL: $*" >&2; FAILURES=$((FAILURES + 1)); }
pass() { echo "  ok: $*"; }

BASE_TMP="$(mktemp -d)"
trap 'rm -rf "$BASE_TMP"' EXIT

# Portable permission read (Linux stat -c / BSD stat -f, for local macOS runs).
perms() { stat -c '%a' "$1" 2>/dev/null || stat -f '%Lp' "$1"; }

# --- Expected event -> type mapping (mirror of log_event.sh's case table) ---
expected_type() {
  case "$1" in
    PermissionDenied)   echo "permission_denied" ;;
    StopFailure)        echo "stop_failure" ;;
    SubagentStart)      echo "agent_start" ;;
    TaskCreated)        echo "task_created" ;;
    TaskCompleted)      echo "task_completed" ;;
    SessionStart)       echo "heartbeat" ;;
    PostCompact)        echo "compaction" ;;
    InstructionsLoaded) echo "instructions_loaded" ;;
    PostToolUse)        echo "tool_use" ;;
    PostToolUseFailure) echo "tool_use_failure" ;;
    *) return 1 ;;
  esac
}

# --- Fixture payload per event ----------------------------------------------
build_payload() {
  local event="$1" base
  base="$(jq -n --arg e "$event" --arg cwd "$REPO_ROOT" '{
    hook_event_name: $e,
    session_id: "fixture-session",
    cwd: $cwd,
    agent_id: "fixture-agent",
    effort: {level: "medium"}
  }')"
  case "$event" in
    PermissionDenied)
      jq -n --argjson b "$base" '$b + {tool_name: "Bash", reason: "fixture-denial"}' ;;
    StopFailure)
      jq -n --argjson b "$base" '$b + {stop_reason: "fixture-stop"}' ;;
    TaskCompleted)
      jq -n --argjson b "$base" '$b + {status: "completed"}' ;;
    SessionStart)
      jq -n --argjson b "$base" '$b + {source: "startup"}' ;;
    PostToolUse|PostToolUseFailure)
      jq -n --argjson b "$base" '$b + {tool_name: "Bash", tool_use_id: "toolu_fixture", duration_ms: 42}' ;;
    *)
      printf '%s' "$base" ;;
  esac
}

# Event-specific jq assertion (beyond the shared envelope assertion).
# MAINTAINER WARNING (security review): these strings are spliced into a jq
# program. Every return value MUST remain a hard-coded literal containing no
# single quotes; no external input may ever reach this function. Dynamic values
# (e.g. the plugin version) are passed via jq --arg on the caller's invocation
# and referenced as $vars here — never interpolated into these strings. A
# malformed assertion fails the gate closed (jq syntax error), but keep it clean.
extra_assertion() {
  case "$1" in
    PermissionDenied)   echo '.tool_name == "Bash" and .reason == "fixture-denial"' ;;
    StopFailure)        echo '.stop_reason == "fixture-stop"' ;;
    TaskCompleted)      echo '.status == "completed"' ;;
    SessionStart)       echo '.source == "startup" and .plugin_version == $pv' ;;
    PostToolUse|PostToolUseFailure)
                        echo '.tool_name == "Bash" and .tool_use_id == "toolu_fixture" and .duration_ms == 42' ;;
    *)                  echo 'true' ;;
  esac
}

# --- Derive the allowlisted event set from hooks/hooks.json -----------------
# (while-read loop, not mapfile: macOS system bash 3.2 lacks mapfile and this
# script is dual-use for local runs)
EVENTS=()
while IFS= read -r e; do EVENTS+=("$e"); done < <(jq -r '
  .hooks | to_entries[]
  | select([.value[].hooks[].command] | any(contains("log_event.sh")))
  | .key' "$HOOKS_JSON")

[ "${#EVENTS[@]}" -gt 0 ] || { echo "ERROR: no events wired to log_event.sh in hooks.json" >&2; exit 2; }
# T4 (testing-tyrant): the bookkeeping must be two-directional. Adding an event
# without a fixture mapping fails below; REMOVING one would silently shrink the
# suite without this pin. Update the count deliberately when (un)wiring events.
EXPECTED_WIRED_EVENTS=10
[ "${#EVENTS[@]}" -eq "$EXPECTED_WIRED_EVENTS" ] \
  || fail "expected $EXPECTED_WIRED_EVENTS events wired to log_event.sh, found ${#EVENTS[@]} — update hooks.json, log_event.sh, and this script together"
echo "== hook-fixture: ${#EVENTS[@]} event(s) wired to log_event.sh: ${EVENTS[*]}"

# --- Fire each event into a FRESH data dir and assert -----------------------
for event in "${EVENTS[@]}"; do
  if ! etype="$(expected_type "$event")"; then
    fail "$event is wired to log_event.sh in hooks.json but has no fixture mapping — update BOTH log_event.sh's case table and this script"
    continue
  fi

  data_dir="$BASE_TMP/$event"
  mkdir -p "$data_dir"
  log_file="$data_dir/agent-logs/activity.jsonl"

  if ! build_payload "$event" | CLAUDE_PLUGIN_DATA="$data_dir" bash "$LOG_EVENT"; then
    fail "$event: log_event.sh exited non-zero"
    continue
  fi

  [ -f "$log_file" ] || { fail "$event: no activity.jsonl written"; continue; }

  lines="$(wc -l < "$log_file" | tr -d ' ')"
  [ "$lines" -eq 1 ] || { fail "$event: expected exactly 1 JSONL line, got $lines"; continue; }

  if ! jq empty "$log_file" 2>/dev/null; then
    fail "$event: activity.jsonl line is not valid JSON"
    continue
  fi

  if jq -e --arg event "$event" --arg etype "$etype" --arg pv "$REPO_PLUGIN_VERSION" '
       .schema_version == 1
       and .event == $event
       and .type == $etype
       and .session == "fixture-session"
       and (.timestamp | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T"))
       and .agent_id == "fixture-agent"
       and .effort_level == "medium"
       and ('"$(extra_assertion "$event")"')' "$log_file" >/dev/null; then
    pass "$event -> type=$etype (envelope + event fields correct)"
  else
    fail "$event: assertion failed. Line was: $(cat "$log_file")"
    continue
  fi

  # Minimal permission safety (umask 077): dir 700, file 600.
  dperm="$(perms "$data_dir/agent-logs")"
  fperm="$(perms "$log_file")"
  [ "$dperm" = "700" ] || fail "$event: agent-logs dir perms $dperm, expected 700 (umask 077 regression)"
  [ "$fperm" = "600" ] || fail "$event: activity.jsonl perms $fperm, expected 600 (umask 077 regression)"
done

# --- Degradation path (T3): SessionStart without a source field --------------
# Older harnesses may omit .source; the heartbeat must still be written with
# the source field OMITTED (not empty) — env-doctor's liveness check tolerates
# absence but must never see "".
deg_dir="$BASE_TMP/SessionStartNoSource"
mkdir -p "$deg_dir"
jq -n --arg cwd "$REPO_ROOT" '{hook_event_name: "SessionStart", session_id: "fixture-session", cwd: $cwd}' \
  | CLAUDE_PLUGIN_DATA="$deg_dir" bash "$LOG_EVENT"
deg_log="$deg_dir/agent-logs/activity.jsonl"
if jq -e '.type == "heartbeat" and (has("source") | not) and .schema_version == 1' "$deg_log" >/dev/null 2>&1; then
  pass "SessionStart without source: heartbeat written, source omitted (degradation path)"
else
  fail "SessionStart without source degradation path broken: $(cat "$deg_log" 2>/dev/null || echo 'no record')"
fi

# --- Allowlist rejection: unknown event writes nothing, exits 0 -------------
reject_dir="$BASE_TMP/RejectUnknown"
mkdir -p "$reject_dir"
if jq -n --arg cwd "$REPO_ROOT" \
     '{hook_event_name: "TotallyUnknownEvent", session_id: "fixture-session", cwd: $cwd}' \
     | CLAUDE_PLUGIN_DATA="$reject_dir" bash "$LOG_EVENT"; then
  if [ -s "$reject_dir/agent-logs/activity.jsonl" ]; then
    fail "unknown event was logged — allowlist rejection broken"
  else
    pass "unknown event rejected (exit 0, nothing written)"
  fi
else
  fail "unknown event caused non-zero exit (should be a silent exit 0)"
fi

# --- Minimal rotation safety: >10MB log rotates before append ---------------
rot_dir="$BASE_TMP/Rotation"
mkdir -p "$rot_dir/agent-logs"
dd if=/dev/zero of="$rot_dir/agent-logs/activity.jsonl" bs=1048576 count=11 status=none
build_payload "SubagentStart" | CLAUDE_PLUGIN_DATA="$rot_dir" bash "$LOG_EVENT"
rotated="$(find "$rot_dir/agent-logs" -name 'activity.jsonl.*.old' | head -n1)"
if [ -n "$rotated" ]; then
  pass "oversize log rotated to $(basename "$rotated")"
  lines="$(wc -l < "$rot_dir/agent-logs/activity.jsonl" | tr -d ' ')"
  [ "$lines" -eq 1 ] || fail "rotation: fresh log has $lines line(s), expected 1"
else
  fail "no rotation: 11MB activity.jsonl was not moved aside"
fi

# --- Verdict ----------------------------------------------------------------
echo
if [ "$FAILURES" -gt 0 ]; then
  echo "hook-fixture: FAILED ($FAILURES assertion(s) failed)" >&2
  exit 1
fi
echo "hook-fixture: PASSED (${#EVENTS[@]} events, allowlist rejection, rotation, permissions)"
