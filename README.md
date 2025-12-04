<img width="1024" height="1024" alt="Parliament of Chaos logo" src="https://github.com/user-attachments/assets/1db1114d-505f-4cf9-807d-6b6054286e41" />

# Parliament of Chaos

**A Claude Code plugin that summons a council of opinionated AI specialists to plan, build, review, and refine your projects through structured debate and iteration.**

---

## What Is This?

Parliament of Chaos transforms Claude Code into a multi-agent development team. Instead of a single AI assistant, you get:

- **29 Agents** including specialists, planners, reviewers, and an orchestrator
- **9 Grumpy Reviewers** who find flaws others miss
- **12 Slash Commands** for project planning, scoping, implementation, and code review

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

---

## Agents

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

### Orchestrator (1)

| Agent | Role |
|-------|------|
| senior-council | Coordinates all agents, runs iterative review cycles until approval |

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

## Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/installation.md) | Detailed setup instructions and troubleshooting |
| [Usage Guide](docs/usage.md) | In-depth command usage with examples |
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

---

## License

MIT
