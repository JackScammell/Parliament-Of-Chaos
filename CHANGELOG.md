# Changelog

All notable changes to Parliament of Chaos will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-04-17

### Added

#### Claude Code Feature Adoption (v2.1.89–v2.1.112)

##### New Hooks
- **PermissionDenied**: Fires when auto mode denies a Parliament agent's tool call — logs denied tool name and reason for diagnosing silent agent failures in automated workflows. Wired to `notify_teams.sh` for optional team notification.
- **TaskCreated**: Fires when a new task is created — completes the task lifecycle logging alongside the existing `TaskCompleted` hook.

##### Hook Consolidation
- **log_event.sh**: Unified event logging dispatcher replaces four individual scripts (`log_agent_activity.sh`, `handle_post_compact.sh`, `handle_instructions_loaded.sh`, `handle_stop_failure.sh`). Uses a `case` statement to extract event-specific fields — adding a new logged event is now a one-line case addition.
- **Log rotation**: `_common.sh` now rotates `activity.jsonl` to `activity.jsonl.old` when it exceeds 10MB, preventing unbounded log growth.

##### Plugin Manifest
- **`keep-coding-instructions: true`** in `plugin.json` — ensures Parliament's `.claude/rules/*.md` (agent-standards, governance, output-standards) stay resident across context compactions, pairing with the existing `InstructionsLoaded` hook. Prevents reviewers from losing the governance priority hierarchy mid-deliberation.
- **`dependencies: []`** field in `plugin.json` — declares zero external-plugin dependencies. v2.1.110 makes this install-enforced; an explicit empty array signals intent and future-proofs additions.

##### Standards Documentation
- **`xhigh` effort tier** documented in `agent-standards.md` — Opus 4.7's new tier (Claude Code v2.1.111) between `high` and `max` is listed as *Reserved* in the effort-tiers table. No agents adopt it yet; reserved for future deliberation-conductor deep-mode runs pending benchmark evidence.
- **Subagent MCP inheritance** documented in `agent-standards.md` — v2.1.101 made MCP tools flow automatically from parent sessions to spawned subagents. Note added to the Tool Restrictions section so contributors don't re-declare MCP servers per agent.
- **Default `effort: high`** informational note in `agent-standards.md` — Claude Code v2.1.94 raised the global default from `medium` to `high`. Parliament sets `effort` explicitly per agent so behaviour is unchanged, but the note flags the upstream default for new contributors.

### Changed
- **_common.sh**: Added `HOOK_LOG_DIR`, `HOOK_LOG_FILE`, automatic `mkdir -p`, and 10MB log rotation guard.
- **notify_teams.sh**: Added `PermissionDenied` event case, hardened `.env` sourcing with ownership/permission checks, replaced wildcard `*)` fallback with safe `exit 0` to reject unknown events.
- **settings.json**: All logging hooks now point to unified `log_event.sh`; added `PermissionDenied` and `TaskCreated` hook configurations.
- **Hook count**: 9 hook event handlers (up from 7), served by 3 scripts (down from 5).
- **plugin.json / marketplace.json**: Version bumped to 1.9.0 across both files.

### Removed
- `log_agent_activity.sh`, `handle_post_compact.sh`, `handle_instructions_loaded.sh`, `handle_stop_failure.sh` — replaced by `log_event.sh`.

### Deferred (Priority 2 — tracked for v1.10.0)
- `PreCompact` hook `block` decision (v2.1.105) — needs scope-weaver design pass with hard attempt counter to avoid infinite-block footgun.
- Plugin `monitors` manifest key (v2.1.105) — prototype candidate for always-on log tailing / roadmap drift alerts; waiting one release for community examples.
- Skill-tool slash-command references in specialist prompts (v2.1.108) — consistency audit across test-prophet, backend-goblin, pipeline-engineer.

## [1.8.0] - 2026-03-31

### Added

#### New Agents (33 total, up from 30)

##### Grumpy Reviewers (12 total, up from 9)
- **grumpy-privacy-paranoid**: PII exposure, GDPR/CCPA compliance, consent handling, data retention — fills the gap between security (auth/vulns) and privacy (data governance)
- **grumpy-i18n-nitpicker**: Hardcoded strings, missing translations, broken pluralisation, locale-aware formatting — for any project with multi-language support
- **grumpy-budget-hawk**: Cloud cost impact of PRs, over-provisioned resources, unbounded queries, missing auto-scaling bounds — performance-troll covers speed, this covers spend

#### New Commands (46 total, up from 34)

##### Phase 1 — High frequency, high impact (4 new)
- `/cut-release`: Automate version bumping, changelog generation, git tagging, and release notes across all version-bearing files
- `/scaffold`: Generate convention-compliant boilerplate by reading existing project patterns — models, endpoints, services, tests, full features
- `/generate-tests`: Write tests for existing code following project conventions — delegates to test-prophet with worktree isolation
- `/track-debt`: Scan TODO/FIXME/HACK, complexity hotspots, coverage gaps — maintain a living debt ledger with trend tracking

##### Phase 2 — Strong value, moderate effort (4 new)
- `/incident`: Structured incident triage, hotfix coordination, runbook generation, and postmortem templates
- `/analyse-queries`: SQL/ORM analysis for missing indexes, N+1 patterns, full table scans, with specific CREATE INDEX recommendations
- `/git-workflow`: Complex git operations — merge conflict resolution with context, cherry-pick strategy, branch cleanup, bisect-based debugging
- `/coverage-audit`: Risk-prioritised test coverage analysis — classifies uncovered code by risk, chains into `/generate-tests`

##### Phase 3 — Rounding out the team (4 new)
- `/retro`: Structured retrospective from git history — identifies hotspots, revert frequency, churn patterns, produces action items
- `/infra-review`: Dockerfile, Kubernetes manifest, docker-compose, and CI/CD config best-practice audit
- `/mutation-test`: Evaluate test quality by introducing code mutations and checking if tests catch them — runs in worktree isolation
- `/test-health`: Detect flaky tests, stale assertions, non-deterministic patterns, and test coupling issues

### Changed
- **senior-council**: Added Task() references for 3 new grumpy reviewers (privacy-paranoid, i18n-nitpicker, budget-hawk)
- **deliberation-conductor**: Added Task() references for 3 new grumpy reviewers
- **Agent count**: 33 agents (up from 30) — 3 new grumpy reviewers
- **Command count**: 46 commands (up from 34) — 12 new commands across 3 phases
- **Grumpy reviewer count**: 12 (up from 9) — now covers privacy, i18n, and cloud cost

## [1.7.0] - 2026-03-31

### Added

#### Claude Code Feature Adoption (v2.1.45–v2.1.88)

##### initialPrompt for Planning Agents
- **project-oracle**: Auto-starts the project planning interview on spawn
- **scope-weaver**: Auto-starts the roadmap scoping workflow on spawn
- Deliberation-conductor excluded — orchestrators should react to input, not auto-fire

##### Effort Frontmatter on All 34 Commands
- **High effort** (4): summon-council, debate-topic, parliament-review, implement-task-list
- **Medium effort** (17): plan-project, changelog-review, security-scan, summon-specialist, and 13 others
- **Low effort** (13): list-agents, version, readme, format-code, run-tests, and 8 others

##### ${CLAUDE_PLUGIN_DATA} for Plugin State
- All 5 hook scripts now write logs to `${CLAUDE_PLUGIN_DATA}` when available
- Falls back to `.project-files/.telemetry/` (isolated from user planning data)
- Changelog review state migrated to `${CLAUDE_PLUGIN_DATA}/changelog-review/`

#### Shared Hook Helper
- New `src/hooks/_common.sh` — shared payload parsing, path validation, and data directory resolution
- All 5 logging hooks refactored to source this helper (eliminates duplicated boilerplate)

#### Agent Standards Updates
- `initialPrompt` guidelines — only for agents that drive conversation without needing input first
- Command effort tiers with rationale table and specific examples
- Storage contract documented — `CLAUDE_PLUGIN_DATA` for telemetry, `.project-files/` for user data

### Changed
- **Hook scripts**: Refactored from ~30 lines each to ~15 lines by extracting shared `_common.sh`
- **Telemetry isolation**: Fallback path changed from `.project-files/` root to `.project-files/.telemetry/`
- **notify_teams.sh**: Added comment clarifying it does not use `CLAUDE_PLUGIN_DATA` (webhook-only, no logs)
- **README.md**: Updated activity logging path reference
- **.gitignore**: Added `.project-files/.telemetry/`

## [1.6.0] - 2026-03-18

### Breaking Changes

- **Plugin renamed**: `parliament-of-chaos` → `chaos`. All slash commands now use the `chaos:` prefix (e.g. `/chaos:summon-council` instead of `/parliament-of-chaos:summon-council`). Existing users must reinstall:
  ```
  claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
  claude plugin install chaos@chaos
  ```

### Added

#### New Commands (34 total, up from 31)

##### Discovery Commands (3 new)
- `/version`: Display the current Parliament of Chaos version, plugin name, agent/command counts, and repository link
- `/readme`: Display the full README directly in the session for quick reference
- `/changelog`: Display the full version history and changelog

### Changed
- **Plugin name**: Renamed from `parliament-of-chaos` to `chaos` for shorter slash command prefixes
- **Command count**: 34 commands (up from 31) — added 3 discovery commands
- **Install/update commands**: Now use `chaos@chaos` format
- **All documentation**: Updated to reflect new plugin name and commands

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

[1.9.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.8.1...v1.9.0
[1.8.1]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.8.0...v1.8.1
[1.8.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/V1.0.0...v1.1.0
[1.0.0]: https://github.com/JackScammell/Parliament-Of-Chaos/releases/tag/V1.0.0
