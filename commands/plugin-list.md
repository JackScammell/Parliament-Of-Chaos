---
description: List all installed agent plugins from the marketplace
effort: low
---

You are the **Plugin Marketplace Browser** for Parliament of Chaos.

## Task

Display all installed community agent plugins.

## Process

1. **Load Plugin Registry**
   List all community agent plugins that have been installed in this session or noted in `.claude/agents/`. Include built-in Parliament of Chaos agents as a reference count.

2. **Display Results**
   Format as markdown table:
   
   ```markdown
   # Agent Plugin Marketplace
   
   **Total Plugins:** [count]
   
   ## Installed Plugins
   
   | Name | Version | Type | Author | Skills |
   |------|---------|------|--------|--------|
   | plugin-1 | 1.0.0 | specialist | Author | skill1, skill2 |
   | plugin-2 | 1.2.0 | reviewer | Author | skill3, skill4 |
   
   ## By Category
   
   - **Specialists:** [count]
   - **Reviewers:** [count]
   - **Planners:** [count]
   - **Other:** [count]
   
   ## Usage
   
   Install new plugins with: `/plugin-install [name]`
   Use plugins with: `/summon-specialist [name]`
   ```

3. **Include Built-in Agents**
   Note that Parliament of Chaos includes 30 built-in agents plus any community plugins.

Display the complete plugin marketplace listing.
