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
- 2 slash commands (`/summon-council`, `/summon-grumpy-reviewer`)
- 17 specialist and reviewer agents

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
      backend-goblin.md
      grumpy-code-reviewer.md
      grumpy-standards-enforcer.md
      grumpy-architecture-skeptic.md
      grumpy-maintainability-curmudgeon.md
      grumpy-security-nag.md
      grumpy-performance-troll.md
      system-architect.md
      security-knight.md
      data-warlock.md
      test-prophet.md
      pipeline-engineer.md
      api-keeper.md
      doc-bard.md
      package-wizard.md
      resilience-tamer.md
      ui-ux-guru.md
      senior-council.md
  commands/
    parliament-of-chaos/
      summon-council.md
      summon-grumpy-reviewer.md
```

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

## Next Steps

- Read the [Usage Guide](usage.md) to learn how to use the commands effectively
- Try `/summon-grumpy-reviewer` on some existing code to see the review process in action
