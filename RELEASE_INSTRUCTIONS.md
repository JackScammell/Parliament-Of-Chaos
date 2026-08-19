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
cd ~/.claude/plugins/marketplaces/chaos && git pull origin main && cd -
```

**Verify the cache has the new version:**
```bash
grep '"version"' ~/.claude/plugins/marketplaces/chaos/.claude-plugin/plugin.json
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
claude plugin install chaos@chaos
```

Then verify:
- `/plugin` shows correct version
- `/list-agents` works
- `/summon-grumpy-reviewer` activates

---

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| `/plugin` shows old version | Marketplace git clone is stale | `cd ~/.claude/plugins/marketplaces/chaos && git pull origin main` |
| `/plugin` shows no version | `plugin.json` missing `version` field | Add `"version": "X.Y.Z"` to `.claude-plugin/plugin.json` |
| Version mismatch | `plugin.json` and `marketplace.json` disagree | Ensure all three version locations match |
| Hooks don't run | Hook scripts in `hooks/` instead of `src/hooks/` | Plugin cache only includes `src/` — hooks must live there |
| Agents can't find hooks | Frontmatter references `hooks/` path | Update to `src/hooks/` in agent `command:` lines |
