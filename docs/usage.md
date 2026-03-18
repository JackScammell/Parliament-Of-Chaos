# Usage Guide

This guide explains how to use Parliament of Chaos commands effectively.

## Commands Overview

| Command | Purpose | Best For |
|---------|---------|----------|
| `/plan-project` | Interactive project planning | Starting new projects, defining scope and roadmap |
| `/project-status` | Dashboard showing progress | Tracking overall project state |
| `/roadmap-add-item` | Add items to existing roadmap | Extending scope without re-planning |
| `/roadmap-item-scope` | Create specs and tasks for an item | Breaking down work before implementation |
| `/implement-task-list` | Execute tasks systematically | Safe, tracked implementation |
| `/summon-council` | Full multi-agent orchestration | Complex tasks, architectural decisions |
| `/summon-grumpy-reviewer` | Quick critical code review | Code review, PR feedback, refactoring |
| `/parliament-review` | Full review with all 9 reviewers | Maximum scrutiny on critical code |
| `/summon-specialist <agent>` | Invoke a specific specialist | Focused domain analysis |
| `/debate-topic [topic]` | Structured multi-agent deliberation | Technical decisions, architecture debates |
| `/parliament-optimize` | Audit agent configurations | Verify effort/model settings compliance |
| `/parliament-webhook` | Configure webhook notifications | Teams, Slack, Discord integrations |
| `/parliament-loop` | Recurring command execution | Continuous monitoring during development |
| `/parliament-monitor` | Background monitoring agents | Persistent code oversight |
| `/onboard-codebase` | Parallel codebase analysis | Onboarding to undocumented codebases |
| `/list-agents` | Show all agents by category | Discovering available agents |
| `/list-commands` | Show all commands by category | Discovering available commands |
| `/explain-agent <agent>` | Detailed agent explanation | Understanding agent capabilities |
| `/debate-analytics` | Analytics dashboard | Tracking deliberation patterns |
| `/plugin-install <name>` | Install community plugins | Adding new agent capabilities |
| `/plugin-list` | List installed plugins | Viewing available plugins |
| `/pre-commit-check` | Run all CI checks locally | Ensuring CI passes before pushing |
| `/format-code` | Auto-detect and run formatter | Formatting code before commit |
| `/lint-fix` | Auto-detect and run linter with fix | Fixing lint errors across changed files |
| `/run-tests` | Auto-detect and run test suite | Running tests with smart options |
| `/security-scan` | Unified security scanning | Checking for secrets, vulnerabilities, patterns |
| `/clean-imports` | Remove unused imports | Cleaning up import statements |
| `/update-dependencies` | Interactive dependency updates | Updating packages safely with testing |
| `/dead-code-sweep` | Find unreachable/unused code | Identifying dead code for removal |
| `/update-docs` | Update docs after code changes | Keeping documentation in sync with code |

---

## Workflow Overview

The Parliament of Chaos supports a complete project lifecycle. Here is the typical workflow:

```
/plan-project
      |
      v
/roadmap-add-item (optional - extend scope)
      |
      v
/roadmap-item-scope <item>
      |
      v
/implement-task-list <item>
      |
      v
/project-status (check progress)
```

### Workflow Stages

1. **Plan** - Define your project vision, features, and roadmap
2. **Extend** - Add new items to the roadmap as scope evolves
3. **Scope** - Break down each item into detailed specs and tasks
4. **Implement** - Execute tasks with safety checks and progress tracking
5. **Monitor** - Check overall project status and next actions

---

## Planning Commands

### /plan-project

Initiate an interactive project planning session with the **project-oracle** agent.

#### When to Use

- Starting a new project from scratch
- Defining project scope and requirements
- Creating a development roadmap
- When you have an idea but need structure

#### How It Works

1. **Check Existing Project** - Looks for `.project-files/` directory; offers to continue or start fresh
2. **Context Establishment** - Asks about the problem, users, and motivation
3. **Scope Definition** - Explores MVP features, nice-to-haves, and non-goals
4. **Technical Constraints** - Discusses tech stack, integrations, and requirements
5. **Timeline and Priorities** - Establishes deadlines and priority order
6. **Confirmation** - Summarizes understanding and asks for approval
7. **Generate Artifacts** - Creates project documentation files

#### Example Usage

```
/plan-project
```

Start an interactive Q&A session from scratch.

```
/plan-project Build a task management app for small teams
```

Start with context already provided - the oracle will use this as a starting point.

#### Output Structure

Creates the following files in `.project-files/`:

```
.project-files/
  project-outline.md     # Project overview, goals, and success criteria
  feature-implementation.md  # MVP and future feature lists
  Roadmap.md             # Phased delivery plan with items
```

#### Next Steps

After planning completes:
- Run `/roadmap-item-scope <item>` to detail any roadmap item
- Run `/project-status` to see your progress dashboard

---

### /project-status

Display a dashboard showing the current state of your project.

#### When to Use

- Checking overall project progress
- Seeing which items are complete, in progress, or pending
- Finding what to work on next
- Getting a quick summary for standup or reporting

#### How It Works

1. **Read Project Files** - Parses `.project-files/` for project info
2. **Scan Roadmap Items** - Checks each item folder for status indicators
3. **Generate Report** - Displays formatted status dashboard

#### Example Usage

```
/project-status
```

No arguments required.

#### Status Definitions

| Status | Indicator | Meaning |
|--------|-----------|---------|
| **Not Started** | No folder in `roadmap/` | Listed in Roadmap.md but not yet scoped |
| **Scoped** | Has `Spec.md` and `tasks.md` | Ready for implementation |
| **In Progress** | Some tasks marked complete | Work has begun |
| **Complete** | Has `work_complete.md` | All tasks finished and documented |

#### Sample Output

```markdown
# Project Status: Task Manager Pro

## Overview
A task management application for small teams with real-time collaboration.

## Roadmap Progress

| Item | Status | Tasks | Last Updated |
|------|--------|-------|--------------|
| user-authentication | Complete | 5/5 | 2025-01-15 |
| team-management | In Progress | 3/8 | 2025-01-14 |
| task-boards | Scoped | 0/6 | - |
| notifications | Not Started | - | - |

## Summary
- **Total Items**: 4
- **Completed**: 1 (25%)
- **In Progress**: 1 (25%)
- **Scoped**: 1 (25%)
- **Not Started**: 1 (25%)

## Next Actions
- Continue work on: team-management (5 tasks remaining)
- Ready to implement: task-boards
- Ready to scope: notifications
```

#### Error States

- **No project**: "No project found. Run `/plan-project` to get started."
- **No roadmap**: "Project exists but no roadmap. Run `/plan-project` to create one."

---

### /roadmap-add-item

Add a new item to an existing roadmap phase without re-running full project planning.

#### When to Use

- Extending project scope after initial planning
- Adding features discovered during development
- Including new agents or commands to build
- Quick roadmap updates

#### Syntax

```
/roadmap-add-item <item-name> --phase <n> [--depends <items>]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<item-name>` | Yes | Kebab-case identifier (e.g., `cache-keeper`) |
| `--phase <n>` | Yes | Phase number to add the item to |
| `--depends <items>` | No | Comma-separated dependency item names |

#### Example Usage

```
/roadmap-add-item cache-keeper --phase 1
```

Add a simple item to Phase 1.

```
/roadmap-add-item grumpy-ux-critic --phase 2
```

Add a new reviewer agent to Phase 2.

```
/roadmap-add-item cmd-export-report --phase 3 --depends review-report
```

Add an item that depends on another item.

#### Validation Rules

- Item name must be kebab-case: lowercase letters, numbers, and hyphens
- Phase must already exist in Roadmap.md
- Item name must be unique across all phases
- Dependencies (if specified) must exist in the roadmap

#### Sample Output

```
Added to Roadmap.md, Phase 1 (New Specialist Agents):

| [cache-keeper](./roadmap/cache-keeper/) | Not Started | None |

Updated overall progress: 0 of 17 items

Next step: Run `/roadmap-item-scope cache-keeper` to create the specification and task list.
```

#### What This Command Does NOT Do

- Create folders (deferred to `/roadmap-item-scope`)
- Create Spec.md or tasks.md
- Update feature-implementation.md (update manually if needed)

---

### /roadmap-item-scope

Create a detailed specification and task breakdown for a roadmap item.

#### When to Use

- Before starting implementation of any roadmap item
- Breaking down high-level features into concrete tasks
- Understanding dependencies and integration points
- Getting a clear picture of what "done" looks like

#### Syntax

```
/roadmap-item-scope <item-name>
```

#### Example Usage

```
/roadmap-item-scope user-authentication
```

Scope the user-authentication feature.

```
/roadmap-item-scope api-integration
```

Scope the api-integration feature.

#### How It Works

1. **Validate Item** - Confirms item exists in Roadmap.md
2. **Check Existing Scope** - If already scoped, offers to view or re-scope
3. **Cross-Reference** - Reviews completed work to find overlaps and dependencies
4. **Invoke scope-weaver** - Creates detailed specification and task list
5. **Report Summary** - Shows task count, complexity, and next steps

#### Output Structure

Creates files in `.project-files/roadmap/<item-name>/`:

```
.project-files/
  roadmap/
    <item-name>/
      Spec.md      # Detailed requirements and technical approach
      tasks.md     # Actionable implementation checklist
```

#### Spec.md Contents

- **What**: What this delivers (2-3 sentences)
- **Why**: Why it is needed
- **Requirements**: Checklist of functional requirements
- **Technical Approach**: High-level implementation strategy
- **Dependencies**: What must be done first, what files are affected

#### tasks.md Contents

- **Status**: Current state (Not Started, In Progress, Complete)
- **Tasks**: Ordered list of atomic, actionable items
- **Notes**: Context needed for implementation

#### Next Steps

After scoping completes:
- Run `/implement-task-list <item>` to begin implementation

---

### /implement-task-list

Implement roadmap tasks with full Parliament oversight - specialists handle implementation while grumpy reviewers ensure quality.

#### When to Use

- Implementing a scoped roadmap item
- When you want thorough, reviewed implementation
- Ensuring previous work is not broken
- When quality matters more than speed

#### Syntax

```
/implement-task-list [item-name]
```

If `item-name` is omitted, shows available items and asks you to choose.

#### Example Usage

```
/implement-task-list user-authentication
```

Implement the user-authentication feature with full council review.

```
/implement-task-list
```

Interactive selection from available items.

#### How It Works

This command uses **senior-council** orchestration, meaning every task goes through the full Parliament review cycle.

##### Phase 1: Safety & Planning

Before any implementation:
- Scans all `.project-files/roadmap/*/work_complete.md` files
- Builds a "Do Not Break" list of critical files and interfaces
- Reports potential overlaps with current tasks
- Loads `tasks.md` and `Spec.md` for context

##### Phase 2: Council Orchestration

For each task:

1. **Analyse Task** - Senior Council identifies relevant domains
2. **Summon Specialists** - Appropriate agents implement the work:

| Domain | Agent |
|--------|-------|
| Architecture | system-architect |
| Database | data-warlock |
| API | api-keeper |
| Security | security-knight |
| Performance | backend-goblin |
| Tests | test-prophet |
| UI/UX | ui-ux-guru |
| Docs | doc-bard |
| Dependencies | package-wizard |
| Resilience | resilience-tamer |
| CI/CD | pipeline-engineer |

3. **Grumpy Review** - ALL reviewers scrutinise the output:
   - grumpy-code-reviewer
   - grumpy-standards-enforcer
   - grumpy-architecture-skeptic
   - grumpy-maintainability-curmudgeon
   - grumpy-security-nag
   - grumpy-performance-troll

4. **Iterate** - Address objections, re-route to specialists until approved
5. **Mark Complete** - Update tasks.md after grumpy approval

##### Phase 3: Documentation

Creates `work_complete.md` containing:
- Summary of accomplishments
- All files modified or created
- Agents consulted and review rounds
- Decisions made with trade-offs
- Follow-up items identified

#### Safety Rules

1. Always perform safety check first
2. Never skip grumpy review for implementation tasks
3. Document all trade-offs when grumps disagree
4. Keep tasks atomic and reversible
5. Update tasks.md only after grumpy approval

#### Output Structure

Creates completion record:

```
.project-files/
  roadmap/
    <item-name>/
      work_complete.md   # Full documentation of completed work
```

#### Output for Each Task

1. **Task Summary** - What was implemented
2. **Agents Consulted** - Which specialists contributed
3. **Review Summary** - Grumpy objections raised and resolved
4. **Final Implementation** - Approved code/changes
5. **Trade-offs** - Any compromises made


---

## Review Commands

### /summon-council

The Senior Council orchestrates multiple specialist agents and grumpy reviewers to tackle complex tasks.

#### When to Use

- Designing new features or systems
- Refactoring complex code
- Making architectural decisions
- Tasks spanning multiple domains (backend, security, testing, etc.)
- When you want thorough, multi-perspective review

#### How It Works

1. **Task Analysis** - The council restates your goal and identifies relevant domains
2. **Agent Selection** - Appropriate specialists are chosen based on the task
3. **Specialist Work** - Each agent contributes from their domain expertise
4. **Grumpy Review** - All outputs go through the panel of critical reviewers
5. **Iteration** - Feedback is routed back to specialists until reviewers approve
6. **Synthesis** - Final solution is presented with trade-offs documented

#### Example Usage

```
/summon-council

Design an authentication system for our Laravel API. It needs to support:
- JWT tokens for mobile clients
- Session-based auth for the web app
- Role-based access control
- Rate limiting on login attempts
```

The council will engage:
- **security-knight** for authentication design and threat modelling
- **backend-goblin** for performance of auth checks
- **api-keeper** for token handling and API contracts
- **system-architect** for overall design
- **grumpy-security-nag** and others for critical review

#### Response Structure

The council returns:

1. **Agents Consulted** - Which specialists were involved and why
2. **Grump Review Summary** - Issues raised and fixes applied per iteration
3. **Final Solution** - The approved code, design, or recommendation
4. **Notes and Trade-offs** - Important context and decisions made

#### Conflict Resolution

When reviewers disagree, the council applies this priority order:

**security > correctness > maintainability > performance > convenience**

Example conflict:
- **grumpy-security-nag**: "Add input validation on all endpoints"
- **grumpy-performance-troll**: "Validation adds 5ms latency per request"
- **Resolution**: Security wins. Validation stays. Trade-off documented.

Out-of-scope recommendations (e.g., documentation requests on a hotfix) are logged to a "Deferred" section for future work rather than blocking approval.

#### Optional: Enable Logging

Add `scribe: on` to your request to save the deliberation process:

```
/summon-council
scribe: on

Refactor the payment processing module for better testability.
```

Logs are saved to `.parliament-of-chaos/{task-name}-{timestamp}.md`.

---

### /summon-grumpy-reviewer

A focused, critical code review from a senior developer perspective.

#### When to Use

- Quick code review before committing
- Validating a refactor
- Getting feedback on a PR
- Finding issues in existing code
- When you want honest, blunt feedback

#### How It Works

1. **Goal Clarification** - The reviewer restates what success looks like
2. **Review Angles** - Defines the perspectives for review (correctness, readability, etc.)
3. **Detailed Analysis** - Goes through code from each angle
4. **Structured Feedback** - Returns issues, recommendations, and a verdict

#### Example Usage

```
/summon-grumpy-reviewer

Review this service class:

class OrderService
{
    public function process($order)
    {
        $user = User::find($order->user_id);
        $items = OrderItem::where('order_id', $order->id)->get();

        foreach ($items as $item) {
            $product = Product::find($item->product_id);
            $item->price = $product->price;
            $item->save();
        }

        $order->total = $items->sum('price');
        $order->save();

        Mail::send(new OrderConfirmation($order));

        return $order;
    }
}
```

#### Response Structure

1. **Quality Summary** - Overall assessment (usually grumpy)
2. **Issues by Category** - Problems organised by type with severity ratings
   - Correctness and Bugs
   - Clarity and Readability
   - Structure and Architecture
   - Reusability and DRY
   - Standards and Conventions
   - Maintainability
   - Testability
3. **Refactor Suggestions** - Concrete improvements with code examples
4. **Definition of Done** - Checklist of required fixes before approval

#### Severity Levels

- **HIGH** - Must fix before merging
- **MEDIUM** - Should fix, technical debt if ignored
- **LOW** - Nice to have, minor improvements

---

## Operations Commands (v1.4.0)

### /parliament-optimize

Audit all 30 agent definitions and recommend effort/model settings based on role. Advisory only — reads but never modifies files.

#### When to Use

- After adding new agents to verify they follow standards
- Reviewing cost optimisation of the agent fleet
- Checking compliance with `.claude/rules/agent-standards.md`

#### Example Usage

```
/parliament-optimize
```

Returns a compliance report with tables showing each agent's frontmatter vs. expected values, plus cost optimisation estimates.

---

### /parliament-webhook

Configure HTTP webhook endpoints for Parliament event notifications.

#### When to Use

- Setting up Slack, Discord, or Teams notifications
- Configuring webhook for CI/CD integration
- Testing notification connectivity

#### Example Usage

```
/parliament-webhook setup
/parliament-webhook test
/parliament-webhook status
/parliament-webhook disable
```

#### Supported Events

All Parliament hook events (Notification, Stop, StopFailure, TaskCompleted, SubagentStart, PostCompact, InstructionsLoaded, TeammateIdle, PreToolUse, PostToolUse) can trigger webhook notifications.

---

### /parliament-loop

Set up recurring execution of Parliament commands on an interval using Claude Code's `/loop` command.

#### When to Use

- Monitoring roadmap progress during implementation sprints
- Running periodic code reviews during active development
- Continuous quality checks on changing code

#### Example Usage

```
/parliament-loop 5m /project-status
/parliament-loop 10m /parliament-review
/parliament-loop 15m /summon-grumpy-reviewer
```

Requires Claude Code v2.1.71+ for `/loop` support.

---

### /parliament-monitor

Manage background monitoring agents for continuous code oversight.

#### When to Use

- During active development sessions for ongoing review
- When you want security, quality, or test coverage monitoring
- For persistent oversight without manual invocation

#### Example Usage

```
/parliament-monitor start
/parliament-monitor start grumpy-security-nag grumpy-testing-tyrant
/parliament-monitor start --all
/parliament-monitor status
/parliament-monitor stop
```

**Default monitors**: grumpy-code-reviewer, grumpy-security-nag, grumpy-testing-tyrant.
**Full set**: All 9 grumpy reviewers.

All monitoring agents are read-only and use `effort: low` with `maxTurns: 5` for minimal overhead.

---

## Developer Workflow Commands (v1.5.0)

These commands automate repetitive software development tasks. They auto-detect your project's toolchain and run the right tools with zero configuration.

### /pre-commit-check

Run all CI checks locally before committing to guarantee your push will pass.

#### When to Use

- Before committing or pushing code
- As a final check after making changes
- When you want a single command to run everything

#### How It Works

1. **Detect Toolchain** — Reads CI config, package manager files, and tool configs to identify formatters, linters, type checkers, and test runners
2. **Run Checks** — Executes detected tools in order: secrets scan, format check, lint, type check, tests
3. **Report Results** — Pass/fail for each step with fix suggestions

#### Example Usage

```
/pre-commit-check                    # Run all detected checks
/pre-commit-check --fix              # Auto-fix what can be fixed
/pre-commit-check --skip tests       # Skip test execution
```

---

### /format-code

Detect and run the project's code formatter on changed files.

#### When to Use

- After writing code, before committing
- When the formatter wasn't run automatically
- To format specific files or the entire project

#### Example Usage

```
/format-code                         # Format changed files
/format-code --all                   # Format entire project
/format-code --check                 # Check only, don't modify
```

Supports: Prettier, Black, gofmt, rustfmt, clang-format, php-cs-fixer, and more.

---

### /lint-fix

Detect and run the project's linter(s) with auto-fix on changed files.

#### When to Use

- After writing code to catch and fix lint errors
- Before committing to ensure compliance
- To understand remaining lint issues that need manual fixes

#### Example Usage

```
/lint-fix                            # Lint and fix changed files
/lint-fix --all                      # Lint entire project
/lint-fix --no-fix                   # Report only, no auto-fix
```

Supports: ESLint, Ruff, Pylint, RuboCop, golangci-lint, Clippy, stylelint, and more. Handles multiple linters per project.

---

### /run-tests

Detect the test framework and run the suite with intelligent options.

#### When to Use

- After making changes to verify nothing broke
- Running only tests affected by your changes (with `--changed`)
- Understanding test failures (with `--explain`)
- Checking test coverage (with `--coverage`)

#### Example Usage

```
/run-tests                           # Run full test suite
/run-tests --changed                 # Only tests affected by git changes
/run-tests --changed --explain       # Changed tests with failure diagnosis
/run-tests --coverage                # Include coverage report
```

The `--explain` flag reads the failing test and source code to diagnose the issue and suggest a fix — far more useful than a raw stack trace.

---

### /security-scan

Unified security check combining dependency audit, secret detection, and vulnerability pattern scanning.

#### When to Use

- Before committing to check for accidentally committed secrets
- Periodically to audit dependency vulnerabilities
- After adding new dependencies
- Before releases for a comprehensive security check

#### Example Usage

```
/security-scan                       # Full scan (all checks)
/security-scan --secrets             # Secret detection only
/security-scan --deps                # Dependency audit only
/security-scan --changed             # Scan only changed files
```

Checks for: hardcoded API keys, tokens, passwords, private keys, dependency CVEs, SQL injection, XSS, command injection, and more.

---

### /clean-imports

Remove unused imports and organise import ordering across changed files.

#### When to Use

- After refactoring when imports become stale
- Before committing to clean up import statements
- To enforce consistent import ordering

#### Example Usage

```
/clean-imports                       # Clean imports in changed files
/clean-imports --all                 # Clean entire project
/clean-imports --check               # Report without modifying
```

Works across: JavaScript/TypeScript, Python, Go, Java, Rust. Respects project conventions (ESLint import/order, isort, goimports).

---

### /update-dependencies

Interactive dependency update with changelog review and test verification between each update.

#### When to Use

- Regular dependency maintenance
- Addressing known vulnerabilities
- Major version upgrades with breaking change review

#### Example Usage

```
/update-dependencies                 # Show outdated and update interactively
/update-dependencies --patch         # Auto-apply all patch updates
/update-dependencies --security      # Only security-related updates
/update-dependencies --major         # Walk through major updates with changelogs
```

Updates are applied one-by-one with tests run between each. Failed updates are automatically rolled back.

---

### /dead-code-sweep

Find unreachable code, unused exports, orphaned files, and dead CSS selectors.

#### When to Use

- After major refactors to find leftover code
- Periodic codebase hygiene
- Before releases to reduce bundle size
- When onboarding to understand what code is actually used

#### Example Usage

```
/dead-code-sweep                     # Report dead code (read-only)
/dead-code-sweep --apply             # Remove with diff preview and confirmation
/dead-code-sweep --scope src/utils/  # Scan specific directory
/dead-code-sweep --type exports      # Only unused exports
```

Report-only by default. The `--apply` flag shows a full diff and requires confirmation before removing anything.

---

### /update-docs

After completing work on an issue or feature, detect and update project documentation that has become stale.

#### When to Use

- After finishing a feature or bug fix
- Before creating a pull request
- When you've changed APIs, config, or CLI flags

#### Example Usage

```
/update-docs                         # Preview updates for current branch
/update-docs --apply                 # Apply updates after confirmation
/update-docs --scope commit          # Only most recent commit
/update-docs --create                # Also create docs for undocumented features
/update-docs --dry-run               # Report what's stale without generating updates
```

Delegates writing to doc-bard and validation to grumpy-documentation-pedant. Preview-only by default — no files modified without `--apply` and explicit confirmation.

---

## Tips for Best Results

### Be Specific About Context

The more context you provide, the better the output:

```
/plan-project

We're building a multi-tenant SaaS for project management.
Target users: Small teams of 5-20 people.
Current stack: Next.js, PostgreSQL, deployed on Vercel.
Constraint: Must launch MVP in 6 weeks.
```

### State Your Constraints

Mention what cannot change:

```
/summon-grumpy-reviewer

This code must remain backwards compatible with v2 API clients.
Review for security issues only.

[code here]
```

### Use the Right Tool

| Need | Use |
|------|-----|
| Starting a new project | `/plan-project` |
| Adding to existing roadmap | `/roadmap-add-item` |
| Breaking down a feature | `/roadmap-item-scope` |
| Implementing with safety | `/implement-task-list` |
| Checking progress | `/project-status` |
| Complex design decisions | `/summon-council` |
| Code review | `/summon-grumpy-reviewer` |
| Maximum scrutiny | `/parliament-review` |
| Technical debate | `/debate-topic` |
| Agent configuration audit | `/parliament-optimize` |
| Webhook setup | `/parliament-webhook` |
| Recurring monitoring | `/parliament-loop` |
| Background code oversight | `/parliament-monitor` |
| Onboarding to a codebase | `/onboard-codebase` |
| Ensure CI passes before push | `/pre-commit-check` |
| Format code | `/format-code` |
| Fix lint errors | `/lint-fix` |
| Run tests smartly | `/run-tests --changed` |
| Security check | `/security-scan` |
| Clean up imports | `/clean-imports` |
| Update packages safely | `/update-dependencies` |
| Find dead code | `/dead-code-sweep` |
| Update docs after changes | `/update-docs` |

### Iterate on Feedback

All commands support follow-up. After receiving feedback:

```
I've addressed the N+1 query issue. Here's the updated code:

[updated code]
```

The reviewer will re-evaluate.

---

## Available Agents

### Planning Agents

These agents drive the project planning and execution workflow:

| Agent | Expertise |
|-------|-----------|
| project-oracle | Project planning via structured Q&A, artifact generation |
| scope-weaver | Roadmap item scoping, spec writing, task decomposition |
| task-executor | Systematic task execution, progress tracking, safety checks |

### Specialist Agents

You can reference these directly when asking the council to focus on specific areas:

| Agent | Expertise |
|-------|-----------|
| api-keeper | API design, versioning, contracts |
| backend-goblin | Performance, caching, async patterns |
| config-curator | Environment config, secrets, feature flags |
| data-warlock | Database design, queries, migrations |
| dependency-detective | Vulnerability chains, license compliance |
| doc-bard | Documentation, comments, READMEs |
| migration-monk | Schema migrations, rollback strategies |
| observability-oracle | Logging, metrics, tracing, alerting |
| package-wizard | Dependencies, versions, compatibility |
| pipeline-engineer | CI/CD, deployment, infrastructure |
| refactor-ranger | Code smells, refactoring patterns |
| resilience-tamer | Error handling, retries, failure modes |
| security-knight | Auth, vulnerabilities, hardening |
| system-architect | High-level design, patterns, trade-offs |
| test-prophet | Testing strategy, coverage, TDD |
| ui-ux-guru | Accessibility, UX patterns, frontend |

### Grumpy Reviewers

| Reviewer | Focus |
|----------|-------|
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

## Project File Structure

When using planning commands, Parliament of Chaos creates and maintains this structure:

```
.project-files/
  project-outline.md         # Project overview and goals
  feature-implementation.md  # Feature lists (MVP and future)
  Roadmap.md                 # Phased delivery plan
  roadmap/
    <item-name>/
      Spec.md                # Detailed specification
      tasks.md               # Implementation checklist
      work_complete.md       # Completion documentation (when done)
```

### File Purposes

| File | Created By | Purpose |
|------|------------|---------|
| `project-outline.md` | `/plan-project` | High-level project definition |
| `feature-implementation.md` | `/plan-project` | Feature breakdown with priorities |
| `Roadmap.md` | `/plan-project` | Phased delivery plan with all items |
| `Spec.md` | `/roadmap-item-scope` | Detailed requirements for one item |
| `tasks.md` | `/roadmap-item-scope` | Actionable task list for one item |
| `work_complete.md` | `/implement-task-list` | Documentation of completed work |

---

## Safe Progress Assurance

The `/implement-task-list` command includes built-in safety mechanisms to prevent regressions:

### How It Works

1. **Pre-Flight Check** - Before implementation, scans all `work_complete.md` files
2. **Conflict Detection** - Identifies files, interfaces, and schemas owned by other features
3. **Do Not Break List** - Creates explicit list of things that must remain working
4. **Runtime Checks** - Verifies each task does not affect protected items
5. **Completion Records** - Documents everything for future safety checks

### What Gets Protected

- Files owned by completed features
- Public interfaces and their signatures
- Database schemas and constraints
- API endpoints and contracts
- Events and their payloads
- Configuration keys

### When Conflicts Arise

- **CRITICAL**: Implementation blocked until resolved
- **HIGH**: Warning displayed, requires acknowledgment
- **MEDIUM**: Noted in logs, proceed with caution
- **LOW**: Recorded for audit purposes

For more details, see [Safe Progress Assurance](./safe-progress-assurance.md).
