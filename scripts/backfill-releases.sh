#!/usr/bin/env bash
# Backfill missing GitHub releases and git tags from CHANGELOG.md.
#
# Idempotent: re-running skips versions that already have a tag AND a release.
# Reads CHANGELOG.md as the single source of truth for release notes.
# Resolves commit SHAs via the project's "vX.Y.Z: ..." commit-message convention,
# with explicit overrides for versions that predate the convention.
#
# Usage:
#   scripts/backfill-releases.sh [--dry-run]
#
# Requirements: git, gh (authenticated), bash 3.2+ (macOS-default compatible).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANGELOG="${REPO_ROOT}/CHANGELOG.md"
DRY_RUN=0
TODAY="$(date -u +%Y-%m-%d)"

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  echo "==> DRY RUN — no tags or releases will be created"
fi

if [[ ! -f "${CHANGELOG}" ]]; then
  echo "ERROR: ${CHANGELOG} not found" >&2
  exit 1
fi

cd "${REPO_ROOT}"

# Versions that predate the "vX.Y.Z: ..." commit-message convention need explicit
# SHA overrides. v1.0.0/v1.1.0 already have GitHub releases (V1.0.0/V1.1.0) but no
# lowercase tag; v1.2.0 has no dedicated commit per its CHANGELOG note.
override_sha() {
  case "$1" in
    1.0.0) git rev-parse V1.0.0^{commit} ;;
    1.1.0) git rev-parse V1.1.0^{commit} ;;
    1.2.0) git rev-parse V1.1.0^{commit} ;;  # CHANGELOG: "no user-facing changes beyond 1.1.0"
    *) return 1 ;;
  esac
}

# Resolve the SHA for a version: override map first, then commit-message grep.
resolve_sha() {
  local version="$1"
  local sha
  if sha="$(override_sha "${version}" 2>/dev/null)"; then
    echo "${sha}"
    return 0
  fi
  sha="$(git log --all --grep="^v${version}:" --pretty=format:"%H" -n 1 || true)"
  if [[ -z "${sha}" ]]; then
    return 1
  fi
  echo "${sha}"
}

# Extract the CHANGELOG section for a single version. Output is the body between
# "## [X.Y.Z] - DATE" (exclusive) and the next "## [" heading (exclusive).
extract_changelog_section() {
  local version="$1"
  awk -v target="[${version}]" '
    /^## \[/ {
      if (in_section) exit
      if (index($0, target)) { in_section=1; next }
    }
    in_section { print }
  ' "${CHANGELOG}"
}

# Extract the "YYYY-MM-DD" date from the heading line for a version.
extract_changelog_date() {
  local version="$1"
  grep -m1 "^## \[${version}\]" "${CHANGELOG}" | sed -E 's/.* - ([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/'
}

tag_exists() {
  git rev-parse --verify --quiet "refs/tags/$1" >/dev/null 2>&1
}

release_exists() {
  gh release view "$1" >/dev/null 2>&1
}

# Parse all versions from CHANGELOG (oldest first for chronological tagging).
versions=()
while IFS= read -r line; do
  v="$(echo "${line}" | sed -E 's/^## \[([0-9]+\.[0-9]+\.[0-9]+)\].*/\1/')"
  versions=("${v}" "${versions[@]:-}")
done < <(grep "^## \[[0-9]" "${CHANGELOG}")

# Trim any trailing empty element (bash 3.2 quirk with empty-array expansion).
clean_versions=()
for v in "${versions[@]}"; do
  [[ -n "${v}" ]] && clean_versions+=("${v}")
done
versions=("${clean_versions[@]}")

# Pick the highest version as the --latest target.
latest_version="${versions[${#versions[@]}-1]}"

echo "==> Found ${#versions[@]} versions in CHANGELOG.md (oldest -> newest):"
printf '    %s\n' "${versions[@]}"
echo "==> --latest=true will be set on: v${latest_version}"
echo

planned_tags=()
planned_releases=()
skipped=()

for version in "${versions[@]}"; do
  tag="v${version}"
  sha="$(resolve_sha "${version}" || true)"

  if [[ -z "${sha}" ]]; then
    echo "  SKIP v${version}: no commit found (no override, no 'v${version}:' commit message)"
    skipped+=("${version}: no SHA")
    continue
  fi

  has_tag=0
  has_release=0
  tag_exists "${tag}" && has_tag=1
  release_exists "${tag}" && has_release=1

  # Also check for the legacy uppercase release for v1.0.0 / v1.1.0.
  legacy_tag="V${version}"
  has_legacy_release=0
  if [[ "${version}" == "1.0.0" || "${version}" == "1.1.0" ]]; then
    release_exists "${legacy_tag}" && has_legacy_release=1
  fi

  status_bits=()
  [[ ${has_tag} -eq 1 ]] && status_bits+=("tag:${tag} exists")
  [[ ${has_release} -eq 1 ]] && status_bits+=("release:${tag} exists")
  [[ ${has_legacy_release} -eq 1 ]] && status_bits+=("legacy release:${legacy_tag} exists (preserved)")

  echo "  v${version} -> ${sha:0:10}  [${status_bits[*]:-needs both}]"

  if [[ ${has_tag} -eq 0 ]]; then
    planned_tags+=("${tag}|${sha}")
  fi
  # Skip release creation if either lowercase release or legacy uppercase release exists.
  if [[ ${has_release} -eq 0 && ${has_legacy_release} -eq 0 ]]; then
    planned_releases+=("${tag}|${sha}|${version}")
  fi
done

echo
echo "==> Plan: create ${#planned_tags[@]} new tag(s), create ${#planned_releases[@]} new release(s)"
echo

if [[ ${DRY_RUN} -eq 1 ]]; then
  echo "==> Dry run complete. Re-run without --dry-run to apply."
  exit 0
fi

# Phase 1: create tags.
for entry in "${planned_tags[@]:-}"; do
  [[ -z "${entry}" ]] && continue
  tag="${entry%%|*}"
  sha="${entry##*|}"
  echo "  tagging ${tag} -> ${sha:0:10}"
  git tag "${tag}" "${sha}"
done

# Phase 2: create releases.
for entry in "${planned_releases[@]:-}"; do
  [[ -z "${entry}" ]] && continue
  IFS='|' read -r tag sha version <<<"${entry}"

  changelog_date="$(extract_changelog_date "${version}")"
  body_file="$(mktemp -t backfill-release.XXXXXX)"
  trap 'rm -f "${body_file}"' EXIT

  {
    echo "> Originally released **${changelog_date}** (per CHANGELOG.md). Backfilled to GitHub on ${TODAY}; the GitHub \"published at\" timestamp on this release reflects the backfill run, not the original release date."
    echo
    extract_changelog_section "${version}"
  } >"${body_file}"

  latest_flag="--latest=false"
  if [[ "${version}" == "${latest_version}" ]]; then
    latest_flag="--latest=true"
  fi

  echo "  creating release ${tag} (target ${sha:0:10}, ${latest_flag})"
  gh release create "${tag}" \
    --target "${sha}" \
    --title "${tag}" \
    --notes-file "${body_file}" \
    ${latest_flag}

  rm -f "${body_file}"
  trap - EXIT
done

# Phase 3: push tags.
if [[ ${#planned_tags[@]} -gt 0 ]]; then
  echo
  echo "==> Pushing new tags to origin"
  git push origin --tags
fi

echo
echo "==> Done."
echo "    Tags now: $(git tag --list | wc -l | tr -d ' ')"
echo "    Releases now: $(gh release list --limit 100 | wc -l | tr -d ' ')"

if [[ ${#skipped[@]} -gt 0 ]]; then
  echo
  echo "==> Skipped:"
  printf '    %s\n' "${skipped[@]}"
fi
