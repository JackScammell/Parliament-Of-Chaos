# Installation Guide

This guide covers installing Parliament of Chaos as a Claude Code plugin.

## Prerequisites

- Claude Code CLI installed and authenticated
- Access to the plugin marketplace

## Installation Steps

### 1. Add the Plugin Marketplace Source

First, register the Parliament of Chaos repository as a plugin source:

```
/plugin marketplace add owner/parliament-of-chaos
```

Replace `owner` with the GitHub username or organisation hosting the plugin.

### 2. Install the Plugin

Install the plugin into your Claude Code environment:

```
/plugin install parliament-of-chaos@parliament-of-chaos
```

This installs:
- 7 slash commands for orchestration, reviews, and project planning
- 21 specialist, reviewer, and planning agents

### 3. Verify Installation

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
      project-oracle.md          # Project planning and roadmap generation
      scope-weaver.md            # Scopes roadmap items into tasks
      task-executor.md           # Executes implementation tasks

      # Specialist Agents (11)
      backend-goblin.md          # Backend development expertise
      system-architect.md        # System design and architecture
      security-knight.md         # Security analysis and hardening
      data-warlock.md            # Database and data layer concerns
      api-keeper.md              # API design and integration
      test-prophet.md            # Testing strategies and coverage
      ui-ux-guru.md              # User interface and experience
      pipeline-engineer.md       # CI/CD and deployment pipelines
      doc-bard.md                # Documentation and technical writing
      package-wizard.md          # Dependency and package management
      resilience-tamer.md        # Error handling and system resilience

      # Grumpy Reviewers (6)
      grumpy-code-reviewer.md             # General code quality nitpicking
      grumpy-standards-enforcer.md        # Coding standards compliance
      grumpy-architecture-skeptic.md      # Architectural decision questioning
      grumpy-maintainability-curmudgeon.md # Long-term maintainability concerns
      grumpy-security-nag.md              # Security vulnerability hunting
      grumpy-performance-troll.md         # Performance issue detection

      # Orchestrator (1)
      senior-council.md          # Coordinates multi-agent sessions

  commands/
    parliament-of-chaos/
      # Core Commands
      summon-council.md          # Full multi-agent orchestration
      summon-grumpy-reviewer.md  # Quick code review session

      # Planning Commands
      plan-project.md            # Interactive project planning
      project-status.md          # Project dashboard and progress
      roadmap-add-item.md        # Add items to project roadmap
      roadmap-item-scope.md      # Scope roadmap items into tasks
      implement-task-list.md     # Execute implementation tasks
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/summon-council` | Convene the full parliament for multi-agent code review and discussion |
| `/summon-grumpy-reviewer` | Quick code review with the grumpy reviewer panel |
| `/plan-project` | Interactive project planning with the Project Oracle |
| `/project-status` | View project dashboard showing roadmap and task progress |
| `/roadmap-add-item` | Add new items to the project roadmap |
| `/roadmap-item-scope` | Break down roadmap items into actionable tasks |
| `/implement-task-list` | Execute tasks from your task list |

## Updating the Plugin

To update to the latest version:

```
/plugin update parliament-of-chaos
```

## Uninstalling

To remove the plugin:

```
/plugin uninstall parliament-of-chaos
```

This removes all agents and commands added by the plugin.

## Troubleshooting

### Commands not available

If `/summon-council` is not recognised:

1. Verify the plugin installed successfully with `/plugin list`
2. Try restarting your Claude Code session
3. Re-run the installation command

### Agent not found errors

If the Senior Council cannot find specialist agents:

1. Ensure the full plugin was installed (check for the `agents/parliament-of-chaos/` directory)
2. Verify file permissions allow Claude Code to read the agent definitions

### Planning commands not working

If `/plan-project` or other planning commands fail:

1. Ensure the planning agents (`project-oracle.md`, `scope-weaver.md`, `task-executor.md`) are installed
2. Check that the `.project-files/` directory is writable for storing project data

## Next Steps

- Read the [Usage Guide](usage.md) to learn how to use the commands effectively
- Try `/summon-grumpy-reviewer` on some existing code to see the review process in action
- Use `/plan-project` to begin planning a new project with the Project Oracle
