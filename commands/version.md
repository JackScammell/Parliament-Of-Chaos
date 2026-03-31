---
description: Display the current Parliament of Chaos version and plugin metadata
effort: low
---

# Version

Display the current Parliament of Chaos version, plugin metadata, and a summary of what is installed.

## Process

1. Read `.claude-plugin/plugin.json` and extract version, name, and description
2. Count agents in `agents/` directory
3. Count commands in `commands/` directory
4. Display summary

## Output

```
Parliament of Chaos v{version}

Plugin: {name}
Agents: {count} (orchestrators, specialists, planners, reviewers)
Commands: {count} slash commands

Repository: https://github.com/JackScammell/Parliament-Of-Chaos
License: MIT

Run /changelog for version history.
Run /readme for full documentation.
```
