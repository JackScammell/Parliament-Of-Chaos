# Release Checklist

Step-by-step checklist for releasing a new version of Parliament of Chaos. Follow every step — skipping any one has caused bugs in production before.

## Pre-Release: Version Bump

All three of these files must show the **same** version string. If any one is out of sync, `claude /plugin` will show the wrong version.

- [ ] `.claude-plugin/plugin.json` — `"version": "X.Y.Z"`
- [ ] `.claude-plugin/marketplace.json` — `metadata.version` **and** `plugins[0].version`
- [ ] `CHANGELOG.md` — new `## [X.Y.Z] - YYYY-MM-DD` section at top, plus `[X.Y.Z]:` compare link at bottom

**Verify with:**
```bash
grep -n '"version"' .claude-plugin/plugin.json .claude-plugin/marketplace.json
```
All three values must match.

## Pre-Release: Content Checks

- [ ] No stale install/update commands in docs (search for old command patterns):
  ```bash
  grep -rn 'install-github-plugin' --include='*.md' | grep -v CHANGELOG | grep -v RELEASE_NOTES
  ```
  Should return zero results (CHANGELOG/RELEASE_NOTES references are historical and OK).

- [ ] Hook paths use `src/hooks/` not `hooks/` in:
  - `hooks/hooks.json`
  - Agent frontmatter (`agents/*.md` — check `command:` lines)

  **Verify with:**
  ```bash
  grep -rn '"hooks/' hooks/hooks.json agents/
  ```
  Should return zero results.

- [ ] All files in `src/hooks/` are executable:
  ```bash
  ls -la src/hooks/*.sh
  ```

## Commit and Push

- [ ] Stage all changed files
- [ ] Commit with message: `vX.Y.Z: <summary of changes>`
- [ ] Push to `main`
- [ ] Verify push landed:
  ```bash
  git log origin/main --oneline -1
  ```

## Post-Push: Update Local Marketplace Cache

Claude Code's marketplace clone does **not** auto-pull on `marketplace add` if the clone already exists. You must manually pull.

```bash
cd ~/.claude/plugins/marketplaces/<marketplace-name> && git pull origin main && cd -   # name per `claude plugin marketplace list` (see Post-release verification note)
```

**Verify the cache has the new version:**
```bash
grep '"version"' ~/.claude/plugins/marketplaces/<marketplace-name>/.claude-plugin/plugin.json
```

## Post-Push: Verify in Claude Code

1. Open a fresh Claude Code session
2. Type `/plugin`
3. Navigate to **Discover** tab
4. Find `chaos`
5. Confirm version shows `X.Y.Z` (not the old version)

If it still shows the old version:
- The marketplace git clone is stale — re-run the `git pull` step above
- Check the **Errors** tab in `/plugin` for any parsing issues

## Post-Push: Create GitHub Release

1. Go to: https://github.com/JackScammell/Parliament-Of-Chaos/releases/new
2. **Tag**: `vX.Y.Z` (lowercase `v`)
3. **Target**: `main`
4. **Title**: `vX.Y.Z - <brief description>`
5. **Body**: Copy the relevant `CHANGELOG.md` section
6. **Options**: Set as latest release
7. Publish

## Post-Push: Test Fresh Install (Optional but Recommended)

On a machine that doesn't have the plugin installed:
```bash
claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
# A GitHub-URL add registers the marketplace under the REPO name:
claude plugin install chaos@parliament-of-chaos
```

Then verify:
- `/plugin` shows correct version
- `/list-agents` works
- `/summon-grumpy-reviewer` activates

---

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| `/plugin` shows old version | Marketplace git clone is stale | `cd ~/.claude/plugins/marketplaces/<marketplace-name> && git pull origin main` |
| `/plugin` shows no version | `plugin.json` missing `version` field | Add `"version": "X.Y.Z"` to `.claude-plugin/plugin.json` |
| Version mismatch | `plugin.json` and `marketplace.json` disagree | Ensure all three version locations match |
| Hooks don't run | Hook scripts in `hooks/` instead of `src/hooks/` | Plugin cache only includes `src/` — hooks must live there |
| Agents can't find hooks | Frontmatter references `hooks/` path | Update to `src/hooks/` in agent `command:` lines |

## Post-release verification (added v1.25.1 — non-negotiable)

After pushing the tag, verify the release actually loads on a real install. The scripted
form (same script CI runs, plus a version assertion the manual check lacked):

```bash
scripts/ci/install_smoke.sh \
  --source https://github.com/JackScammell/Parliament-Of-Chaos.git \
  --expected-version X.Y.Z
```

Then update your own live install. **The marketplace name depends on how it was added**
(a GitHub-URL add registers under the repo name `parliament-of-chaos`; a local-path add
registers under marketplace.json's `chaos`) — check yours first:

```bash
claude plugin marketplace list          # find YOUR registered marketplace name
claude plugin marketplace update <marketplace-name>
claude plugin update chaos@<marketplace-name>
claude plugin list   # must show "enabled" at the new version, not "failed to load"
```

Both hook-registration incidents (v1.9.0's ignored settings.json, v1.25.0's duplicate
hooks-field) would have been caught by this step. Config that has never been load-tested on a
real install is config that has never worked.
