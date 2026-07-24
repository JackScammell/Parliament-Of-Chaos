# Installation Guide

This guide covers installing Parliament of Chaos as a Claude Code plugin.

## Prerequisites

- Claude Code CLI installed and authenticated
- Git available for cloning repositories

## Installation

### Quick Install

```
claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
claude plugin install chaos@chaos
```

These commands install:
- 66 slash commands across 15 categories (orchestration, deliberation, planning, developer workflow, hygiene, quality, release, observability, decisions, lifecycle, operations, analysis, discovery, plugins)
- 33 agents — 2 orchestrators, 3 planning agents, 16 specialists, 12 grumpy reviewers
- `commands/manifest.yaml` — declarative registry that `/parliament-doctor` reconciles against the filesystem and skill registry

### Verify Installation

Confirm the plugin is active by running:

```
/summon-grumpy-reviewer
```

You should see the grumpy reviewer persona activate and prompt you for code to review.

## Where Plugin Files Live

When installed via the marketplace, plugin files are stored in a **centralised user-level cache**, not in your project directory:

```
~/.claude/plugins/marketplaces/<plugin-name>/
```

For Parliament of Chaos, this means:

| Content | Location |
|---------|----------|
| Commands | `~/.claude/plugins/marketplaces/chaos/commands/` |
| Agents | `~/.claude/plugins/marketplaces/chaos/agents/` |
| Plugin metadata | `~/.claude/plugins/marketplaces/chaos/.claude-plugin/marketplace.json` |

### Why This Location?

The centralised approach means:
- **One copy serves all projects** - no duplication across repositories
- **Automatic updates** - updating the plugin updates it everywhere
- **Clean project directories** - your `.claude/` folder isn't cluttered with plugin files
- **Git-friendly** - plugin files don't pollute your project's version control

### Plugin Registry

Claude Code tracks installed plugins in:

```
~/.claude/plugins/installed_plugins.json
```

This file records:
- Plugin name and version
- Installation path
- Git commit SHA (for update tracking)
- Installation timestamp

## Logical Structure

While the files live in the centralised cache, Claude Code presents them as if they were installed at:

```
src/
  deliberation/           # Python deliberation system (analytics, plugins, core modules)
  hooks/                  # Hook scripts (_common.sh, log_event.sh, notify_teams.sh)
requirements.txt          # Python dependencies for the deliberation system

agents/                   # 33 agent definitions
  # Orchestrators (2)
  senior-council.md
  deliberation-conductor.md

  # Planning Agents (3)
  project-oracle.md
  scope-weaver.md
  task-executor.md

  # Specialists (16)
  api-keeper.md              backend-goblin.md
  config-curator.md          data-warlock.md
  dependency-detective.md    doc-bard.md
  migration-monk.md          observability-oracle.md
  package-wizard.md          pipeline-engineer.md
  refactor-ranger.md         resilience-tamer.md
  security-knight.md         system-architect.md
  test-prophet.md            ui-ux-guru.md

  # Grumpy Reviewers (12)
  grumpy-accessibility-auditor.md       grumpy-architecture-skeptic.md
  grumpy-budget-hawk.md                 grumpy-code-reviewer.md
  grumpy-documentation-pedant.md        grumpy-i18n-nitpicker.md
  grumpy-maintainability-curmudgeon.md  grumpy-performance-troll.md
  grumpy-privacy-paranoid.md            grumpy-security-nag.md
  grumpy-standards-enforcer.md          grumpy-testing-tyrant.md

commands/                 # 66 commands + manifest
  manifest.yaml           # Source-of-truth registry (name, status, owner, effort, category)
  <66 command .md files across 15 categories>
```

The `commands/manifest.yaml` file tracks every command's status (`active`, `deprecated`, `experimental`, `orphaned`), owner agent, effort tier, and category. Run `/parliament-doctor` after any change to reconcile the manifest against the filesystem and the registered skill surface.

## Available Commands

Parliament of Chaos ships 66 slash commands organised into 15 categories. The authoritative list lives in [`commands/manifest.yaml`](../commands/manifest.yaml), which tracks name, status, owner agent, effort tier, and category for every command.

For the complete table grouped by category, see the [README](../README.md#commands). For a live view inside Claude Code, run:

```
/list-commands            # Grouped by category, reads commands/manifest.yaml
/list-agents              # All 33 agents grouped by category
/version                  # Plugin version and metadata
```

### Command Categories (15)

| Category | Representative Commands |
|----------|-------------------------|
| Agent Invocation | `/summon-council`, `/summon-specialist`, `/summon-grumpy-reviewer`, `/parliament-review` |
| Deliberation | `/debate-topic`, `/debate-analytics`, `/debate-replay` |
| Project Planning | `/plan-project`, `/project-status`, `/roadmap-add-item`, `/roadmap-item-scope`, `/implement-task-list` |
| Developer Workflow | `/pre-commit-check`, `/format-code`, `/lint-fix`, `/run-tests`, `/security-scan`, `/clean-imports`, `/update-dependencies`, `/dead-code-sweep`, `/update-docs`, `/analyse-queries`, `/git-workflow`, `/scaffold` |
| Quality | `/coverage-audit`, `/generate-tests`, `/mutation-test`, `/test-health`, `/track-debt`, `/i18n-audit` |
| Release | `/cut-release`, `/release-notes-draft`, `/plugin-upgrade` |
| Decisions | `/adr-new`, `/adr-supersede`, `/decision-review` |
| Observability | `/telemetry-query`, `/parliament-metrics`, `/cost-report` |
| Lifecycle | `/session-snapshot`, `/docs-audit`, `/settings-audit`, `/env-doctor`, `/fast-track`, `/ci-watch` |
| Operations | `/parliament-optimize`, `/parliament-webhook`, `/parliament-loop`, `/parliament-monitor`, `/changelog-review`, `/incident`, `/infra-review`, `/retro`, `/agent-usage-stats` |
| Hygiene | `/parliament-doctor` |
| Codebase Analysis | `/onboard-codebase` |
| Discovery | `/list-agents`, `/list-commands`, `/explain-agent`, `/version`, `/readme`, `/changelog` |
| Plugins | `/plugin-install`, `/plugin-list` |

### Verifying Your Installation

After installing, run `/parliament-doctor` to confirm there is no drift between the manifest, the command files, and the registered skill surface. `/env-doctor` validates that hook scripts and the plugin data directory are wired correctly.

## Updating the Plugin

### How Updates Work

**Claude Code does NOT automatically update plugins.** You must manually update when new versions are released.

### When to Update

Update Parliament of Chaos when:
- A new version is released on GitHub
- New agents or commands are announced
- Bug fixes or improvements are available
- You see an update notification in the repository

### How to Update

To update to the latest version:

```
claude plugin update chaos@chaos
```

**What happens during update:**
1. Claude Code fetches the latest version from GitHub
2. Existing plugin files are replaced with new versions
3. New agents/commands are added automatically
4. Your project files (`.project-files/`) are not affected
5. Custom hooks and settings are preserved

### Update Process

**Step 1: Check for Updates**

Visit the repository to see if a new version is available:
- https://github.com/JackScammell/Parliament-Of-Chaos

Look for:
- New release tags
- Updated `version` in `.claude-plugin/marketplace.json`
- CHANGELOG or release notes

**Step 2: Run Update Command**

```
claude plugin update chaos@chaos
```

**Step 3: Verify Update**

After updating, verify the new version is active:

```
/list-agents
```

Check that any newly announced agents appear in the list.

### Update Frequency

**Recommended:** Check for updates monthly or when:
- Starting a new major project
- You need a feature mentioned in release notes
- A bug you've encountered is fixed

### What Gets Updated

During an update, these are replaced with new versions:
- `agents/` - All agent files
- `commands/` - All command files

**Not affected by updates:**
- `.project-files/` - Your project plans and roadmaps
- `.claude/settings.json` - Your hook configurations
- `.claude/settings.local.json` - Your personal settings
- `.claude/hooks/` - Your custom hook scripts

### Automatic Updates

**Claude Code does NOT have automatic plugin updates.**

This is by design to ensure:
- Stability of your development environment
- Control over when changes are introduced
- Compatibility with your existing workflows

You must manually run `claude plugin update chaos@chaos` to get updates.

### Checking Your Current Version

To see which version you have installed:

1. Check the version in your local installation:
   ```bash
   cat .claude-plugin/marketplace.json | grep version
   ```

2. Compare with the latest version on GitHub:
   - Visit: https://github.com/JackScammell/Parliament-Of-Chaos
   - Check `.claude-plugin/marketplace.json` in the repository

### FAQ: Updates

**Q: Will the plugin update automatically when I start Claude Code?**

**A:** No. Claude Code does not automatically update plugins. You must manually update:

```
claude plugin update chaos@chaos
```

**Q: How will I know when an update is available?**

**A:** Check the GitHub repository periodically:
- Watch for release notifications if you've starred the repo
- Check the repository's releases page
- Review the CHANGELOG or release notes

**Q: Do I need to uninstall before updating?**

**A:** No. Simply run the update command:

```
claude plugin update chaos@chaos
```

The command will replace old files with new ones automatically.

**Q: Will updating break my existing projects?**

**A:** No. Your project files (`.project-files/`), roadmaps, and custom configurations are not touched during updates. Only the agent and command files are replaced.

**Q: What if I want to stay on an older version?**

**A:** Simply don't run the update command. Your current version will continue to work. To install a specific version, you would need to manually download and install it from a specific GitHub tag/release.

## Uninstalling

To remove the plugin via Claude Code:

```
/uninstall-plugin chaos
```

Or manually delete the plugin files:

```bash
# Remove plugin files
rm -rf ~/.claude/plugins/marketplaces/chaos

# Edit installed_plugins.json to remove the entry (optional - Claude Code handles this)
```

## Troubleshooting

### Commands not available

If `/summon-council` is not recognised:

1. Verify the plugin is registered: `cat ~/.claude/plugins/installed_plugins.json`
2. Check the plugin files exist: `ls ~/.claude/plugins/marketplaces/chaos/`
3. Try restarting your Claude Code session
4. Re-run the installation command

### Agent not found errors

If the Senior Council cannot find specialist agents:

1. Ensure all agent files are present in `~/.claude/plugins/marketplaces/chaos/agents/`
2. Check that files have `.md` extension and correct YAML frontmatter

### Planning commands not working

If `/plan-project` or other planning commands fail:

1. Ensure planning agents are installed (`project-oracle.md`, `scope-weaver.md`, `task-executor.md`)
2. Check that `.project-files/` directory is writable in your current project

### Files not in project directory

This is expected behaviour. Marketplace plugins are stored in a centralised location (`~/.claude/plugins/marketplaces/`) rather than copied into each project. See [Where Plugin Files Live](#where-plugin-files-live) above.

## Next Steps

- Read the [Usage Guide](usage.md) to learn how to use the commands effectively
- Try `/summon-grumpy-reviewer` on some existing code
- Use `/plan-project` to begin planning a new project
