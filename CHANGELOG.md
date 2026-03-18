# Changelog

All notable changes to Parliament of Chaos will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-03-18

### Added

#### New Commands (30 total, up from 21)

##### Developer Workflow Commands (9 new)
- `/pre-commit-check`: Auto-detect CI pipeline, linters, formatters, type checkers, and test suites — run them all locally before committing. Includes secret scanning. Supports `--fix` for auto-remediation and `--skip` to bypass specific steps
- `/format-code`: Detect the project's formatter (Prettier, Black, gofmt, rustfmt, etc.) and run on changed files. Supports `--all`, `--check`, and explicit file targets. Offers setup if no formatter configured
- `/lint-fix`: Detect linter(s) (ESLint, Ruff, RuboCop, golangci-lint, etc.) and run with auto-fix on changed files. Handles multiple linters per project. Parses remaining errors with explanations
- `/run-tests`: Detect test framework and run suite with `--changed` (only tests affected by git changes via import graph analysis), `--coverage` (highlight untested critical paths), and `--explain` (diagnose failures and suggest fixes)
- `/security-scan`: Unified security check — dependency vulnerability audit, secret/credential detection, and OWASP Top 10 pattern scanning. Supports `--secrets`, `--deps`, `--patterns` focused modes
- `/clean-imports`: Remove unused imports, sort/organise imports per project conventions, convert to type imports (TypeScript). Works across JS/TS, Python, Go, Java, Rust
- `/update-dependencies`: Interactive dependency update — show outdated packages, review changelogs for breaking changes, update incrementally with test runs between each, auto-rollback on failure. Supports `--patch`, `--minor`, `--major`, `--security` filters
- `/dead-code-sweep`: Find unreachable code, unused exports, orphaned files, and dead CSS. Report-only by default with confidence levels. `--apply` shows diff preview and asks for confirmation before removing
- `/update-docs`: Detect and update project documentation affected by recent code changes. Analyses git diff, cross-references with docs, generates updates with provenance tracking. Delegates to doc-bard for writing and grumpy-documentation-pedant for validation. Preview-only by default with `--apply` for confirmed writes

### Changed
- **Command count**: 30 commands (up from 21) — added 9 developer workflow commands
- **Command categories**: Added new "Developer Workflow" category to `/list-commands`

## [1.4.0] - 2026-03-18

### Added

#### New Commands (21 total, up from 17)
- `/parliament-optimize`: Advisory audit of all agent definitions — recommends effort/model settings based on role
- `/parliament-webhook`: Configure HTTP webhook notification endpoints for Slack, Discord, Teams, or custom URLs
- `/parliament-loop`: Set up recurring execution of Parliament commands via Claude Code's `/loop` integration
- `/parliament-monitor`: Manage background monitoring agents for continuous code oversight during sessions

#### Agent Frontmatter Enhancements
- **Effort tiers**: All 30 agents now have `effort` frontmatter — orchestrators `high`, specialists `medium`, reviewers `low`. Estimated 40-60% token cost reduction on review tasks
- **maxTurns limits**: All agents now have `maxTurns` — orchestrators 30, planning 20, specialists 15, reviewers 5
- **Memory scopes**: All 16 specialists now have `memory: project` for persistent project knowledge across sessions
- **Worktree isolation**: All 15 implementation specialists now have `isolation: worktree` for parallel work in isolated git branches (security-knight, doc-bard, package-wizard, dependency-detective, observability-oracle added)

#### New Hooks
- **StopFailure**: Fires on API errors (rate limits, auth failures) during Parliament sessions — logs failure and optionally notifies via webhook
- **PostCompact**: Fires after context compaction — checkpoints state for monitoring context usage patterns
- **InstructionsLoaded**: Fires when CLAUDE.md or rules files are loaded/reloaded — detects stale rules in long sessions

#### Agent Standards
- `.claude/rules/agent-standards.md`: Comprehensive frontmatter standards document covering effort tiers, maxTurns guidelines, memory scopes, tool restrictions, isolation patterns, and templates for each agent role

#### Agent Teams Abstraction (Phase 3 Scaffold)
- `CommunicationLayer` abstraction in `src/deliberation/core/communication.py` — unified interface for inter-agent communication
- `TaskCommunication`: Stable implementation using current Task() subagent model
- `AgentTeamsCommunication`: Experimental placeholder for Agent Teams (v2.1.32+), behind `PARLIAMENT_USE_AGENT_TEAMS=1` feature flag
- Go/no-go gate: Agent Teams integration activates only when the feature exits Claude Code's research preview

### Changed
- **notify_teams.sh**: Added support for StopFailure, PostCompact, and InstructionsLoaded hook events
- **settings.json**: Added StopFailure, PostCompact, and InstructionsLoaded hook configurations with dedicated handler scripts
- **Agent count**: 30 agents (unchanged), now with standardised frontmatter across all roles
- **Command count**: 21 commands (up from 17)

## [1.3.0] - 2026-03-18

### Added
- Native Claude Code plugin installation via `claude plugin marketplace add` and `claude plugin install`

### Changed
- **Hook scripts relocated** from `hooks/` to `src/hooks/` so they survive plugin cache (fixes hooks not working for installed users)
- **Install commands updated** across all documentation to use native `claude plugin` CLI commands instead of non-existent `/install-github-plugin`
- **Update commands updated** to use `claude plugin update parliament-of-chaos@parliament-of-chaos`
- **notify_teams.sh**: Fixed JSON injection vulnerability — payload now constructed with `jq` instead of string interpolation
- **system-architect**: Added `Bash` to `disallowedTools` to enforce read-only access consistently with other analysis agents

### Fixed
- Hooks and settings.json were stripped from plugin cache because they lived in `hooks/` (not cached); moved to `src/hooks/` which is cached
- JSON injection risk in Teams webhook notifications via crafted project directory names

## [1.2.0] - 2026-01-15

### Changed
- Version bump for marketplace registration and Phase 3 advanced orchestration features
- No user-facing changes beyond what was included in the 1.1.0 release

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

[1.5.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/V1.0.0...v1.1.0
[1.0.0]: https://github.com/JackScammell/Parliament-Of-Chaos/releases/tag/V1.0.0
