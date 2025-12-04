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

Systematically execute all tasks for a roadmap item with safety checks.

#### When to Use

- Implementing a scoped roadmap item
- When you want tracked, methodical progress
- Ensuring previous work is not broken during implementation
- When you need clear documentation of what was done

#### Syntax

```
/implement-task-list [item-name]
```

If `item-name` is omitted, shows available items and asks you to choose.

#### Example Usage

```
/implement-task-list user-authentication
```

Implement the user-authentication feature.

```
/implement-task-list
```

Interactive selection from available items.

#### How It Works

##### Step 1: Safety Check (Mandatory)

Before any implementation:
- Scans all `.project-files/roadmap/*/work_complete.md` files
- Builds a "Do Not Break" list of critical files and interfaces
- Reports potential overlaps with current tasks
- Identifies APIs and data structures that must remain compatible

##### Step 2: Task Loading

- Reads `tasks.md` for the target item
- Reads `Spec.md` for full context
- Plans execution order based on dependencies

##### Step 3: Task Execution

For each uncompleted task:
1. Announces what is about to happen
2. Checks for "Do Not Break" conflicts
3. Executes the implementation
4. Verifies completion
5. Marks task as done in tasks.md
6. Documents what changed

##### Step 4: Completion Documentation

Creates `work_complete.md` containing:
- Summary of accomplishments
- All files modified or created
- Decisions made and rationale
- Integration points established
- Regression checks performed
- Follow-up items identified

#### Specialist Delegation

The task-executor may delegate specialized work to other agents:

| Task Type | Delegated To |
|-----------|--------------|
| Architecture decisions | system-architect |
| Database changes | data-warlock |
| API design | api-keeper |
| Security concerns | security-knight |
| Performance work | backend-goblin |
| Test creation | test-prophet |
| Documentation | doc-bard |

#### Safety Rules

1. Always perform the safety check first
2. Never skip documenting completed work
3. Stop and ask if potential regressions detected
4. Keep tasks atomic and reversible
5. Update tasks.md after each task completion

#### Output Structure

Creates completion record:

```
.project-files/
  roadmap/
    <item-name>/
      work_complete.md   # Full documentation of completed work
```


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
| backend-goblin | Performance, caching, async patterns |
| system-architect | High-level design, patterns, trade-offs |
| security-knight | Auth, vulnerabilities, hardening |
| data-warlock | Database design, queries, migrations |
| api-keeper | API design, versioning, contracts |
| test-prophet | Testing strategy, coverage, TDD |
| ui-ux-guru | Accessibility, UX patterns, frontend |
| pipeline-engineer | CI/CD, deployment, infrastructure |
| doc-bard | Documentation, comments, READMEs |
| package-wizard | Dependencies, versions, compatibility |
| resilience-tamer | Error handling, retries, failure modes |

### Grumpy Reviewers

| Reviewer | Focus |
|----------|-------|
| grumpy-code-reviewer | Overall code quality |
| grumpy-standards-enforcer | Coding standards compliance |
| grumpy-architecture-skeptic | Architectural decisions |
| grumpy-maintainability-curmudgeon | Long-term maintenance burden |
| grumpy-security-nag | Security oversights |
| grumpy-performance-troll | Performance issues |

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
