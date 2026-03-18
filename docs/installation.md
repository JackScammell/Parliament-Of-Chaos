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
- 34 slash commands for orchestration, reviews, project planning, developer workflow, operations, and analytics
- 30 agents (specialists, reviewers, planners, and orchestrators)

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
requirements.txt          # Python dependencies for the deliberation system

.claude/
  agents/
    chaos/
      # Planning Agents (3)
      project-oracle.md          # Project planning via Q&A
      scope-weaver.md            # Scopes roadmap items into tasks
      task-executor.md           # Task tracking and documentation

      # Specialist Agents (16)
      api-keeper.md              # API design and versioning
      backend-goblin.md          # Backend performance and caching
      config-curator.md          # Environment config and feature flags
      data-warlock.md            # Database design and migrations
      dependency-detective.md    # Vulnerability and license compliance
      doc-bard.md                # Documentation and READMEs
      migration-monk.md          # Schema migrations and rollbacks
      observability-oracle.md    # Logging, metrics, and tracing
      package-wizard.md          # Dependency management
      pipeline-engineer.md       # CI/CD and deployment
      refactor-ranger.md         # Code smells and refactoring
      resilience-tamer.md        # Error handling and resilience
      security-knight.md         # Security analysis and hardening
      system-architect.md        # System design and architecture
      test-prophet.md            # Testing strategies and TDD
      ui-ux-guru.md              # User interface and accessibility

      # Grumpy Reviewers (9)
      grumpy-accessibility-auditor.md     # WCAG compliance
      grumpy-architecture-skeptic.md      # Architectural decisions
      grumpy-code-reviewer.md             # General code quality
      grumpy-documentation-pedant.md      # Documentation completeness
      grumpy-maintainability-curmudgeon.md # Maintainability
      grumpy-performance-troll.md         # Performance issues
      grumpy-security-nag.md              # Security vulnerabilities
      grumpy-standards-enforcer.md        # Standards compliance
      grumpy-testing-tyrant.md            # Test coverage and quality

      # Orchestrators (2)
      senior-council.md          # Coordinates multi-agent sessions
      deliberation-conductor.md  # Orchestrates structured debates

  commands/
    chaos/
      # Council Commands
      summon-council.md          # Full multi-agent orchestration
      summon-grumpy-reviewer.md  # Quick code review session
      summon-specialist.md       # Invoke a specific specialist
      parliament-review.md       # Full review with all 9 grumpy reviewers

      # Discovery Commands
      list-agents.md             # Display all agents by category
      list-commands.md           # Display all commands by category
      explain-agent.md           # Detailed agent explanation

      # Planning Commands
      plan-project.md            # Interactive project planning
      project-status.md          # Project dashboard
      roadmap-add-item.md        # Add items to roadmap
      roadmap-item-scope.md      # Scope items into tasks
      implement-task-list.md     # Execute tasks with council review

      # Operations Commands (v1.4.0)
      parliament-optimize.md     # Audit agent configurations
      parliament-webhook.md      # Configure webhook notifications
      parliament-loop.md         # Recurring command execution
      parliament-monitor.md      # Background monitoring agents

      # Developer Workflow Commands (v1.5.0)
      pre-commit-check.md        # Run all CI checks locally
      format-code.md             # Auto-detect and run formatter
      lint-fix.md                # Auto-detect and run linter with fix
      run-tests.md               # Auto-detect and run test suite
      security-scan.md           # Unified security scanning
      clean-imports.md           # Remove unused imports
      update-dependencies.md     # Interactive dependency updates
      dead-code-sweep.md         # Find dead code and orphaned files
      update-docs.md             # Update docs after code changes

      # Discovery Commands (v1.6.0)
      version.md                 # Display plugin version
      readme.md                  # Display README in session
      changelog.md               # Display version history

      # Analytics & Plugin Commands
      debate-analytics.md        # Generate analytics dashboard
      debate-topic.md            # Run structured deliberation
      plugin-install.md          # Install community plugins
      plugin-list.md             # List installed plugins
```

## Available Commands

### Council Commands

| Command | Description |
|---------|-------------|
| `/summon-council` | Full parliament orchestration with specialists and grumpy review |
| `/summon-grumpy-reviewer` | Quick code review from grumpy perspective |
| `/summon-specialist` | Directly invoke a specialist agent |
| `/parliament-review` | Full review using all 9 grumpy reviewers |
| `/debate-topic` | Run structured multi-agent deliberation with convergence detection |

### Discovery Commands

| Command | Description |
|---------|-------------|
| `/list-agents` | Display all agents grouped by category |
| `/list-commands` | Display all commands grouped by category |
| `/explain-agent` | Detailed explanation of what an agent does and when to use it |
| `/version` | Display current plugin version and metadata |
| `/readme` | Display the full README in the session |
| `/changelog` | Display the full version history |

### Project Planning Commands

| Command | Description |
|---------|-------------|
| `/plan-project` | Interactive project planning with Project Oracle |
| `/project-status` | View project progress dashboard |
| `/roadmap-add-item` | Add new items to the roadmap |
| `/roadmap-item-scope` | Break down items into specs and tasks |
| `/implement-task-list` | Execute tasks with full council oversight |

### Operations Commands

| Command | Description |
|---------|-------------|
| `/parliament-optimize` | Audit agent definitions and recommend effort/model settings |
| `/parliament-webhook` | Configure webhook notification endpoints (Teams, Slack, Discord) |
| `/parliament-loop` | Set up recurring Parliament commands via `/loop` integration |
| `/parliament-monitor` | Manage background monitoring agents for continuous oversight |

### Developer Workflow Commands

| Command | Description |
|---------|-------------|
| `/pre-commit-check` | Auto-detect and run all CI checks locally before committing |
| `/format-code` | Auto-detect and run the project's code formatter |
| `/lint-fix` | Auto-detect and run linter(s) with auto-fix |
| `/run-tests` | Auto-detect and run the test suite with intelligent options |
| `/security-scan` | Unified security check: dependencies, secrets, vulnerability patterns |
| `/clean-imports` | Remove unused imports and organise import ordering |
| `/update-dependencies` | Interactive dependency update with changelog review and test verification |
| `/dead-code-sweep` | Find unreachable code, unused exports, and orphaned files |
| `/update-docs` | Detect and update documentation affected by recent code changes |

### Analytics & Plugin Commands

| Command | Description |
|---------|-------------|
| `/debate-analytics` | Generate comprehensive analytics dashboard with metrics and insights |
| `/plugin-install` | Install community agent plugins from the marketplace |
| `/plugin-list` | List all installed plugins and marketplace summary |

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
