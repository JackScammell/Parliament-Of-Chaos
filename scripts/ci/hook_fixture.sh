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
#   - SILENT OUTPUT on every healthy path: combined stdout+stderr must be
#     exactly 0 bytes. Deliberately-degraded paths get the weaker
#     MAX_HOOK_OUTPUT_BYTES bound instead (upstream v2.1.247 session-overflow
#     class — reached one line at a time as readily as in one burst)
#   - degraded environment: an UNWRITABLE data dir must not turn telemetry
#     failure into session noise
#
# Also covers src/hooks/notify_teams.sh, with `curl` replaced by a stub on
# PATH — this suite makes NO network calls of any kind, and must not start.
# The stub records its full argv, so the suite additionally asserts the SHAPE of
# the curl invocation (timeout and silent/show-error flags). That is deliberate:
# request safety is the one property a stub structurally cannot exercise, and an
# un-timed curl against a blackholing webhook host is the real session-hang
# hazard in that script.
#
# EVERY hook invocation in this file is guarded — either `set +e` / capture rc /
# `fail`, or an `if !` test. `set -e` is global here, so a BARE invocation would
# abort the entire suite the moment the hook regressed: the FAILURES machinery
# would never engage, the case's diagnostic would never print, and every
# assertion after it would silently never run. Keep the idiom when adding cases.
#
# Environment-conditional case groups are COUNTED (SKIPPED) and named in the
# final verdict line: a run that skipped the notify_teams fixtures or the
# unwritable-dir case must not be mistaken for a full pass.
#
# Not verified here: that Claude Code actually FIRES these hooks in a session
# (install-smoke covers registration; live firing needs a real keyed session).
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_JSON="$REPO_ROOT/hooks/hooks.json"
LOG_EVENT="$REPO_ROOT/src/hooks/log_event.sh"
NOTIFY_TEAMS="$REPO_ROOT/src/hooks/notify_teams.sh"

# Output budget for a DELIBERATELY DEGRADED hook invocation, in bytes of
# combined stdout+stderr. Upstream v2.1.247 fixed a class where megabytes of
# hook output wedge a session with "Prompt is too long".
#
# This budget is NOT the healthy-path contract. A hook is a side-channel, not a
# reporter, so on every non-degraded path its output volume must be exactly
# ZERO — asserted by assert_output_silent() below. The two assertions are
# deliberately different (testing-tyrant, v1.27.0): a suite whose only output
# assertion is "<= 512" green-lights a hook that starts emitting 400 bytes of
# diagnostic on EVERY event, which is precisely how the v2.1.247 overflow is
# reached one line at a time — the same failure the unwritable-dir case below
# exists to catch. `<= 512` is the right bound only where a diagnostic is
# expected; it is far too small to hide a leaked payload, a stack trace, or a
# curl transcript, and roomy enough for one line of degradation notice.
#
# Do NOT raise this, and do NOT downgrade a silent assertion to a bounded one,
# to make a noisy script pass. Quiet the script.
MAX_HOOK_OUTPUT_BYTES=512

# jq is a hard requirement HERE even though log_event.sh soft-exits without it:
# a jq-less runner must fail the gate loudly, not pass it silently.
command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required" >&2; exit 2; }
[ -f "$HOOKS_JSON" ]  || { echo "ERROR: missing $HOOKS_JSON" >&2; exit 2; }
[ -f "$LOG_EVENT" ]   || { echo "ERROR: missing $LOG_EVENT" >&2; exit 2; }
[ -f "$NOTIFY_TEAMS" ] || { echo "ERROR: missing $NOTIFY_TEAMS" >&2; exit 2; }
jq empty "$HOOKS_JSON" || { echo "ERROR: hooks/hooks.json is not valid JSON" >&2; exit 2; }

# T3 (testing-tyrant): the heartbeat's plugin_version is deterministic in
# fixture context (BASH_SOURCE resolves to this repo's plugin.json), so assert
# the exact value — a regression hardcoding "unknown" must fail.
REPO_PLUGIN_VERSION="$(jq -r '.version' "$REPO_ROOT/.claude-plugin/plugin.json")"

FAILURES=0
fail() { echo "FAIL: $*" >&2; FAILURES=$((FAILURES + 1)); }
pass() { echo "  ok: $*"; }

# Skipped case-GROUPS (testing-tyrant, v1.27.0). Two case groups are
# environment-conditional — the notify_teams fixtures (skipped when a real
# src/hooks/.env could inject a live webhook) and the unwritable-data-dir case
# (vacuous as root, since root ignores mode 500). Before this counter, both
# printed a NOTE to stderr and the run still ended with the SAME "PASSED (…
# unwritable-dir degradation, notify_teams via stubbed curl)" line: the verdict
# claimed coverage the run had not executed. A verdict that can lie about its own
# scope is worse than no verdict. The count is now surfaced in the final line, so
# "passed everything" and "passed what it bothered to run" are distinguishable at
# a glance.
SKIPPED=0
SKIP_LABELS=""
skip() {
  local label="$1"
  shift
  SKIPPED=$((SKIPPED + 1))
  if [ -z "$SKIP_LABELS" ]; then SKIP_LABELS="$label"; else SKIP_LABELS="$SKIP_LABELS, $label"; fi
  echo "SKIP: $label — $*" >&2
}

BASE_TMP="$(mktemp -d)"
# chmod 700 first: the unwritable-data-dir case below leaves a mode-500 dir
# behind, which rm -rf cannot descend into.
trap 'chmod -R u+rwX "$BASE_TMP" 2>/dev/null; rm -rf "$BASE_TMP"' EXIT

# Combined stdout+stderr of a hook invocation, in bytes.
out_bytes() { wc -c < "$1" | tr -d ' '; }

# Assert one invocation stayed inside the output budget. On breach, show a
# bounded excerpt — printing the whole thing would reproduce the very failure
# mode under test in the CI log.
assert_output_bounded() {
  local label="$1" out_file="$2" n
  n="$(out_bytes "$out_file")"
  if [ "$n" -gt "$MAX_HOOK_OUTPUT_BYTES" ]; then
    fail "$label: hook wrote $n bytes to stdout+stderr, budget is $MAX_HOOK_OUTPUT_BYTES" \
         "(upstream v2.1.247 session-overflow class: oversized hook output wedges a session" \
         "with 'Prompt is too long'). First 200 bytes: $(head -c 200 "$out_file")"
    return 1
  fi
  pass "$label: hook output $n byte(s) <= $MAX_HOOK_OUTPUT_BYTES"
  return 0
}

# Assert one invocation was COMPLETELY SILENT. This is the assertion for every
# NON-degraded path: a healthy hook writes its record and says nothing at all.
# Anything above zero — a debug echo, a stray `set -x`, a deprecation notice from
# a dependency — is a regression, because a hook fires on every event and even a
# few hundred bytes accumulates into the v2.1.247 session-overflow class over a
# long session. assert_output_bounded (512) is reserved for the two cases where a
# diagnostic is EXPECTED: the unwritable data dir and the failing webhook.
assert_output_silent() {
  local label="$1" out_file="$2" n
  n="$(out_bytes "$out_file")"
  if [ "$n" -ne 0 ]; then
    fail "$label: hook wrote $n byte(s) to stdout+stderr; a healthy hook invocation must be SILENT (0 bytes)." \
         "A hook is a side-channel, not a reporter: per-event chatter accumulates into the upstream" \
         "v2.1.247 session-overflow class one line at a time. Quiet the hook; do not relax this to" \
         "assert_output_bounded. First 200 bytes: $(head -c 200 "$out_file")"
    return 1
  fi
  pass "$label: hook output silent (0 bytes)"
  return 0
}

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
  out_file="$BASE_TMP/$event.out"

  # Combined stdout+stderr is captured, never discarded: a hook's output volume
  # is an asserted part of its contract, not incidental noise.
  #
  # ORDERING IS LOAD-BEARING (code-review M4, v1.27.0): the output assertion runs
  # BEFORE the exit-code branch. It used to sit after it, behind a `continue`, so
  # the single shape most likely to breach the budget — a hook that floods AND
  # fails, which is the realistic v2.1.247 shape because flooding happens on error
  # paths — was exactly the shape that skipped the output assertion entirely and
  # reported only its exit code plus `head -c 200` of the flood. Both facts are
  # now always asserted, for every event, in every outcome.
  #
  # The rc is captured rather than tested inline for the same reason as the
  # unwritable-dir case below: `set -e` is active, and a bare invocation would
  # abort the whole suite instead of recording a named failure.
  set +e
  build_payload "$event" | CLAUDE_PLUGIN_DATA="$data_dir" bash "$LOG_EVENT" >"$out_file" 2>&1
  ev_rc=$?
  set -e

  assert_output_silent "$event" "$out_file" || true

  if [ "$ev_rc" -ne 0 ]; then
    fail "$event: log_event.sh exited $ev_rc, expected 0. Output was: $(head -c 200 "$out_file")"
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
# `set +e` / capture rc / `fail` — NOT a bare invocation (code-review M3, v1.27.0).
# `set -e` is in force for the whole script, so a bare pipeline here would ABORT
# the suite the moment log_event.sh regressed to a non-zero exit on this path:
# the FAILURES machinery would never engage, this case's specific diagnostic
# would never print, and every assertion below — rotation, the unwritable dir,
# all four notify_teams cases, the webhook-URL-leak check — would silently never
# run. CI would still go red, but with the wrong cause and a truncated suite,
# which is strictly worse than a named failure. Every other invocation in this
# file already uses this idiom; these two were the outliers.
set +e
jq -n --arg cwd "$REPO_ROOT" '{hook_event_name: "SessionStart", session_id: "fixture-session", cwd: $cwd}' \
  | CLAUDE_PLUGIN_DATA="$deg_dir" bash "$LOG_EVENT" >"$BASE_TMP/deg.out" 2>&1
deg_rc=$?
set -e
assert_output_silent "SessionStart-no-source" "$BASE_TMP/deg.out" || true
[ "$deg_rc" -eq 0 ] \
  || fail "SessionStart without source: log_event.sh exited $deg_rc, expected 0. Output was: $(head -c 200 "$BASE_TMP/deg.out")"
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
     | CLAUDE_PLUGIN_DATA="$reject_dir" bash "$LOG_EVENT" >"$BASE_TMP/reject.out" 2>&1; then
  assert_output_silent "unknown-event" "$BASE_TMP/reject.out" || true
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
# Guarded for the same reason as the degradation case above (code-review M3):
# this one is the more dangerous of the two, because roughly ten assertions
# follow it. A bare invocation here turns a rotation regression into a silently
# truncated suite that never reaches the notify_teams fixtures at all.
set +e
build_payload "SubagentStart" | CLAUDE_PLUGIN_DATA="$rot_dir" bash "$LOG_EVENT" >"$BASE_TMP/rot.out" 2>&1
rot_rc=$?
set -e
assert_output_silent "rotation" "$BASE_TMP/rot.out" || true
[ "$rot_rc" -eq 0 ] \
  || fail "rotation: log_event.sh exited $rot_rc, expected 0. Output was: $(head -c 200 "$BASE_TMP/rot.out")"
rotated="$(find "$rot_dir/agent-logs" -name 'activity.jsonl.*.old' | head -n1)"
if [ -n "$rotated" ]; then
  pass "oversize log rotated to $(basename "$rotated")"
  lines="$(wc -l < "$rot_dir/agent-logs/activity.jsonl" | tr -d ' ')"
  [ "$lines" -eq 1 ] || fail "rotation: fresh log has $lines line(s), expected 1"
else
  fail "no rotation: 11MB activity.jsonl was not moved aside"
fi

# --- Degraded environment: UNWRITABLE data dir ------------------------------
# Telemetry is a side-channel. If the data dir cannot be written, the hook must
# give up silently — exit 0, no output. The failure mode this guards against is
# not a crash but a NAG: a hook that prints a shell diagnostic on every event
# for the rest of the session, which is exactly how the v2.1.247 overflow class
# is reached one line at a time. A session must never be degraded because
# telemetry could not be written.
if [ "$(id -u)" -eq 0 ]; then
  skip "unwritable-data-dir" \
       "running as root — chmod 500 is not enforced, so this case would be vacuous." \
       "CI (ubuntu-latest) runs non-root and DOES run it."
else
  ro_dir="$BASE_TMP/UnwritableDataDir"
  mkdir -p "$ro_dir"
  chmod 500 "$ro_dir"
  ro_out="$BASE_TMP/unwritable.out"
  set +e
  build_payload "SubagentStart" | CLAUDE_PLUGIN_DATA="$ro_dir" bash "$LOG_EVENT" >"$ro_out" 2>&1
  ro_rc=$?
  set -e
  chmod 700 "$ro_dir"
  if [ "$ro_rc" -eq 0 ]; then
    pass "unwritable data dir: hook exited 0 (telemetry failure invisible to the session)"
  else
    fail "unwritable data dir: log_event.sh exited $ro_rc, expected 0 — a hook must degrade" \
         "silently when it cannot write telemetry, never surface the failure to the session." \
         "Output was: $(head -c 200 "$ro_out")"
  fi
  assert_output_bounded "unwritable data dir" "$ro_out" || true
fi

# --- notify_teams.sh — fixtures with a STUBBED curl (no network, ever) -------
# notify_teams.sh is the genuinely risky hook for the v2.1.247 output class: it
# shells out to curl against an external webhook. It previously had no fixture
# at all because a real invocation would depend on network reachability.
# Resolved by putting a stub `curl` first on PATH: the suite exercises the whole
# script — payload construction, allowlist, scheme guard, output suppression —
# while making NO network call and depending on no external host. The stub can
# also FLOOD its output, which is how the suppression assertion below is proved
# rather than assumed, and it RECORDS ITS ARGV, which is how the request-safety
# assertions (timeout, silent/show-error) reach the one property a stub can
# otherwise never exercise.
#
# Flooding and the curl exit code are INDEPENDENT knobs (see nt_run): output
# suppression and webhook-failure tolerance are separate properties and must not
# be asserted only in combination.
if [ -f "$REPO_ROOT/src/hooks/.env" ]; then
  skip "notify_teams" \
       "src/hooks/.env exists — it would be sourced and could inject a real TEAMS_WEBHOOK_URL," \
       "so the notify_teams.sh fixtures cannot run safely on this machine." \
       "They always run in CI, where no .env exists."
else
  STUB_BIN="$BASE_TMP/stub-bin"
  mkdir -p "$STUB_BIN"
  STUB_MARKER="$BASE_TMP/curl-was-called"
  STUB_PAYLOAD="$BASE_TMP/curl-payload.json"
  STUB_URL="$BASE_TMP/curl-url"
  STUB_ARGV="$BASE_TMP/curl-argv"

  cat > "$STUB_BIN/curl" <<'STUB'
#!/usr/bin/env bash
# Fixture stub for curl. Records the invocation; NEVER opens a socket.
: > "$CURL_STUB_MARKER"
# Record the FULL argv, one argument per line. This is what makes the
# invocation-shape assertions below possible: with curl stubbed, the suite can
# never observe the behaviour of a real request, so the only thing it can
# meaningfully check about request safety is the arguments the caller chose.
printf '%s\n' "$@" > "$CURL_STUB_ARGV"
prev=""; last=""
for a in "$@"; do
  if [ "$prev" = "-d" ]; then printf '%s' "$a" > "$CURL_STUB_PAYLOAD"; fi
  prev="$a"; last="$a"
done
printf '%s' "$last" > "$CURL_STUB_URL"
# Optional flood: proves the CALLER suppresses hook output (v2.1.247 class).
if [ -n "${CURL_STUB_FLOOD:-}" ]; then
  head -c 200000 /dev/zero | tr '\0' 'x'
  head -c 200000 /dev/zero | tr '\0' 'y' >&2
fi
exit "${CURL_STUB_EXIT:-0}"
STUB
  chmod +x "$STUB_BIN/curl"

  # Loopback port 1: unroutable and unbound by construction. Nothing ever
  # connects to it (curl is stubbed) — it exists so that a future regression
  # which somehow reached the real curl still could not contact a live host.
  UNREACHABLE_URL="https://127.0.0.1:1/parliament-fixture-never-contacted"

  # nt_run <label> <event> <url|""> <flood 0|1> <curl-exit-code>
  #   -> sets NT_RC and NT_OUT
  #
  # flood and curl-exit are SEPARATE parameters (testing-tyrant, v1.27.0). They
  # used to be one: passing flood=1 set CURL_STUB_FLOOD=1 *and* CURL_STUB_EXIT=1,
  # so "notify_teams suppresses curl's output" and "notify_teams tolerates a
  # failing webhook" were only ever asserted JOINTLY. That is a confounded
  # experiment: a notify_teams.sh that suppressed output only on its error path
  # would satisfy the combined case while still spraying a successful curl's
  # output into the session, and this fixture could not tell the difference.
  # They are now exercised independently.
  nt_run() {
    local label="$1" event="$2" url="$3" flood="$4" curl_exit="$5" rc
    rm -f "$STUB_MARKER" "$STUB_PAYLOAD" "$STUB_URL" "$STUB_ARGV"
    NT_OUT="$BASE_TMP/nt-$label.out"
    local -a envcmd
    # `env -u` must precede any NAME=VALUE operand: option parsing stops at the
    # first assignment, so a trailing -u would be read as the command name.
    envcmd=(env)
    if [ -z "$url" ]; then envcmd+=(-u TEAMS_WEBHOOK_URL); fi
    envcmd+=("PATH=$STUB_BIN:$PATH"
             "CURL_STUB_MARKER=$STUB_MARKER"
             "CURL_STUB_PAYLOAD=$STUB_PAYLOAD"
             "CURL_STUB_URL=$STUB_URL"
             "CURL_STUB_ARGV=$STUB_ARGV"
             "CURL_STUB_EXIT=$curl_exit")
    if [ -n "$url" ]; then envcmd+=("TEAMS_WEBHOOK_URL=$url"); fi
    if [ "$flood" = "1" ]; then envcmd+=("CURL_STUB_FLOOD=1"); fi
    # Payload via a FILE, not a pipe: notify_teams.sh exits before reading stdin
    # in two of these cases (no webhook configured, non-https scheme), so a pipe
    # would race SIGPIPE into the producer and, under `pipefail`, turn a correct
    # exit 0 into a spurious 141.
    local payload_file="$BASE_TMP/nt-$label.payload.json"
    jq -n --arg e "$event" --arg cwd "$REPO_ROOT" \
       '{hook_event_name: $e, session_id: "fixture-session", cwd: $cwd}' > "$payload_file"
    set +e
    "${envcmd[@]}" bash "$NOTIFY_TEAMS" <"$payload_file" >"$NT_OUT" 2>&1
    rc=$?
    set -e
    NT_RC="$rc"
  }

  # argv_has <token>... : true if ANY token appears as a whole argument in the
  # stub's recorded argv. Whole-argument matching (space-delimited), not
  # substring: a substring test would match "--max-time" inside an unrelated
  # value and quietly turn these assertions decorative.
  argv_has() {
    local joined t
    [ -f "$STUB_ARGV" ] || return 1
    joined=" $(tr '\n' ' ' < "$STUB_ARGV") "
    for t in "$@"; do
      case "$joined" in *" $t "*) return 0 ;; esac
    done
    return 1
  }

  # 1. No webhook configured: silent no-op. This is the default state for every
  #    user who never sets TEAMS_WEBHOOK_URL, so it must be perfectly quiet.
  nt_run "unconfigured" "Stop" "" 0 0
  [ "$NT_RC" -eq 0 ] || fail "notify_teams (no webhook configured): exited $NT_RC, expected 0"
  [ ! -f "$STUB_MARKER" ] || fail "notify_teams (no webhook configured): invoked curl — it must not"
  assert_output_silent "notify_teams (no webhook configured)" "$NT_OUT" || true

  # 2. Scheme guard: a non-https webhook must be refused BEFORE any request.
  #    Exit 1 is the script's documented, deliberate behaviour here — a
  #    misconfigured webhook is a config error the user should see, unlike a
  #    telemetry-write failure.
  nt_run "insecure-scheme" "Stop" "http://insecure.invalid/hook" 0 0
  [ "$NT_RC" -eq 1 ] || fail "notify_teams (http:// webhook): exited $NT_RC, expected 1 (scheme guard)"
  [ ! -f "$STUB_MARKER" ] || fail "notify_teams (http:// webhook): invoked curl — the scheme guard must refuse first"
  assert_output_silent "notify_teams (http:// webhook)" "$NT_OUT" || true

  # 3. Allowlist: an unknown event produces no webhook at all.
  nt_run "unknown-event" "TotallyUnknownEvent" "$UNREACHABLE_URL" 0 0
  [ "$NT_RC" -eq 0 ] || fail "notify_teams (unknown event): exited $NT_RC, expected 0"
  [ ! -f "$STUB_MARKER" ] || fail "notify_teams (unknown event): invoked curl — allowlist rejection broken"
  assert_output_silent "notify_teams (unknown event)" "$NT_OUT" || true

  # 4. FLOOD, curl SUCCEEDS. Isolates output suppression from failure tolerance:
  #    the stub sprays ~400KB across stdout and stderr and exits 0, so a
  #    notify_teams.sh that only suppresses output on its error path fails HERE
  #    and nowhere else. This is the v2.1.247 session-overflow assertion on the
  #    one hook capable of page-sized output, and the assertion is SILENT (0
  #    bytes), not merely bounded — the caller redirects curl wholesale, so
  #    there is no legitimate byte for it to emit.
  nt_run "flooding-webhook" "Stop" "$UNREACHABLE_URL" 1 0
  [ "$NT_RC" -eq 0 ] || fail "notify_teams (flooding webhook, curl exit 0): exited $NT_RC, expected 0"
  if [ -f "$STUB_MARKER" ]; then
    pass "notify_teams (known event): webhook invoked"
    if jq -e '.title == "Claude Code: task complete" and (.text | type == "string")' \
         "$STUB_PAYLOAD" >/dev/null 2>&1; then
      pass "notify_teams: payload is valid JSON with the expected title"
    else
      fail "notify_teams: payload malformed or wrong title: $(head -c 200 "$STUB_PAYLOAD" 2>/dev/null)"
    fi
    [ "$(cat "$STUB_URL")" = "$UNREACHABLE_URL" ] \
      || fail "notify_teams: webhook URL not passed through as the final curl argument"

    # --- Invocation-shape assertions on the RECORDED ARGV ---------------------
    # (testing-tyrant, v1.27.0.) Everything above tests the stub's behaviour.
    # These test the caller's REQUEST SAFETY, which is the one property stubbing
    # structurally hides — and the reason the hidden property matters is that it
    # is the worse hazard: a production curl with NO timeout, pointed at a
    # webhook host that blackholes packets rather than refusing them, hangs the
    # hook, and a hung hook hangs the session. A stub always returns instantly,
    # so no amount of behavioural testing here can ever surface that. Worse, a
    # file that LOOKS thoroughly covered is less likely to be read for the flaw.
    # The stub records argv precisely so the shape can be asserted for free.
    if argv_has --max-time -m; then
      pass "notify_teams: curl invoked with an explicit timeout (--max-time/-m)"
    else
      fail "notify_teams: curl invoked WITHOUT a timeout flag (--max-time or -m)." \
           "A webhook host that blackholes packets instead of refusing them will hang this curl," \
           "and a hung hook hangs the SESSION — the real-world hazard a stubbed curl can never" \
           "reproduce. Fix src/hooks/notify_teams.sh, not this assertion." \
           "Recorded argv: $(tr '\n' ' ' < "$STUB_ARGV")"
    fi
    if argv_has -sS -Ss -s --silent; then
      pass "notify_teams: curl invoked with a silent flag (progress meter suppressed)"
    else
      fail "notify_teams: curl invoked WITHOUT -s/--silent — the progress meter is written to" \
           "stderr on every event. Recorded argv: $(tr '\n' ' ' < "$STUB_ARGV")"
    fi
    if argv_has -sS -Ss -S --show-error; then
      pass "notify_teams: curl invoked with a show-error flag (failures are diagnosable)"
    else
      fail "notify_teams: curl invoked WITHOUT -S/--show-error — combined with -s this discards" \
           "the reason for every webhook failure. Recorded argv: $(tr '\n' ' ' < "$STUB_ARGV")"
    fi
  else
    fail "notify_teams (known event): curl was never invoked — the Stop event should produce a webhook"
  fi
  assert_output_silent "notify_teams (flooding webhook, curl exit 0)" "$NT_OUT" || true
  # Secret hygiene: the webhook URL must never be echoed into hook output.
  if grep -qF "$UNREACHABLE_URL" "$NT_OUT" 2>/dev/null; then
    fail "notify_teams: leaked the webhook URL into hook output"
  else
    pass "notify_teams: webhook URL not leaked into hook output"
  fi

  # 5. QUIET, curl FAILS. The other half of the split: a failing webhook must
  #    never fail the session. Deliberately degraded, so this is one of only two
  #    cases assert_output_bounded (rather than _silent) applies to — a single
  #    line of diagnostic about a failed webhook would be defensible here, though
  #    the current script emits none.
  nt_run "failing-webhook" "Stop" "$UNREACHABLE_URL" 0 1
  [ "$NT_RC" -eq 0 ] \
    || fail "notify_teams (failing webhook, curl exit 1): exited $NT_RC, expected 0 — a webhook failure must never fail the session"
  [ -f "$STUB_MARKER" ] \
    || fail "notify_teams (failing webhook): curl was never invoked — the Stop event should produce a webhook"
  assert_output_bounded "notify_teams (failing webhook, curl exit 1)" "$NT_OUT" || true
  if grep -qF "$UNREACHABLE_URL" "$NT_OUT" 2>/dev/null; then
    fail "notify_teams (failing webhook): leaked the webhook URL into hook output"
  else
    pass "notify_teams (failing webhook): webhook URL not leaked into hook output"
  fi
fi

# --- Verdict ----------------------------------------------------------------
echo
# The verdict must never claim coverage the run did not execute (testing-tyrant,
# v1.27.0). SKIPPED is surfaced in every branch, and the coverage list is only
# printed in full when nothing was skipped.
if [ "$FAILURES" -gt 0 ]; then
  echo "hook-fixture: FAILED ($FAILURES assertion(s) failed, $SKIPPED case group(s) skipped)" >&2
  [ "$SKIPPED" -eq 0 ] || echo "hook-fixture: skipped case group(s): $SKIP_LABELS" >&2
  exit 1
fi
if [ "$SKIPPED" -gt 0 ]; then
  echo "hook-fixture: PASSED WITH SKIPS — $SKIPPED case group(s) NOT run: $SKIP_LABELS" \
       "(see the SKIP line(s) above for why). Everything that ran passed:" \
       "${#EVENTS[@]} events, allowlist rejection, rotation, permissions, output silence on" \
       "healthy paths. This is NOT full coverage; CI (ubuntu-latest, non-root, no .env)" \
       "runs every case group."
  exit 0
fi
echo "hook-fixture: PASSED (${#EVENTS[@]} events, allowlist rejection, rotation, permissions," \
     "silent output on healthy paths and <= ${MAX_HOOK_OUTPUT_BYTES}B on degraded ones," \
     "unwritable-dir degradation, notify_teams via stubbed curl incl. curl invocation shape;" \
     "0 skipped)"
