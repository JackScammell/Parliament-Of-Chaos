#!/usr/bin/env bash
# ============================================================================
# Parliament of Chaos — headless install smoke test ("The Gate", v1.26.0)
#
# Proves the plugin actually LOADS on a real `claude` install, with no API key,
# using a throwaway CLAUDE_CONFIG_DIR. This exact check catches the v1.25.0
# incident class: on that release, `claude plugin list` showed "failed to load"
# where a healthy install shows "enabled" + the version.
#
# Dual-use by design:
#   CI      : scripts/ci/install_smoke.sh                  (defaults: repo checkout)
#   Release : scripts/ci/install_smoke.sh \
#               --source https://github.com/JackScammell/Parliament-Of-Chaos.git \
#               --expected-version X.Y.Z
#             (the RELEASE_INSTRUCTIONS.md "Post-release verification" step)
#
# Assertion philosophy (upstream-version-coupling mitigation):
#   - Substring, case-insensitive checks on words: "enabled", the version
#     string, absence of "fail". NEVER glyphs ("✔"/"✘") or column layout —
#     those drift across CLI releases.
#   - `claude plugin validate` presence is ASSERTED, not feature-detected, when
#     the caller knows the pin guarantees it (REQUIRE_PLUGIN_VALIDATE=1, set by
#     The Gate's pinned install-smoke job). Feature detection survives only for
#     the dual-use local path, where the user's CLI may genuinely predate the
#     subcommand. Rationale: `--help`-based detection is a weak signal — a CLI
#     that exits 0 on an unrecognised subcommand's --help yields a false
#     positive, and the real failure then misreports as "validate reported
#     errors" instead of "not available".
#   - stdin is closed off SCRIPT-WIDE via `exec 0</dev/null` immediately below,
#     not per call site. Upstream v2.1.246 fixed a class where a CLI call could
#     block waiting on input; with stdin at EOF, any such prompt fails
#     IMMEDIATELY instead of hanging until the job's timeout-minutes budget is
#     exhausted. Non-interactive is asserted here, not assumed. The per-call
#     `</dev/null` redirects are KEPT as belt-and-braces (they are explicit at
#     the point of risk and survive code extraction), but correctness no longer
#     depends on remembering one: a convention that must be re-applied to every
#     new call site is a convention that drifts.
#
# Not verified by this script (green here is NOT full validation):
#   - Hooks firing inside a live session (needs an API key + a real turn)
#   - Prompt/agent semantics, command behaviour, review quality
#   - macOS installs (CI runs Linux only)
# ============================================================================
set -euo pipefail

# Close stdin ONCE, for the whole script and everything it spawns (v1.27.0).
# This supersedes the per-call `</dev/null` convention as the load-bearing
# guard: enumerating call sites is a maintenance burden that silently regresses
# the first time someone adds a `claude` call without reading the header comment
# — the same enumerate-the-literals anti-pattern that has already bitten this
# repo elsewhere. The per-call redirects below are retained as documentation and
# defence-in-depth, but no longer carry the invariant.
exec 0</dev/null

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

usage() {
  cat <<'EOF'
Usage: install_smoke.sh [--source <path-or-git-url>] [--expected-version <X.Y.Z>] [--keep-config]

  --source            Marketplace source. Local path (CI default: repo root) or git URL
                      (post-release verification). Default: the repo containing this script.
  --expected-version  Version that must appear in `claude plugin list`. Default: read from
                      <source>/.claude-plugin/plugin.json when source is a local directory,
                      else from this checkout's plugin.json.
  --keep-config       Do not delete the throwaway CLAUDE_CONFIG_DIR (debugging).
EOF
}

SOURCE="$REPO_ROOT"
EXPECTED_VERSION=""
KEEP_CONFIG=0

while [ $# -gt 0 ]; do
  case "$1" in
    --source)           SOURCE="$2"; shift 2 ;;
    --expected-version) EXPECTED_VERSION="$2"; shift 2 ;;
    --keep-config)      KEEP_CONFIG=1; shift ;;
    -h|--help)          usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for tool in claude jq; do
  command -v "$tool" >/dev/null 2>&1 || { echo "ERROR: required tool not found: $tool" >&2; exit 2; }
done

FAILURES=0
fail() { echo "FAIL: $*" >&2; FAILURES=$((FAILURES + 1)); }
pass() { echo "  ok: $*"; }

# --- Resolve source, names, expected version --------------------------------
SOURCE_IS_LOCAL=0
if [ -d "$SOURCE" ]; then
  SOURCE="$(cd "$SOURCE" && pwd)"
  SOURCE_IS_LOCAL=1
fi

PLUGIN_NAME="chaos"
MARKETPLACE_NAME="chaos"
if [ "$SOURCE_IS_LOCAL" -eq 1 ]; then
  PLUGIN_NAME="$(jq -r '.name' "$SOURCE/.claude-plugin/plugin.json")"
  MARKETPLACE_NAME="$(jq -r '.name' "$SOURCE/.claude-plugin/marketplace.json")"
fi

if [ -z "$EXPECTED_VERSION" ]; then
  if [ "$SOURCE_IS_LOCAL" -eq 1 ]; then
    EXPECTED_VERSION="$(jq -r '.version' "$SOURCE/.claude-plugin/plugin.json")"
  else
    EXPECTED_VERSION="$(jq -r '.version' "$REPO_ROOT/.claude-plugin/plugin.json")"
    echo "NOTE: --expected-version not given for a remote source; using this checkout's" \
         "plugin.json ($EXPECTED_VERSION). Pass it explicitly when verifying a release." >&2
  fi
fi
[ -n "$EXPECTED_VERSION" ] && [ "$EXPECTED_VERSION" != "null" ] \
  || { echo "ERROR: could not resolve expected version" >&2; exit 2; }

echo "== install-smoke: plugin='$PLUGIN_NAME' marketplace='$MARKETPLACE_NAME'" \
     "expected-version='$EXPECTED_VERSION' source='$SOURCE'"

# --- Static pre-flight checks on the source (local sources only) ------------
if [ "$SOURCE_IS_LOCAL" -eq 1 ]; then
  # v1.25.0 incident class, static half: plugin.json's `hooks` field must not
  # reference hooks/hooks.json — Claude Code auto-loads that conventional path,
  # and referencing it again double-registers the hooks and the plugin fails to
  # load (the v1.25.0 -> v1.25.1 hotfix).
  if jq -e 'has("hooks")' "$SOURCE/.claude-plugin/plugin.json" >/dev/null; then
    if jq -r '.hooks | if type == "array" then .[] else . end' \
         "$SOURCE/.claude-plugin/plugin.json" | grep -q 'hooks/hooks\.json'; then
      fail "plugin.json 'hooks' field references hooks/hooks.json (auto-loaded path) — duplicate registration, v1.25.0 incident class"
    else
      pass "plugin.json 'hooks' field present but does not duplicate hooks/hooks.json"
    fi
  else
    pass "plugin.json has no 'hooks' field (hooks/hooks.json auto-load only)"
  fi

  # RELEASE_INSTRUCTIONS gotcha: hook scripts must be executable.
  # Exemption: _-prefixed files (e.g. _common.sh) are SOURCED helpers, never
  # executed by the harness, so the executable bit is not required on them.
  for hook_script in "$SOURCE"/src/hooks/*.sh; do
    case "$(basename "$hook_script")" in _*) continue ;; esac
    [ -x "$hook_script" ] || fail "hook script not executable: $hook_script"
  done
  pass "src/hooks/*.sh executable-bit check done (sourced _* helpers exempt)"
fi

# --- Isolated headless install (proven flow, no API key) --------------------
CLAUDE_CONFIG_DIR="$(mktemp -d)"
export CLAUDE_CONFIG_DIR
export DISABLE_AUTOUPDATER=1
# CI hygiene: the claude CLI must not phone home from the gate (security review).
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export DISABLE_TELEMETRY=1
cleanup() { [ "$KEEP_CONFIG" -eq 1 ] || rm -rf "$CLAUDE_CONFIG_DIR"; }
trap cleanup EXIT

echo "== using throwaway CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR"

if ! claude plugin marketplace add "$SOURCE" </dev/null; then
  echo "ERROR: 'claude plugin marketplace add $SOURCE' failed" >&2
  exit 1
fi
pass "marketplace add"

if ! claude plugin install "${PLUGIN_NAME}@${MARKETPLACE_NAME}" </dev/null; then
  echo "ERROR: 'claude plugin install ${PLUGIN_NAME}@${MARKETPLACE_NAME}' failed" >&2
  exit 1
fi
pass "plugin install"

# --- Assertions on `claude plugin list` -------------------------------------
LIST_OUTPUT="$(claude plugin list </dev/null 2>&1 || true)"
echo "---- claude plugin list ----"
echo "$LIST_OUTPUT"
echo "----------------------------"

# Scope assertions to the lines around our plugin's entry, so an unrelated
# plugin's state cannot mask or trigger a failure.
PLUGIN_BLOCK="$(printf '%s\n' "$LIST_OUTPUT" | grep -iF -B1 -A3 -- "$PLUGIN_NAME" || true)"

if [ -z "$PLUGIN_BLOCK" ]; then
  fail "plugin '$PLUGIN_NAME' not present in 'claude plugin list' output"
else
  pass "plugin '$PLUGIN_NAME' listed"
  if printf '%s' "$PLUGIN_BLOCK" | grep -qi 'enabled'; then
    pass "plugin block contains 'enabled'"
  else
    fail "plugin block does not contain 'enabled' — v1.25.0 incident class (plugin did not load)"
  fi
  if printf '%s' "$PLUGIN_BLOCK" | grep -qi 'fail'; then
    fail "plugin block contains a failure marker ('fail...') — plugin did not load cleanly"
  else
    pass "no failure marker in plugin block"
  fi
  if printf '%s' "$PLUGIN_BLOCK" | grep -qF "$EXPECTED_VERSION"; then
    pass "version $EXPECTED_VERSION visible in plugin block"
  else
    fail "expected version '$EXPECTED_VERSION' not found in plugin block (stale marketplace cache or version desync)"
  fi
fi

# --- Duplicate hook registration, dynamic half ------------------------------
# Inspect every hooks manifest the install produced for this plugin. Multiple
# *copies* of hooks.json on disk (marketplace clone + installed copy) are fine;
# what must never happen is log_event.sh registered more than once FOR THE SAME
# EVENT within any single manifest.
MANIFESTS="$(find "$CLAUDE_CONFIG_DIR" -type f -name 'hooks.json' -path "*${PLUGIN_NAME}*" 2>/dev/null || true)"
if [ -z "$MANIFESTS" ]; then
  echo "NOTE: no hooks.json manifests found under CLAUDE_CONFIG_DIR (cache layout may have" \
       "drifted); relying on the 'enabled' assertion for the duplicate-registration class." >&2
else
  while IFS= read -r manifest; do
    # T2 (testing-tyrant, v1.26.0 review): a jq parse/shape error here must FAIL
    # the check, not silently produce an empty DUPES and a vacuous pass — the
    # check must exercise the invariant, not its own error suppression.
    if ! DUPES="$(jq -r '
      .hooks | to_entries[]
      | [.key, ([.value[].hooks[].command] | map(select(contains("log_event.sh"))) | length)]
      | select(.[1] > 1) | @tsv' "$manifest")"; then
      fail "could not parse installed hooks manifest $manifest (jq error) — cannot verify duplicate registration"
      continue
    fi
    if [ -n "$DUPES" ]; then
      fail "duplicate log_event.sh registration in $manifest:"$'\n'"$DUPES"
    else
      pass "no per-event duplicate registration in $manifest"
    fi
    # Re-run the static plugin.json check on the installed copy, if adjacent.
    installed_plugin_json="$(dirname "$manifest")/../.claude-plugin/plugin.json"
    if [ -f "$installed_plugin_json" ] \
       && jq -e 'has("hooks")' "$installed_plugin_json" >/dev/null 2>&1 \
       && jq -r '.hooks | if type == "array" then .[] else . end' "$installed_plugin_json" \
            | grep -q 'hooks/hooks\.json'; then
      fail "installed plugin.json duplicates hooks/hooks.json: $installed_plugin_json"
    fi
  done <<< "$MANIFESTS"
fi

# --- claude plugin validate ---------------------------------------------------
# Presence is ASSERTED where the caller knows the CLI pin guarantees it, and only
# feature-detected on the dual-use local path.
#
# Why not feature-detection everywhere (code-review L3, v1.27.0): `--help` is a
# weak probe. A CLI that exits 0 on an unrecognised subcommand's `--help` gives a
# false positive, after which a genuinely-absent subcommand misreports as
# "validate reported errors" — pointing the reader at the manifests when the real
# cause is the CLI. Worse, the failure that matters most (the pinned release job
# silently stopping running validate at all, because upstream renamed or removed
# the subcommand) degrades to a NOTE nobody reads.
#
# The Gate's pinned install-smoke job sets REQUIRE_PLUGIN_VALIDATE=1 because its
# CLAUDE_CLI_VERSION pin (>= 2.1.247) ships the subcommand. There, absence is a
# hard failure with an unambiguous message. Locally — and on the non-blocking
# canary — the default 0 keeps the old skip-with-NOTE behaviour, because a user's
# CLI may legitimately predate it.
#
# If validate starts reporting errors, fix the manifests — do not weaken this
# back to an unconditional skip.
REQUIRE_PLUGIN_VALIDATE="${REQUIRE_PLUGIN_VALIDATE:-0}"

HAVE_PLUGIN_VALIDATE=0
if claude plugin validate --help </dev/null >/dev/null 2>&1; then
  HAVE_PLUGIN_VALIDATE=1
fi

if [ "$HAVE_PLUGIN_VALIDATE" -eq 0 ]; then
  if [ "$REQUIRE_PLUGIN_VALIDATE" = "1" ]; then
    fail "'claude plugin validate' is NOT available on this CLI, but the caller set" \
         "REQUIRE_PLUGIN_VALIDATE=1 (the pinned CLI is documented to ship it)." \
         "Either upstream removed/renamed the subcommand — adopt the change and update" \
         "CLAUDE_CLI_VERSION in .github/workflows/gate.yml — or the pinned install did not" \
         "take effect. This is NOT a manifest error."
  else
    echo "NOTE: 'claude plugin validate' not available on this CLI version — skipped." \
         "(Not required on the dual-use local path; the pinned CI job sets" \
         "REQUIRE_PLUGIN_VALIDATE=1 and fails instead of skipping.)" >&2
  fi
elif [ "$SOURCE_IS_LOCAL" -eq 1 ]; then
  if claude plugin validate "$SOURCE" </dev/null; then
    pass "claude plugin validate"
  else
    fail "claude plugin validate reported errors"
  fi
else
  echo "NOTE: skipping 'claude plugin validate' for a remote source" >&2
fi

# --- Verdict ----------------------------------------------------------------
echo
if [ "$FAILURES" -gt 0 ]; then
  echo "install-smoke: FAILED ($FAILURES assertion(s) failed)" >&2
  exit 1
fi
echo "install-smoke: PASSED (plugin '$PLUGIN_NAME' v$EXPECTED_VERSION loads headlessly)"
