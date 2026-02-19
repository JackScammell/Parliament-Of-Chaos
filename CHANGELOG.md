# Changelog

All notable changes to Parliament of Chaos will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-05

### Added

#### New Agents (29 total, up from 21)
- **migration-monk**: Schema migrations and rollback strategies
- **dependency-detective**: Vulnerability chains and license compliance
- **refactor-ranger**: Code smells and refactoring patterns
- **config-curator**: Environment config, secrets, and feature flags
- **observability-oracle**: Logging, metrics, tracing, and alerting
- **grumpy-accessibility-auditor**: WCAG compliance and inclusive design
- **grumpy-documentation-pedant**: Documentation completeness
- **grumpy-testing-tyrant**: Test coverage and quality

#### New Commands (12 total)
- `/list-agents`: Display all agents grouped by category
- `/list-commands`: Display all commands grouped by category
- `/explain-agent <agent>`: Detailed explanation of what an agent does and when to use it
- `/summon-specialist <agent>`: Directly invoke a specialist agent on your current task
- `/parliament-review`: Full review using all 9 grumpy reviewers for maximum scrutiny

#### Features
- **Standards Compliance**: All 16 specialist agents now include a "Standards Compliance" section instructing them to consult official documentation, verify recommendations, and cite sources for framework-specific patterns
- **Conflict Resolution Protocol**: Introduced priority-based conflict resolution (security > correctness > maintainability > performance) for when reviewers disagree
- **Marketplace Configuration**: Added `.claude-plugin/marketplace.json` to register the plugin for Claude Code marketplace
- **Hooks Configuration Guide**: New comprehensive guide (`docs/hooks.md`) explaining how to configure and use hooks for notifications and automation
- **Agent Memory Context**: Added roadmap specification for persistent agent memory across sessions
- **Configurable Grumpiness**: Added roadmap specification for adjustable reviewer strictness levels
- **Review Report Export**: Added roadmap specification for exporting review reports to various formats

### Changed
- **Agent Definitions**: Revised all agent role definitions and output structures for clarity, consistency, and conciseness
- **Senior Council**: Updated task analysis to reference project conventions and standards instead of specific files
- **Command Optimization**: Optimized `/summon-council` and `/summon-grumpy-reviewer` commands for brevity and token efficiency
- **Documentation**: Expanded and improved documentation across all guides (installation, usage, hooks, safe progress assurance)
- **Roadmap Structure**: Added scoped and completed status tracking for roadmap items
- **Agent Count**: Updated from 21 to 29 agents throughout documentation

### Improved
- Agent selection logic in senior-council with expanded specialist roles
- Verification steps and cross-referencing across all agent definitions
- Response style consistency across specialist agents
- Installation and usage guides to reflect the expanded multi-agent, multi-command workflow

## [1.0.0] - 2025-12-03

### Added
- Initial release of Parliament of Chaos
- 21 AI agents (11 specialists, 6 grumpy reviewers, 3 planning agents, 1 orchestrator)
- 7 slash commands for project planning and code review
- Complete documentation suite
- MIT License
- Example project files demonstrating the planning workflow

[1.1.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/V1.0.0...v1.1.0
[1.0.0]: https://github.com/JackScammell/Parliament-Of-Chaos/releases/tag/V1.0.0
