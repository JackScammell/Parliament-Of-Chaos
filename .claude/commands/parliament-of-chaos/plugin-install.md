---
name: plugin-install
description: Install a community agent plugin from the marketplace
arguments:
  - name: plugin-name
    description: Name of the plugin to install
    required: true
---

You are the **Plugin Manager** for Parliament of Chaos.

## Task

Install a community agent plugin and make it available for use in debates.

## Process

1. **Validate Plugin Name**
   - Check if plugin name is valid
   - Verify plugin doesn't already exist

2. **Install Plugin**
   Use the PluginManager from `src/deliberation/plugins/plugin_manager.py`:
   
   ```python
   from src/deliberation import PluginManager
   
   manager = PluginManager()
   
   # Install plugin
   success = manager.install_plugin(
       name="[plugin-name]",
       version="1.0.0",
       author="Community",
       description="[Description]",
       agent_type="specialist",
       skills=["skill1", "skill2"]
   )
   ```

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

Complete the plugin installation for **[plugin-name]**.
