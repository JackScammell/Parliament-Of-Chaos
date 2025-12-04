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
- 7 slash commands for orchestration, reviews, and project planning
- 21 specialist, reviewer, and planning agents

### Verify Installation

Confirm the plugin is active by running:

```
/summon-grumpy-reviewer
```

You should see the grumpy reviewer persona activate and prompt you for code to review.

## What Gets Installed

The plugin adds the following to your Claude Code configuration:

```
.claude/
  agents/
    parliament-of-chaos/
      # Planning Agents (3)
      project-oracle.md          # Project planning via Q&A
      scope-weaver.md            # Scopes roadmap items into tasks
      task-executor.md           # Task tracking and documentation

      # Specialist Agents (11)
      backend-goblin.md          # Backend performance
      system-architect.md        # System design and architecture
      security-knight.md         # Security analysis
      data-warlock.md            # Database and data layer
      api-keeper.md              # API design
      test-prophet.md            # Testing strategies
      ui-ux-guru.md              # User interface and experience
      pipeline-engineer.md       # CI/CD and deployment
      doc-bard.md                # Documentation
      package-wizard.md          # Dependency management
      resilience-tamer.md        # Error handling and resilience

      # Grumpy Reviewers (6)
      grumpy-code-reviewer.md             # General code quality
      grumpy-standards-enforcer.md        # Standards compliance
      grumpy-architecture-skeptic.md      # Architectural decisions
      grumpy-maintainability-curmudgeon.md # Maintainability
      grumpy-security-nag.md              # Security vulnerabilities
      grumpy-performance-troll.md         # Performance issues

      # Orchestrator (1)
      senior-council.md          # Coordinates multi-agent sessions

  commands/
    parliament-of-chaos/
      # Core Commands
      summon-council.md          # Full multi-agent orchestration
      summon-grumpy-reviewer.md  # Quick code review session

      # Planning Commands
      plan-project.md            # Interactive project planning
      project-status.md          # Project dashboard
      roadmap-add-item.md        # Add items to roadmap
      roadmap-item-scope.md      # Scope items into tasks
      implement-task-list.md     # Execute tasks with council review
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/summon-council` | Full parliament orchestration with specialists and grumpy review |
| `/summon-grumpy-reviewer` | Quick code review from grumpy perspective |
| `/plan-project` | Interactive project planning with Project Oracle |
| `/project-status` | View project progress dashboard |
| `/roadmap-add-item` | Add new items to the roadmap |
| `/roadmap-item-scope` | Break down items into specs and tasks |
| `/implement-task-list` | Execute tasks with full council oversight |

## Updating

To update to the latest version, re-run the install command:

```
/install-github-plugin JackScammell/Parliament-Of-Chaos
```

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
