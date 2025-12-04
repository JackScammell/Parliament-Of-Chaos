# Feature Implementation: Parliament of Chaos

## Feature Categories

### 1. Specialist Agents

Agents that perform specific types of work. Each is an expert in their domain.

#### Existing (v1.0)

| Agent | Domain | Status |
|-------|--------|--------|
| project-oracle | Project scoping via Q&A | Complete |
| scope-weaver | Roadmap item specs and tasks | Complete |
| task-executor | Systematic task implementation | Complete |
| backend-goblin | Backend performance | Complete |
| data-warlock | Data modeling and queries | Complete |
| security-knight | Security implementation | Complete |
| system-architect | System design | Complete |
| resilience-tamer | Error handling, retries, failover | Complete |
| ui-ux-guru | UI/UX and accessibility | Complete |
| api-keeper | API design and contracts | Complete |
| pipeline-engineer | CI/CD and DevOps | Complete |
| package-wizard | Dependencies and packaging | Complete |
| doc-bard | Documentation | Complete |
| test-prophet | Testing strategy | Complete |

#### New (v1.1)

| Agent | Domain | Description |
|-------|--------|-------------|
| migration-monk | Database migrations | Schema changes, data transformations, rollback strategies |
| dependency-detective | Dependency analysis | Vulnerability scanning, update recommendations, license compliance |
| refactor-ranger | Code refactoring | Code smell detection, refactoring patterns, incremental improvements |
| config-curator | Configuration management | Environment configs, secrets management, feature flags |
| observability-oracle | Observability | Logging standards, metrics, distributed tracing, alerting setup |

---

### 2. Grumpy Reviewers

Agents that critique work from specific angles. They don't implement - they nitpick.

#### Existing (v1.0)

| Agent | Nitpicks About | Status |
|-------|----------------|--------|
| grumpy-code-reviewer | General code quality | Complete |
| grumpy-standards-enforcer | Standards compliance | Complete |
| grumpy-architecture-skeptic | Architecture decisions | Complete |
| grumpy-maintainability-curmudgeon | Maintainability | Complete |
| grumpy-security-nag | Security issues | Complete |
| grumpy-performance-troll | Performance problems | Complete |

#### New (v1.1)

| Agent | Nitpicks About | Description |
|-------|----------------|-------------|
| grumpy-accessibility-auditor | Accessibility | WCAG compliance, screen reader support, keyboard navigation |
| grumpy-documentation-pedant | Documentation | Missing docs, unclear explanations, outdated examples |
| grumpy-testing-tyrant | Test quality | Coverage gaps, missing edge cases, flaky tests |

---

### 3. Commands

Slash commands that orchestrate agents and manage workflow.

#### Existing (v1.0)

| Command | Purpose | Status |
|---------|---------|--------|
| /summon-council | Orchestrate full specialist + review cycle | Complete |
| /summon-grumpy-reviewer | Run grumpy review on code | Complete |
| /plan-project | Interactive project planning | Complete |
| /project-status | Show project progress dashboard | Complete |
| /roadmap-item-scope | Scope a roadmap item into tasks | Complete |
| /implement-task-list | Execute tasks systematically | Complete |

#### New (v1.1)

| Command | Purpose | Description |
|---------|---------|-------------|
| /summon-specialist `<name>` | Call individual specialist | Direct access to any specialist without full council |
| /parliament-review | Review-only mode | Run grumpy council on existing code without implementation |
| /explain-agent `<name>` | Describe agent | Show what an agent does, when to use it, example usage |
| /list-agents | List all agents | Display all agents grouped by category with descriptions |

---

### 4. Quality of Life Features

Features that enhance the overall experience.

#### New (v1.1)

| Feature | Description | Implementation Notes |
|---------|-------------|---------------------|
| Agent memory/context | Pass learnings between roadmap items | Store context in `.project-files/context/` |
| Configurable grumpiness | Adjust reviewer strictness | Levels: strict, balanced, lenient via command arg |
| Review report export | Generate markdown summary | Output to `.project-files/reviews/` |
| Conflict resolution | Tiebreaker for disagreements | senior-council agent arbitrates disputes |

---

### 5. Integrations

External system integrations.

#### Existing (v1.0)

| Integration | Purpose | Status |
|-------------|---------|--------|
| Teams webhook | Alert when Claude is waiting | Complete (via hooks) |

---

## Implementation Priority

### Phase 1: New Agents
1. migration-monk
2. dependency-detective
3. refactor-ranger
4. config-curator
5. observability-oracle
6. grumpy-accessibility-auditor
7. grumpy-documentation-pedant
8. grumpy-testing-tyrant

### Phase 2: New Commands
1. /list-agents
2. /explain-agent
3. /summon-specialist
4. /parliament-review

### Phase 3: Quality of Life
1. Review report export
2. Configurable grumpiness levels
3. Conflict resolution mechanism
4. Agent memory/context

---

**Related Documents**:
- [Project Outline](./project-outline.md)
- [Roadmap](./Roadmap.md)
