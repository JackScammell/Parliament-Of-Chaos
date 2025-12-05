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
- 12 slash commands for orchestration, reviews, and project planning
- 29 agents (specialists, reviewers, planners, and orchestrator)

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
| Commands | `~/.claude/plugins/marketplaces/parliament-of-chaos/.claude/commands/parliament-of-chaos/` |
| Agents | `~/.claude/plugins/marketplaces/parliament-of-chaos/.claude/agents/parliament-of-chaos/` |
| Plugin metadata | `~/.claude/plugins/marketplaces/parliament-of-chaos/.claude-plugin/marketplace.json` |

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

      # Orchestrator (1)
      senior-council.md          # Coordinates multi-agent sessions

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

      # Discovery Commands
      list-agents.md             # Display all agents by category
      list-commands.md           # Display all commands by category
      explain-agent.md           # Detailed agent explanation
```

## Available Commands

### Council Commands

| Command | Description |
|---------|-------------|
| `/summon-council` | Full parliament orchestration with specialists and grumpy review |
| `/summon-grumpy-reviewer` | Quick code review from grumpy perspective |
| `/summon-specialist` | Directly invoke a specialist agent |
| `/parliament-review` | Full review using all 9 grumpy reviewers |
| `/list-agents` | Display all agents grouped by category |
| `/list-commands` | Display all commands grouped by category |
| `/explain-agent` | Detailed explanation of what an agent does |
| `/plan-project` | Interactive project planning with Project Oracle |
| `/project-status` | View project progress dashboard |
| `/roadmap-add-item` | Add new items to the roadmap |
| `/roadmap-item-scope` | Break down items into specs and tasks |
| `/implement-task-list` | Execute tasks with full council oversight |

### Discovery Commands

| Command | Description |
|---------|-------------|
| `/list-agents` | Display all agents grouped by category |
| `/list-commands` | Display all commands grouped by category |
| `/explain-agent` | Detailed explanation of what an agent does and when to use it |

## Updating

To update to the latest version, re-run the install command:

```
/install-github-plugin JackScammell/Parliament-Of-Chaos
```

## Uninstalling

To remove the plugin via Claude Code:

```
/uninstall-plugin parliament-of-chaos
```

Or manually delete the plugin files:

```bash
# Remove plugin files
rm -rf ~/.claude/plugins/marketplaces/parliament-of-chaos

# Edit installed_plugins.json to remove the entry (optional - Claude Code handles this)
```

## Troubleshooting

### Commands not available

If `/summon-council` is not recognised:

1. Verify the plugin is registered: `cat ~/.claude/plugins/installed_plugins.json`
2. Check the plugin files exist: `ls ~/.claude/plugins/marketplaces/parliament-of-chaos/`
3. Try restarting your Claude Code session
4. Re-run the installation command

### Agent not found errors

If the Senior Council cannot find specialist agents:

1. Ensure all agent files are present in `~/.claude/plugins/marketplaces/parliament-of-chaos/.claude/agents/parliament-of-chaos/`
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
