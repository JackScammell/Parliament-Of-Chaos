<img width="1024" height="1024" alt="Parliament of Chaos logo" src="https://github.com/user-attachments/assets/1db1114d-505f-4cf9-807d-6b6054286e41" />

# Parliament of Chaos

**A Claude Code plugin that summons a council of opinionated AI specialists to plan, build, review, and refine your projects through structured debate and iteration.**

---

## What Is This?

Parliament of Chaos transforms Claude Code into a multi-agent development team. Instead of a single AI assistant, you get:

- **33 Agents** including specialists, planners, reviewers, and orchestrators
- **12 Grumpy Reviewers** who find flaws others miss (security, quality, privacy, i18n, cost, and more)
- **66 Slash Commands** across 15 categories: project planning, code review, deliberation, developer workflow, hygiene, quality, release, observability, decisions, lifecycle, and operations
- **`commands/manifest.yaml`** — declarative registry that acts as the source of truth for every command, reconciled by `/parliament-doctor`

The result: thoroughly planned projects, battle-tested code, and solutions that have survived scrutiny from multiple perspectives.

---

## Quick Start

### Install the Plugin

```
claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
claude plugin install chaos@chaos
```

### Your First Command

**For code review and development tasks:**

```
/summon-council Design an authentication system with JWT and RBAC
```

**For onboarding to an undocumented codebase:**

```
/onboard-codebase
```

**For planning a new project:**

```
/plan-project A CLI tool for managing Docker containers
```

---

## Commands

All 66 commands are declared in [`commands/manifest.yaml`](commands/manifest.yaml), which acts as the source of truth for command name, status, owner agent, effort tier, and category. Run `/parliament-doctor` to reconcile the manifest against the filesystem and skill registry.

> **Not the same as Claude Code's built-in `/code-review`.** Parliament's review commands (`/summon-grumpy-reviewer`, `/parliament-review`) run the plugin's grumpy-reviewer fleet against your working changes and are invoked directly. Claude Code also ships a separate built-in `/code-review` (as of recent versions, manual-only and dispatched to a background subagent) that is unrelated to Parliament and applies its own review model. When you want the Parliament governance flow, use the `/chaos:` review commands; the bare `/code-review` is the upstream feature.

### Agent Invocation

| Command | Description |
|---------|-------------|
| `/ask-council <question>` | Ask the council a question. Auto-selects 2–5 specialists, consults them in parallel, and returns a single synthesised answer with consensus and disagreements surfaced. No fix loop, no artifact, no code edits |
| `/summon-council [plan\|implement] [task]` | Two-mode orchestrator — `plan` writes a spec to `.project-files/plans/`, `implement` runs full specialist + 9-grump cycle. Always opens with an `Explore` inventory pass so the council extends existing capabilities rather than creating duplicates |
| `/summon-specialist <agent>` | Directly invoke a specialist agent on your current task |
| `/summon-grumpy-reviewer` | Quick, ruthless code review from a senior developer perspective |
| `/parliament-review` | Grumpy-reviewer review — relevance-tiered by default (only reviewers whose domain the diff touches); `--all` forces the full 9 for maximum scrutiny. The security + correctness floor (+ privacy on PII) is always present |

### Deliberation

| Command | Description |
|---------|-------------|
| `/debate-topic [topic]` | Structured multi-agent deliberation with convergence detection |
| `/debate-analytics [topic]` | Analytics dashboard with metrics and insights for a debate |
| `/debate-replay <session>` | Deterministic replay of a past debate from a session snapshot |

### Project Planning

| Command | Description |
|---------|-------------|
| `/plan-project [description]` | Interactive Q&A to create project-outline.md, feature-implementation.md, and Roadmap.md |
| `/project-status` | Dashboard showing roadmap progress across all phases |
| `/roadmap-add-item <name> --phase <n>` | Add a new item to an existing roadmap |
| `/roadmap-item-scope <item>` | Create detailed Spec.md and tasks.md for a roadmap item |
| `/implement-task-list [item]` | Execute tasks with full council review (specialists + grumpy approval) |

### Developer Workflow

| Command | Description |
|---------|-------------|
| `/pre-commit-check` | Auto-detect and run all CI checks locally before committing |
| `/commit-and-push` | Drafts a commit message, runs pre-flight checks, audits push safety, and emits a copy-paste git command block. **Never** executes git commit/push/tag — those are explicit developer actions |
| `/format-code` | Auto-detect and run the project's code formatter |
| `/lint-fix` | Auto-detect and run linter(s) with auto-fix |
| `/run-tests [--changed] [--explain]` | Auto-detect and run the test suite with intelligent options |
| `/security-scan` | Unified security check: dependencies, secrets, vulnerability patterns |
| `/clean-imports` | Remove unused imports and organise import ordering |
| `/update-dependencies` | Interactive dependency update with changelog review and test verification |
| `/dead-code-sweep` | Find unreachable code, unused exports, and orphaned files |
| `/update-docs` | Detect and update documentation affected by recent code changes |
| `/analyse-queries` | SQL/ORM analysis for missing indexes, N+1 patterns, full table scans |
| `/git-workflow` | Complex git operations — merge conflicts, cherry-picks, bisect |
| `/scaffold` | Generate convention-compliant boilerplate by reading existing patterns |

### Quality

| Command | Description |
|---------|-------------|
| `/coverage-audit` | Risk-prioritised test coverage analysis |
| `/generate-tests` | Write tests for existing code following project conventions |
| `/mutation-test` | Evaluate test quality by introducing code mutations |
| `/test-health` | Detect flaky tests, stale assertions, non-deterministic patterns |
| `/track-debt` | Scan TODO/FIXME/HACK, complexity hotspots, coverage gaps |
| `/i18n-audit` | Scan user-facing strings, pluralisation, locale-aware formatting |

### Release

| Command | Description |
|---------|-------------|
| `/cut-release` | Automate version bumping, changelog generation, git tagging |
| `/release-notes-draft` | Draft CHANGELOG entries from git log and merged PRs since last tag |
| `/plugin-upgrade` | Version-sync helper — bumps plugin.json, marketplace.json, CHANGELOG atomically |

### Decisions

| Command | Description |
|---------|-------------|
| `/adr-new` | Scaffold new Architectural Decision Records under `.project-files/adrs/` |
| `/adr-supersede` | Mark an ADR superseded and forward-link it to its replacement |
| `/decision-review` | Re-evaluate a prior ADR, debate, or council ruling |

### Observability

| Command | Description |
|---------|-------------|
| `/telemetry-query` | Ad-hoc read path over `activity.jsonl` and plugin data directory |
| `/parliament-metrics` | Cost, latency, SLO, and trend dashboard from telemetry |
| `/cost-report` | Dry-run estimates, soft caps, and post-flight retrospectives |

### Lifecycle

| Command | Description |
|---------|-------------|
| `/session-snapshot` | Checkpoint/resume primitive — `create`, `list`, `resume`, `show`, `prune` |
| `/docs-audit` | Symmetric opposite of `/onboard-codebase` — detects doc drift |
| `/settings-audit` | Permissions, secrets, feature flags, hooks, and scope diff audit |
| `/env-doctor` | Runtime environment validator — hook locations, data dirs, tool availability |
| `/fast-track` | Minimum-review-floor bypass (never below security + code review) with logged review debt |
| `/ci-watch` | Poll CI for the current branch — GitHub Actions, GitLab CI, CircleCI |

### Operations

| Command | Description |
|---------|-------------|
| `/parliament-optimize` | Audit agent definitions and recommend effort/model settings |
| `/parliament-webhook` | Configure webhook notification endpoints (Teams, Slack, Discord) |
| `/parliament-loop` | Set up recurring Parliament commands via `/loop` integration |
| `/parliament-monitor` | Manage background monitoring agents for continuous oversight |
| `/changelog-review` | Review Claude Code changelog and propose new features |
| `/incident` | Structured incident triage, hotfix coordination, postmortems |
| `/infra-review` | Dockerfile, Kubernetes, docker-compose, and CI/CD config audit |
| `/retro` | Structured retrospective from git history — hotspots, churn, revert patterns |
| `/agent-usage-stats` | Per-agent frequency, duration, token cost, and approval-rate stats |

### Hygiene

| Command | Description |
|---------|-------------|
| `/parliament-doctor` | Reconcile `commands/manifest.yaml` against `commands/*.md` and skill registry |

### Codebase Analysis

| Command | Description |
|---------|-------------|
| `/onboard-codebase` | Analyse an undocumented codebase in parallel and generate `docs/getting_started/` |

### Discovery

| Command | Description |
|---------|-------------|
| `/list-agents` | Display all agents grouped by category |
| `/list-commands` | Display all commands grouped by category (reads manifest) |
| `/explain-agent <agent>` | Detailed explanation of what an agent does and when to use it |
| `/version` | Display current plugin version and metadata |
| `/readme` | Display the full README in the session |
| `/changelog` | Display the full version history |

### Plugins

| Command | Description |
|---------|-------------|
| `/plugin-install <name>` | Install community agent plugins from the marketplace |
| `/plugin-list` | List all installed plugins and marketplace summary |

---

## Agents

### Orchestration Agents (2)

| Agent | Role |
|-------|------|
| senior-council | Coordinates all agents, runs iterative review cycles until approval |
| deliberation-conductor | **NEW**: Orchestrates structured debates with parallel execution and convergence detection |

### Planning Agents (3)

| Agent | Role |
|-------|------|
| project-oracle | Conducts project scoping via Q&A, creates project outline and roadmap |
| scope-weaver | Breaks roadmap items into detailed specs and actionable tasks |
| task-executor | Handles task tracking, safety checks, and documentation (utility for senior-council) |

### Specialist Agents (16)

| Agent | Domain |
|-------|--------|
| system-architect | High-level design, patterns, trade-offs |
| backend-goblin | Backend performance, caching, async patterns |
| security-knight | Authentication, vulnerabilities, hardening |
| data-warlock | Database design, queries, migrations |
| api-keeper | API design, versioning, contracts |
| test-prophet | Testing strategy, coverage, TDD |
| ui-ux-guru | Accessibility, UX patterns, frontend |
| pipeline-engineer | CI/CD, deployment, infrastructure |
| doc-bard | Documentation, comments, READMEs |
| package-wizard | Dependencies, versions, compatibility |
| resilience-tamer | Error handling, retries, failure modes |
| migration-monk | Schema migrations, rollback strategies |
| dependency-detective | Vulnerability chains, license compliance |
| refactor-ranger | Code smells, refactoring patterns |
| config-curator | Environment config, secrets, feature flags |
| observability-oracle | Logging, metrics, tracing, alerting |

### Grumpy Reviewers (12)

| Agent | Focus |
|-------|-------|
| grumpy-code-reviewer | Overall code quality |
| grumpy-standards-enforcer | Coding standards compliance |
| grumpy-architecture-skeptic | Architectural decisions |
| grumpy-maintainability-curmudgeon | Long-term maintenance burden |
| grumpy-security-nag | Security oversights |
| grumpy-performance-troll | Performance issues |
| grumpy-accessibility-auditor | WCAG compliance, inclusive design |
| grumpy-documentation-pedant | Documentation completeness |
| grumpy-testing-tyrant | Test coverage and quality |
| grumpy-privacy-paranoid | PII exposure, GDPR/CCPA compliance, consent, data retention |
| grumpy-i18n-nitpicker | Hardcoded strings, missing translations, pluralisation, locale formatting |
| grumpy-budget-hawk | Cloud cost impact, over-provisioned resources, unbounded queries |

---

## How It Works

### The Council Workflow

`/summon-council` runs in one of two modes:

- **`plan` mode** — produces a written plan at `.project-files/plans/<slug>.md`. No code edits. Uses a planning-specialist subset and a plan-shaped reviewer subset (architecture, maintainability, security, performance, with budget/privacy/testing added when the topic warrants).
- **`implement` mode** — coordinates specialists and the full 9-grump panel to ship working code.

If the mode is not given and cannot be inferred from the topic, the council asks before doing any work. Pure review requests (no fix loop) are redirected to `/parliament-review`.

Both modes follow the same five steps:

1. **Inventory** — the council dispatches the `Explore` agent to find existing helpers, utilities, services, modules, and tests related to the topic. Default rule: **extend existing capabilities; only create new ones when a specialist gives a concrete reason.** The inventory is shared with every specialist spawned.
2. **Analyse** — the Senior Council restates the goal and identifies which domains the task requires.
3. **Dispatch** — appropriate specialists are selected and consulted, referencing the inventory.
4. **Review** — outputs pass through the relevant reviewer subset (plan-shaped for `plan` mode, all 9 grumps for `implement` mode).
5. **Iterate & synthesise** — feedback routes back to specialists until reviewers approve or trade-offs are documented. Conflicts resolved via priority (security > correctness > maintainability > performance > convenience).

### The Onboarding Workflow

When you invoke `/onboard-codebase`:

1. **Parallel Analysis** - 11 specialists fan out simultaneously, each analysing the codebase through their lens (architecture, APIs, database, config, tests, security, etc.)
2. **Documentation Generation** - The Doc Bard compiles all specialist reports into up to 17 comprehensive getting-started guides
3. **Quality Review** - The Grumpy Documentation Pedant reviews every file for accuracy, completeness, and fabrication
4. **Iteration** - Issues are fixed and re-reviewed until approved
5. **Delivery** - Complete `docs/getting_started/` directory ready for new developers

### The Planning Workflow

When you invoke `/plan-project`:

1. **Discovery** - The Project Oracle asks clarifying questions about your project
2. **Outline** - Creates `project-outline.md` with goals, constraints, and scope
3. **Features** - Generates `feature-implementation.md` breaking down capabilities
4. **Roadmap** - Produces `Roadmap.md` with phased implementation plan

Then use `/roadmap-item-scope` to expand items into specs and tasks, and `/implement-task-list` to execute them with full council oversight (specialists implement, grumpy reviewers approve).

---

## Features

### Agent Effort Tiers (v1.4.0)
- **Cost-Optimised Reasoning**: Orchestrators use `effort: high`, specialists use `effort: medium`, reviewers use `effort: low` — estimated 40-60% token savings on review tasks
- **Turn Limits**: `maxTurns` per agent role prevents runaway sessions (orchestrators 30, specialists 15, reviewers 5)
- **Persistent Memory**: All agents have scoped memory (`memory: project` for specialists, `memory: user` for reviewers) for cross-session knowledge

### Worktree Isolation
- **Parallel Implementation**: 15 of 16 specialists work in isolated git worktrees via `isolation: worktree` (system-architect excluded — read-only advisory agent)
- **No Conflicts**: Each specialist operates on an isolated copy of the repo
- **Automatic Cleanup**: Worktrees are cleaned up after the agent finishes

### Background Monitoring (v1.4.0)
- **Continuous Oversight**: All 12 grumpy reviewers have `background: true` for persistent monitoring
- **Managed via `/parliament-monitor`**: Start, stop, and check status of background agents
- **Low Overhead**: Reviewers use `effort: low` and `maxTurns: 5` for minimal resource consumption

### Hook System
- **10 Hook Events**: Notification, Stop, StopFailure, TaskCompleted, SubagentStart, PostCompact, InstructionsLoaded, TeammateIdle, PreToolUse, PostToolUse
- **Teams/Slack/Discord**: Webhook notifications via `/parliament-webhook`
- **Activity Logging**: All events logged to `${CLAUDE_PLUGIN_DATA}/agent-logs/activity.jsonl` (falls back to `.project-files/.telemetry/`)
- **Security Hardened**: Path validation, HTTPS enforcement, secrets gitignored

### Context Optimisation
- **70% Token Reduction**: Accurate token counting, dynamic pruning, and deduplication
- **Session Token Monitor**: Real-time tracking with automatic compression triggers
- **Statement Deduplication**: Jaccard similarity detection to prevent redundant arguments
- **Bounded Memory**: Token usage independent of debate length

### Structured Deliberation
- **4 Debate Modes**: fast (3 rounds), adversarial (5-7), consensus (5), deep (7-10)
- **4 Voting Systems**: majority, supermajority, quadratic, influence-weighted
- **Convergence Detection**: Automatic early termination when consensus reached
- **Performance Metrics**: Token usage, latency, convergence trajectory

### Agent Teams Abstraction (v1.4.0)
- **CommunicationLayer**: Unified interface for inter-agent messaging
- **Task()-Based Today**: Stable implementation using current subagent model
- **Agent Teams Ready**: Experimental path behind `PARLIAMENT_USE_AGENT_TEAMS=1` feature flag
- **Go/No-Go Gate**: Activates only when Agent Teams exits Claude Code research preview

### Governance
- **Conflict Resolution**: security > correctness > maintainability > performance > convenience
- **Agent Standards**: `.claude/rules/agent-standards.md` enforces frontmatter consistency
- **Read-Only Reviewers**: All 12 grumpy reviewers have `disallowedTools: [Edit, Write, NotebookEdit, Bash]`
- **Command Manifest**: `commands/manifest.yaml` is the source of truth for every slash command — `/parliament-doctor` reconciles it against the filesystem and skill registry and gates releases in `--strict` mode

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/ARCHITECTURE.md) | **Start here** — how the Claude Code plugin and the Python deliberation library relate |
| [Installation Guide](docs/installation.md) | Detailed setup instructions and troubleshooting |
| [Update Guide](docs/UPDATE.md) | **How plugin updates work - NOT automatic** |
| [Usage Guide](docs/usage.md) | In-depth command usage with examples |
| [API Reference](docs/API_REFERENCE.md) | Python library API documentation |
| [Development Guide](docs/DEVELOPMENT.md) | Development environment setup and contribution workflow |
| [Deliberation System](docs/DELIBERATION_SYSTEM.md) | Multi-agent deliberation architecture and features |
| [Enhanced Features](docs/ENHANCED_FEATURES.md) | Persistent memory, plugin marketplace, skill trees, governance, and self-improvement modules |
| [Context Optimization](docs/CONTEXT_OPTIMIZATION.md) | Token reduction architecture and design |
| [Token Reduction Guide](docs/TOKEN_REDUCTION_GUIDE.md) | Complete guide to session token reduction features |
| [Hooks Configuration](docs/hooks.md) | Set up notifications and automated actions |
| [Safe Progress Assurance](docs/safe-progress-assurance.md) | How the system ensures reliable task completion |
| [Example Project Files](docs/example-project-files/) | Sample outputs from the planning workflow |
| [Command Manifest](commands/manifest.yaml) | Declarative registry of every slash command (source of truth) |
| [Agent Standards](.claude/rules/agent-standards.md) | Frontmatter, effort tiers, maxTurns, memory, and isolation conventions |
| [Governance Rules](.claude/rules/governance.md) | Conflict resolution priority and agent hierarchy |
| [Contributing Guide](CONTRIBUTING.md) | **How to contribute to the project** |
| [Changelog](CHANGELOG.md) | **Version history and release notes** |

---

## Project Files

Parliament of Chaos creates and manages files in `.project-files/`:

```
.project-files/
  project-outline.md      # Project goals, constraints, scope
  feature-implementation.md   # Feature breakdown
  Roadmap.md              # Phased implementation plan
  roadmap/
    <item-name>/
      Spec.md             # Detailed specification
      tasks.md            # Actionable task list
      work_complete.md    # Completion record
  plans/
    <slug>.md             # Ad-hoc plan written by `/summon-council plan` (created lazily)
```

---

## Installation

```
claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
claude plugin install chaos@chaos
```

For detailed installation steps, verification, and troubleshooting, see the [Installation Guide](docs/installation.md).

### Updating

**Important:** Claude Code does NOT automatically update plugins.

To update to the latest version:
```
claude plugin update chaos@chaos
```

For complete update instructions and FAQs, see the [Update Guide](docs/UPDATE.md).

---

## License

MIT
