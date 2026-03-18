<img width="1024" height="1024" alt="Parliament of Chaos logo" src="https://github.com/user-attachments/assets/1db1114d-505f-4cf9-807d-6b6054286e41" />

# Parliament of Chaos

**A Claude Code plugin that summons a council of opinionated AI specialists to plan, build, review, and refine your projects through structured debate and iteration.**

---

## What Is This?

Parliament of Chaos transforms Claude Code into a multi-agent development team. Instead of a single AI assistant, you get:

- **30 Agents** including specialists, planners, reviewers, and orchestrators
- **9 Grumpy Reviewers** who find flaws others miss
- **22 Slash Commands** for project planning, code review, deliberation, monitoring, and operations

The result: thoroughly planned projects, battle-tested code, and solutions that have survived scrutiny from multiple perspectives.

---

## Quick Start

### Install the Plugin

```
claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
claude plugin install parliament-of-chaos@parliament-of-chaos
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

### Council Commands

| Command | Description |
|---------|-------------|
| `/summon-council [task]` | Orchestrate specialists + grumpy review cycle for complex tasks |
| `/summon-grumpy-reviewer` | Quick, ruthless code review from a senior developer perspective |
| `/parliament-review` | Full review using all 9 grumpy reviewers for maximum scrutiny |
| `/summon-specialist <agent>` | Directly invoke a specialist agent on your current task |
| `/debate-topic [topic]` | Run structured multi-agent deliberation with convergence detection |

### Discovery Commands

| Command | Description |
|---------|-------------|
| `/list-agents` | Display all agents grouped by category |
| `/list-commands` | Display all commands grouped by category |
| `/explain-agent <agent>` | Detailed explanation of what an agent does and when to use it |

### Project Planning Commands

| Command | Description |
|---------|-------------|
| `/plan-project [description]` | Interactive Q&A to create project-outline.md, feature-implementation.md, and Roadmap.md |
| `/project-status` | Dashboard showing roadmap progress across all phases |
| `/roadmap-add-item <name> --phase <n>` | Add a new item to an existing roadmap |
| `/roadmap-item-scope <item>` | Create detailed Spec.md and tasks.md for a roadmap item |
| `/implement-task-list [item]` | Execute tasks with full council review (specialists + grumpy approval) |

### Codebase Analysis Commands

| Command | Description |
|---------|-------------|
| `/onboard-codebase` | Analyse an undocumented codebase in parallel and generate comprehensive `docs/getting_started/` documentation |

### Operations Commands

| Command | Description |
|---------|-------------|
| `/parliament-optimize` | Audit agent definitions and recommend effort/model settings |
| `/parliament-webhook` | Configure webhook notification endpoints (Teams, Slack, Discord) |
| `/parliament-loop` | Set up recurring Parliament commands via `/loop` integration |
| `/parliament-monitor` | Manage background monitoring agents for continuous oversight |
| `/changelog-review` | Review Claude Code changelog and propose new features |

### Analytics & Plugin Commands

| Command | Description |
|---------|-------------|
| `/debate-analytics [topic]` | Generate comprehensive analytics dashboard with metrics and insights |
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

### Grumpy Reviewers (9)

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

---

## How It Works

### The Council Workflow

When you invoke `/summon-council`:

1. **Analyse** - The Senior Council identifies which domains your task requires
2. **Dispatch** - Appropriate specialists are selected and consulted
3. **Review** - All outputs pass through the grumpy reviewer panel
4. **Iterate** - Feedback routes back to specialists until all reviewers approve. Conflicts resolved via priority (security > correctness > maintainability > performance)
5. **Synthesise** - Final solution is delivered with documented trade-offs

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
- **Continuous Oversight**: All 9 grumpy reviewers have `background: true` for persistent monitoring
- **Managed via `/parliament-monitor`**: Start, stop, and check status of background agents
- **Low Overhead**: Reviewers use `effort: low` and `maxTurns: 5` for minimal resource consumption

### Hook System
- **10 Hook Events**: Notification, Stop, StopFailure, TaskCompleted, SubagentStart, PostCompact, InstructionsLoaded, TeammateIdle, PreToolUse, PostToolUse
- **Teams/Slack/Discord**: Webhook notifications via `/parliament-webhook`
- **Activity Logging**: All events logged to `.project-files/agent-logs/activity.jsonl`
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
- **Read-Only Reviewers**: All 9 grumpy reviewers have `disallowedTools: [Edit, Write, NotebookEdit, Bash]`

---

## Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/installation.md) | Detailed setup instructions and troubleshooting |
| [Update Guide](docs/UPDATE.md) | **How plugin updates work - NOT automatic** |
| [Usage Guide](docs/usage.md) | In-depth command usage with examples |
| [API Reference](docs/API_REFERENCE.md) | Python library API documentation |
| [Development Guide](docs/DEVELOPMENT.md) | Development environment setup and contribution workflow |
| [Deliberation System](docs/DELIBERATION_SYSTEM.md) | Multi-agent deliberation architecture and features |
| [Context Optimization](docs/CONTEXT_OPTIMIZATION.md) | Token reduction architecture and design |
| [Token Reduction Guide](docs/TOKEN_REDUCTION_GUIDE.md) | Complete guide to session token reduction features |
| [Hooks Configuration](docs/hooks.md) | Set up notifications and automated actions |
| [Safe Progress Assurance](docs/safe-progress-assurance.md) | How the system ensures reliable task completion |
| [Example Project Files](docs/example-project-files/) | Sample outputs from the planning workflow |
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
```

---

## Installation

```
claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
claude plugin install parliament-of-chaos@parliament-of-chaos
```

For detailed installation steps, verification, and troubleshooting, see the [Installation Guide](docs/installation.md).

### Updating

**Important:** Claude Code does NOT automatically update plugins.

To update to the latest version:
```
claude plugin update parliament-of-chaos@parliament-of-chaos
```

For complete update instructions and FAQs, see the [Update Guide](docs/UPDATE.md).

---

## License

MIT
