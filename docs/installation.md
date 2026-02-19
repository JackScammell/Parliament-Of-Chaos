# Installation Guide

This guide covers installing Parliament of Chaos as a Claude Code plugin.

## Prerequisites

- Claude Code CLI installed and authenticated
- Git available for cloning repositories

## Installation

### Quick Install

```
/install-github-plugin JackScammell/Parliament-Of-Chaos
```

This single command installs:
- 16 slash commands for orchestration, reviews, project planning, and analytics
- 30 agents (specialists, reviewers, planners, and orchestrators)

### Verify Installation

Confirm the plugin is active by running:

```
/summon-grumpy-reviewer
```

You should see the grumpy reviewer persona activate and prompt you for code to review.

## What Gets Installed

The plugin adds the following to your Claude Code configuration:

```
src/
  deliberation/           # Python deliberation system (analytics, plugins, core modules)
requirements.txt          # Python dependencies for the deliberation system

.claude/
  agents/
    parliament-of-chaos/
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
    parliament-of-chaos/
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

### Project Planning Commands

| Command | Description |
|---------|-------------|
| `/plan-project` | Interactive project planning with Project Oracle |
| `/project-status` | View project progress dashboard |
| `/roadmap-add-item` | Add new items to the roadmap |
| `/roadmap-item-scope` | Break down items into specs and tasks |
| `/implement-task-list` | Execute tasks with full council oversight |

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

To update to the latest version, re-run the install command:

```
/install-github-plugin JackScammell/Parliament-Of-Chaos
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
/install-github-plugin JackScammell/Parliament-Of-Chaos
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
- `.claude/agents/parliament-of-chaos/` - All agent files
- `.claude/commands/parliament-of-chaos/` - All command files

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

You must manually run `/install-github-plugin` to get updates.

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

**A:** No. Claude Code does not automatically update plugins. You must manually run `/install-github-plugin JackScammell/Parliament-Of-Chaos` to get updates.

**Q: How will I know when an update is available?**

**A:** Check the GitHub repository periodically:
- Watch for release notifications if you've starred the repo
- Check the repository's releases page
- Review the CHANGELOG or release notes

**Q: Do I need to uninstall before updating?**

**A:** No. Simply re-run `/install-github-plugin JackScammell/Parliament-Of-Chaos`. The command will replace old files with new ones automatically.

**Q: Will updating break my existing projects?**

**A:** No. Your project files (`.project-files/`), roadmaps, and custom configurations are not touched during updates. Only the agent and command files are replaced.

**Q: What if I want to stay on an older version?**

**A:** Simply don't run the update command. Your current version will continue to work. To install a specific version, you would need to manually download and install it from a specific GitHub tag/release.

## Uninstalling

To remove the plugin, delete the installed directories:

```
rm -rf .claude/agents/parliament-of-chaos
rm -rf .claude/commands/parliament-of-chaos
```

## Troubleshooting

### Commands not available

If `/summon-council` is not recognised:

1. Verify the directories exist in `.claude/`
2. Try restarting your Claude Code session
3. Re-run the installation command

### Agent not found errors

If the Senior Council cannot find specialist agents:

1. Ensure all agent files are present in `.claude/agents/parliament-of-chaos/`
2. Check that files have `.md` extension and correct YAML frontmatter

### Planning commands not working

If `/plan-project` or other planning commands fail:

1. Ensure planning agents are installed (`project-oracle.md`, `scope-weaver.md`, `task-executor.md`)
2. Check that `.project-files/` directory is writable

## Next Steps

- Read the [Usage Guide](usage.md) to learn how to use the commands effectively
- Try `/summon-grumpy-reviewer` on some existing code
- Use `/plan-project` to begin planning a new project
