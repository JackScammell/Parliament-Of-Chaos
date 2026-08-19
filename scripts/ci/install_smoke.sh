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
#   - `claude plugin validate` is feature-detected, never required (absent on
#     CLI 2.1.197; may exist on newer versions).
#
# Not verified by this script (green here is NOT full validation):
#   - Hooks firing inside a live session (needs an API key + a real turn)
#   - Prompt/agent semantics, command behaviour, review quality
#   - macOS installs (CI runs Linux only)
# ============================================================================
set -euo pipefail

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

if ! claude plugin marketplace add "$SOURCE"; then
  echo "ERROR: 'claude plugin marketplace add $SOURCE' failed" >&2
  exit 1
fi
pass "marketplace add"

if ! claude plugin install "${PLUGIN_NAME}@${MARKETPLACE_NAME}"; then
  echo "ERROR: 'claude plugin install ${PLUGIN_NAME}@${MARKETPLACE_NAME}' failed" >&2
  exit 1
fi
pass "plugin install"

# --- Assertions on `claude plugin list` -------------------------------------
LIST_OUTPUT="$(claude plugin list 2>&1 || true)"
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

# --- Feature-detected: claude plugin validate (newer CLIs only) -------------
if claude plugin validate --help >/dev/null 2>&1; then
  if [ "$SOURCE_IS_LOCAL" -eq 1 ]; then
    if claude plugin validate "$SOURCE"; then
      pass "claude plugin validate"
    else
      fail "claude plugin validate reported errors"
    fi
  else
    echo "NOTE: skipping 'claude plugin validate' for a remote source" >&2
  fi
else
  echo "NOTE: 'claude plugin validate' not available on this CLI version — skipped (feature-detected, not required)" >&2
fi

# --- Verdict ----------------------------------------------------------------
echo
if [ "$FAILURES" -gt 0 ]; then
  echo "install-smoke: FAILED ($FAILURES assertion(s) failed)" >&2
  exit 1
fi
echo "install-smoke: PASSED (plugin '$PLUGIN_NAME' v$EXPECTED_VERSION loads headlessly)"
