<img width="1024" height="1024" alt="Parliament of Chaos logo" src="https://github.com/user-attachments/assets/1db1114d-505f-4cf9-807d-6b6054286e41" />

# Parliament of Chaos

**A Claude Code plugin that summons a council of opinionated AI specialists to plan, build, review, and refine your projects through structured debate and iteration.**

---

## What Is This?

Parliament of Chaos transforms Claude Code into a multi-agent development team. Instead of a single AI assistant, you get:

- **30 Agents** including specialists, planners, reviewers, and orchestrators
- **9 Grumpy Reviewers** who find flaws others miss
- **13 Slash Commands** for project planning, scoping, implementation, code review, and structured deliberation

The result: thoroughly planned projects, battle-tested code, and solutions that have survived scrutiny from multiple perspectives.

---

## Quick Start

### Install the Plugin

```
/install-github-plugin JackScammell/Parliament-Of-Chaos
```

### Your First Command

**For code review and development tasks:**

```
/summon-council Design an authentication system with JWT and RBAC
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

### Analytics & Plugin Commands

| Command | Description |
|---------|-------------|
| `/debate-analytics [topic]` | **NEW**: Generate comprehensive analytics dashboard with metrics, influence scores, and insights |
| `/plugin-install <name>` | **NEW**: Install community agent plugins from the marketplace |
| `/plugin-list` | **NEW**: List all installed plugins and marketplace summary |

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

### Orchestrators (2)

| Agent | Role |
|-------|------|
| senior-council | Coordinates all agents, runs iterative review cycles until approval |
| deliberation-conductor | Orchestrates structured debates with parallel execution and convergence detection |

---

## How It Works

### The Council Workflow

When you invoke `/summon-council`:

1. **Analyse** - The Senior Council identifies which domains your task requires
2. **Dispatch** - Appropriate specialists are selected and consulted
3. **Review** - All outputs pass through the grumpy reviewer panel
4. **Iterate** - Feedback routes back to specialists until all reviewers approve. Conflicts resolved via priority (security > correctness > maintainability > performance)
5. **Synthesise** - Final solution is delivered with documented trade-offs

### The Planning Workflow

When you invoke `/plan-project`:

1. **Discovery** - The Project Oracle asks clarifying questions about your project
2. **Outline** - Creates `project-outline.md` with goals, constraints, and scope
3. **Features** - Generates `feature-implementation.md` breaking down capabilities
4. **Roadmap** - Produces `Roadmap.md` with phased implementation plan

Then use `/roadmap-item-scope` to expand items into specs and tasks, and `/implement-task-list` to execute them with full council oversight (specialists implement, grumpy reviewers approve).

---

## Enhanced Features

Parliament of Chaos now includes advanced features leveraging Claude Code's latest capabilities:

### 🎯 Context Optimization and Management **ENHANCED**
- **70% Token Reduction**: Accurate token counting with tiktoken, dynamic pruning, and deduplication
- **Session Token Monitor**: Real-time tracking with automatic compression triggers
- **Token Budget Enforcer**: Per-agent budget limits with automatic context compression
- **Statement Deduplication**: Jaccard similarity detection to prevent redundant arguments
- **Context Pruning**: Remove low-confidence statements while preserving high-influence agents
- **Bounded Memory**: Token usage independent of debate length
- **Multi-Session Support**: Persist and restore context across sessions
- **Semantic Retrieval**: Optional vector memory integration for relevant arguments
- **Token Tracking**: Real-time metrics and optimization statistics
- **Backward Compatible**: Opt-in system maintaining legacy support

### 🤝 Native Agent Teams Integration
- **Structured Debate Teams**: Advocate, Opponent, Moderator, and Synthesis roles
- **Parallel Execution**: Teams work simultaneously for faster deliberation
- **Real-time Coordination**: Visual output showing debate activity and progress

### 🧠 Persistent Memory System
- **Cross-Session Learning**: Remember debates across projects
- **Pattern Recognition**: Track conceptual evolution and solutions
- **Semantic Search**: Find relevant past discussions by topic

### 🔌 Plugin Marketplace
- **Community Agents**: Install specialist agents from the marketplace
- **Extensible System**: `/plugin-install [name]` to add new capabilities
- **Skill Trees**: Hierarchical expertise for token-efficient specialization

### 📊 Debate Analytics Dashboard
- **Comprehensive Metrics**: Consensus scores, agent influence, argument novelty
- **Visual Reports**: Markdown dashboards with trends and insights
- **Performance Tracking**: Token usage, latency, time to convergence

### 🎯 Advanced Governance Models
- **Confidence-Weighted Voting**: Votes weighted by agent confidence
- **Coalition Formation**: Agents align based on positions and values
- **Delegated Voting**: High-confidence agents receive more weight
- **Supermajority & Quadratic**: Multiple voting system options

### ⚙️ User-Driven Constraints
- **YAML Configuration**: Define debate rules and patterns to avoid
- **Automatic Validation**: Agents check against constraints
- **Custom Rules**: Pattern matching and requirement enforcement

### 🔄 Multi-Session Debate Chaining
- **Stateful Debates**: Carry context across multiple sessions
- **Conflict Tracking**: Monitor and resolve unresolved issues
- **Session Summaries**: Compressed history for long-running topics

### 🎓 Self-Improving Agents
- **Meta-Learning**: Track strategy performance over time
- **Adaptive Behavior**: Agents learn from past debates
- **Pattern Evolution**: Identify successful and failed approaches

---

## Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/installation.md) | Detailed setup instructions and troubleshooting |
| [Update Guide](docs/UPDATE.md) | **How plugin updates work - NOT automatic** |
| [Usage Guide](docs/usage.md) | In-depth command usage with examples |
| [Deliberation System](docs/DELIBERATION_SYSTEM.md) | Multi-agent deliberation architecture and features |
| [Context Optimization](docs/CONTEXT_OPTIMIZATION.md) | Token reduction architecture and design |
| [Token Reduction Guide](docs/TOKEN_REDUCTION_GUIDE.md) | Complete guide to session token reduction features |
| [Hooks Configuration](docs/hooks.md) | Set up notifications and automated actions |
| [Safe Progress Assurance](docs/safe-progress-assurance.md) | How the system ensures reliable task completion |
| [Example Project Files](docs/example-project-files/) | Sample outputs from the planning workflow |

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
/install-github-plugin JackScammell/Parliament-Of-Chaos
```

For detailed installation steps, verification, and troubleshooting, see the [Installation Guide](docs/installation.md).

### Updating

**Important:** Claude Code does NOT automatically update plugins.

To update to the latest version, re-run:
```
/install-github-plugin JackScammell/Parliament-Of-Chaos
```

For complete update instructions and FAQs, see the [Update Guide](docs/UPDATE.md).

---

## License

MIT
