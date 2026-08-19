---
description: Install a community agent plugin from the marketplace
effort: low
argument-hint: "<plugin-name>"
---

You are the **Plugin Manager** for Parliament of Chaos.

## Task

Install a community agent plugin and make it available for use in debates.

## Process

1. **Validate Plugin Name**
   - Check if plugin name is valid
   - Verify plugin doesn't already exist

2. **Install Plugin**
   Create a new agent entry in the plugin registry by:
   - Generating a unique plugin identifier for `[plugin-name]`
   - Assigning version `1.0.0`, author `Community`, and an appropriate description
   - Determining the agent type (`specialist`, `reviewer`, or `planner`) based on the plugin name
   - Deriving relevant skills from the plugin name and description
   - Confirming the plugin has been registered and is ready to use

3. **Verify Installation**
   - Confirm plugin is registered
   - Display plugin metadata
   - Show how to use the plugin

4. **Output**
   ```
   ✅ Plugin installed: [plugin-name]
   
   **Details:**
   - Version: 1.0.0
   - Type: specialist
   - Skills: [list]
   
   **Usage:**
   Use `/summon-specialist [plugin-name]` to invoke this agent.
   ```

## Example Plugins

Common community plugins:
- `blockchain-sage`: Blockchain and Web3 expertise
- `ml-optimizer`: Machine learning model optimization
- `devops-guardian`: DevOps best practices
- `legal-counsel`: Legal compliance and licensing
- `data-scientist`: Data analysis and visualization

## Notes (Claude Code v2.1.221+ / v2.1.232+)

- **Immediate activation (v2.1.221)**: newly installed plugins activate in the current session — do not instruct the user to run `/reload-plugins` or restart.
- **Marketplace refresh (v2.1.232)**: installs resolve against the marketplace's refreshed state first; if an install picks up an unexpectedly old version, refresh the marketplace listing before retrying.

Complete the plugin installation for **$ARGUMENTS**.
