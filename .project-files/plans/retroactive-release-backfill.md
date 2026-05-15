# Retroactive GitHub Release Backfill

## Goal

The Parliament of Chaos repository has 21 versions documented in `CHANGELOG.md` (`1.0.0` through `1.20.0`) but only **3 GitHub releases** (`V1.0.0`, `V1.1.0`, `v1.14.0`) and **3 git tags** (same set). This means **18 versions** ship without a discoverable GitHub release page or stable tag. The goal is to backfill those 18 missing releases so every documented version has a tag pointing at the correct commit and a GitHub release whose body is the corresponding `CHANGELOG.md` section. "Done" means: `git tag --list` returns 21 tags, `gh release list` returns 21 releases, and every release body links to a real commit.

## Existing Capabilities Found

- `/Users/jack/Parliament-Of-Chaos/CHANGELOG.md` — Keep-a-Changelog formatted, 21 version sections from 1.0.0 to 1.20.0. Every section is delimited by `## [X.Y.Z] - YYYY-MM-DD` heading. Single source of truth for release notes.
- `/Users/jack/Parliament-Of-Chaos/RELEASE_INSTRUCTIONS.md` — Manual release checklist. Step "Post-Push: Create GitHub Release" describes exactly the operation we are backfilling, but is human-driven and does not address the historical gap. Does not create tags / releases itself.
- `/Users/jack/Parliament-Of-Chaos/RELEASE_NOTES_v1.1.0.md` — One-off release notes file for v1.1.0. Confirms convention of "release body = changelog section" for at least that version.
- `/Users/jack/Parliament-Of-Chaos/commands/cut-release.md` — `/cut-release` slash command for cutting **new** releases (forward-looking). Does not handle backfill.
- `/Users/jack/Parliament-Of-Chaos/commands/release-notes-draft.md` — `/release-notes-draft` drafts CHANGELOG entries from git log. Forward-looking. Does not handle backfill.
- `/Users/jack/Parliament-Of-Chaos/commands/plugin-upgrade.md` — `/plugin-upgrade --tag` uses `claude plugin tag` for upstream-validated tag creation on **new** releases. Does not handle backfill.
- Git history — Every release commit since v1.3.0 follows the convention `vX.Y.Z: <summary>`, making SHA resolution trivial via `git log --grep`.
- Existing tags: `V1.0.0` (uppercase), `V1.1.0` (uppercase), `v1.14.0` (lowercase). Existing GitHub releases: `V1.0.0`, `V1.1.0`. Note: there is a `v1.14.0` git tag but **no** corresponding GitHub release.

## Reuse Decision

- **EXTEND `CHANGELOG.md` as the release-body source** — already structured for this; we slice each `## [X.Y.Z]` section verbatim into the matching release.
- **EXTEND the `vX.Y.Z:` commit-message convention** for SHA resolution — already enforced by the project, makes backfill trivially mechanical.
- **CREATE a one-off backfill script** at `scripts/backfill-releases.sh` — no existing analogue. `/cut-release`, `/release-notes-draft`, and `/plugin-upgrade` are all forward-looking. A backfill is a distinct concern (read CHANGELOG, resolve historical SHAs, create missing tags, create missing releases without re-creating the three that exist) and one-shot in nature. Keeping it as a script (not a slash command) is the right scope: this is a one-time cleanup, not a recurring capability. If a similar backfill is needed on another plugin/project later, the script is portable and trivially copyable.

## Options Considered

### Option A — Manual `gh release create` per version (20-line bash loop, one-shot)

- **Pros**: Minimal tooling, immediate, transparent.
- **Cons**: No retry safety, no verification step, no per-version log.

### Option B — Standalone backfill script (`scripts/backfill-releases.sh`)

- **Pros**: Idempotent (skips existing tags / releases), verifies every step, reads CHANGELOG as single source of truth, leaves an artifact on disk for posterity, reproducible if a future cleanup is needed on another project.
- **Cons**: ~80 lines of bash to maintain (but it's a one-shot — maintenance cost is near zero after the run).

### Option C — New slash command `/backfill-releases`

- **Pros**: Reusable across plugins, integrates with Parliament conventions.
- **Cons**: Over-engineered for a one-time cleanup. Builds infrastructure for a use case that may never recur on this repo. Carries the cost of a new manifest entry, documentation, and a long-tail maintenance burden.

## Recommended Approach

**Option B** — write a one-shot `scripts/backfill-releases.sh` that:

1. Parses every `## [X.Y.Z] - YYYY-MM-DD` heading from `CHANGELOG.md` (21 versions).
2. For each version, resolves the commit SHA via `git log --grep="^v${V}:" -n 1`. For versions that predate the `vX.Y.Z:` commit-message convention (v1.0.0, v1.1.0, v1.2.0), uses an explicit override map.
3. Skips any version that already has a git tag **and** a GitHub release (idempotent re-runs).
4. For missing tags: `git tag vX.Y.Z <sha>`.
5. Extracts the CHANGELOG section between `## [X.Y.Z]` and the next `## [` heading.
6. Prepends a one-line preamble: `> Originally released **YYYY-MM-DD** (per CHANGELOG). Backfilled to GitHub on YYYY-MM-DD; the published-at timestamp on this release reflects the backfill run, not the original release date.`
7. Calls `gh release create vX.Y.Z --target <sha> --notes-file <tmp> --latest=false` for everything except the most recent (`v1.20.0`), which gets `--latest=true`.
8. Pushes all new tags to `origin` at the end (`git push origin --tags`).

**Tag-case policy**: Use lowercase `vX.Y.Z` for new tags (matches the existing `v1.14.0` and the project's commit-message convention). Leave `V1.0.0` and `V1.1.0` GitHub releases as-is — do **not** rename or re-create them, because their existing URLs are public and may be referenced externally. This results in a mixed-case set of three legacy releases (`V1.0.0`, `V1.1.0`, lowercase `v1.14.0`) plus 18 lowercase backfilled releases. The split is documented in this plan and in the script's banner.

**v1.2.0 SHA resolution**: The CHANGELOG entry for 1.2.0 says "Version bump for marketplace registration … no user-facing changes beyond 1.1.0." There is no `v1.2.0:` commit. Use the V1.1.0 tag commit (`0ee9c27`) as the target — defensible because the changelog itself states this version contains no incremental code change. Document the mapping in the release body.

**v1.0.0 / v1.1.0 SHA resolution**: Use the existing `V1.0.0` and `V1.1.0` tag commits. These releases already exist on GitHub, so no new release is created — but lowercase `v1.0.0` and `v1.1.0` git tags are added for naming consistency going forward. Document this dual-tag situation in the release-script log.

## Risks & Trade-offs

- **Cosmetic timestamps**: GitHub's "published at" field is server-set at creation time and is not user-writable via the API. Every backfilled release will show today's date as its publish date. This is unavoidable. Mitigation: every backfilled release body opens with a "Originally released YYYY-MM-DD" line.
- **Mixed tag case**: We will end up with `V1.0.0`, `V1.1.0`, and 19 lowercase tags (`v1.0.0` through `v1.20.0`, including a duplicate-content lowercase `v1.0.0` and `v1.1.0`). Trade-off: breaking the existing uppercase URLs is worse than the inconsistency. We accept the cosmetic mismatch.
- **`--latest` flag**: GitHub computes "latest" by SemVer when `--latest` is unset on releases. Explicitly setting `--latest=false` for all except `v1.20.0` and `--latest=true` for `v1.20.0` makes the result deterministic and prevents the existing `V1.1.0` "Latest" badge from drifting during the run.
- **Script idempotency vs partial-run recovery**: If the script aborts mid-run (rate limit, network), the next invocation must skip what already succeeded. This is handled by checking `git tag --list` and `gh release view` before each step.
- **Push of 18 new tags**: A single `git push origin --tags` push is fine; no force-push needed.
- **No new agents, no settings.json changes, no hook changes**: The script is a developer tool, not a Parliament command — does not need a manifest entry.

## Suggested Task Breakdown

1. Write `scripts/backfill-releases.sh` implementing the recommended approach. Include a `--dry-run` flag that prints the plan without creating tags or releases.
2. Run the script with `--dry-run` first; verify the version-to-SHA map and the planned actions match this plan.
3. Run the script for real. Capture stdout/stderr to a log file.
4. Verify with `git tag --list | sort -V` (expect 21 tags) and `gh release list --limit 30` (expect 21 releases).
5. Push tags: `git push origin --tags`.
6. Spot-check three release pages on GitHub: oldest backfilled (v1.2.0), middle (v1.10.0), newest (v1.20.0). Confirm preamble + CHANGELOG body render correctly.

## Open Questions

None — the V1.0.0 / V1.1.0 dual-case decision is locked in (preserve existing uppercase URLs, add lowercase tags going forward), the v1.2.0 → V1.1.0-commit mapping is defensible from the changelog text, and `--latest` flag handling is explicit. Proceed to implementation.
