---
description: Orchestrate specialists and grumpy reviewers for ad-hoc planning or implementation
effort: high
context: fork
background: false
agent: senior-council
argument-hint: "<task-description> [plan|implement]"
---

# Summon the Council

Two-mode orchestrator for ad-hoc multi-domain work that doesn't fit the roadmap state machine.

- `plan` mode — produce a structured plan/spec without editing code.
- `implement` mode — coordinate specialists and grumpy reviewers to ship working code.

## Mode selection

- Explicit: `/summon-council plan <topic>` or `/summon-council implement <topic>`.
- Implicit: if no mode is given, infer from the topic. **If inference is ambiguous, ask the user which mode they want before doing any work.** Never silently default.
- Pure review (no fix loop)? Stop and point the user at `/parliament-review`.

## When NOT to use

| Situation | Use this instead |
|---|---|
| Greenfield project planning Q&A | `/plan-project` |
| Adding or scoping a single roadmap item | `/roadmap-add-item`, `/roadmap-item-scope` |
| Implementing a roadmap item with a `tasks.md` | `/implement-task-list <item>` |
| Critique only, no fix loop | `/parliament-review` |
| Single-domain critique or fix | `/summon-grumpy-reviewer`, `/summon-specialist` |
| Open-ended question, no artifact wanted | `/ask-council <question>` |

## Process

### Step 1 — Inventory (both modes)

Before any specialist work, run a codebase inventory pass via the `Explore` agent so the council does not propose something the project already has.

1. Distil the topic into search terms (symbol names, file-name patterns, domain keywords).
2. Dispatch `Explore` to grep for related helpers, utilities, services, modules, and tests.
3. For any plausible match, capture path + a one-line summary of what it does and how many callers use it.

Output (always present, even if empty):

```
## Existing Capabilities Found
- <path> — <what it does>. <N callers / used by …>
- (or) None found for <term>.

## Reuse Decision
- EXTEND <path> with <new behaviour> — matches existing API shape.
- CREATE <new module> — no existing analogue, distinct concern.
```

**Default rule when in doubt: extend, don't create.** A specialist proposing a new file/helper/module must reference the inventory and justify why an existing capability cannot be extended.

### Step 2 — Mode-specific work

#### `plan` mode

1. **Clarify goal** — restate the task, define "good" and "done".
2. **Select planning specialists** — typically `system-architect`, `security-knight`, `data-warlock`, `api-keeper`, plus domain agents relevant to the topic. **Do not** use `project-oracle`, `scope-weaver`, or `task-executor` — they have their own driving commands.
3. **Specialist analysis** — each produces options + recommendation, referencing inventory findings.
4. **Plan-shaped review** — route the draft plan through a focused reviewer subset:
   - `grumpy-architecture-skeptic`
   - `grumpy-maintainability-curmudgeon`
   - `grumpy-security-nag`
   - `grumpy-performance-troll`
   - Add `grumpy-budget-hawk` if infra-heavy, `grumpy-privacy-paranoid` if PII-touching, `grumpy-testing-tyrant` if a test strategy is part of the plan.
5. **Iterate** — revise plan against reviewer feedback. Conflict priority: security > correctness > maintainability > performance > convenience.
6. **Write the plan** — save to `.project-files/plans/<slug>.md` (create the directory if missing). Filename slug is a kebab-case derivation of the topic.

Plan artifact structure:

```markdown
# <Topic>

## Goal
<one paragraph>

## Existing Capabilities Found
<from Step 1>

## Reuse Decision
<from Step 1>

## Options Considered
- Option A — pros / cons
- Option B — pros / cons

## Recommended Approach
<one paragraph + rationale>

## Risks & Trade-offs
<bulleted>

## Suggested Task Breakdown
1. …
2. …

## Open Questions
<bulleted, if any>
```

Return the plan path to the user. Do **not** edit code in `plan` mode.

#### `implement` mode

1. **Clarify goal** — restate the task, define "good" and "done".
2. **Select implementation specialists** from: `backend-goblin`, `ui-ux-guru`, `data-warlock`, `test-prophet`, `api-keeper`, `doc-bard`, `package-wizard`, `resilience-tamer`, `pipeline-engineer`, `migration-monk`, `dependency-detective`, `refactor-ranger`, `config-curator`, `observability-oracle`. Bring in `system-architect` / `security-knight` for advisory input as needed.
3. **Pre-flight cost gate (A4)** — before fanning out to specialists and reviewers, apply the existing `/cost-report estimate` soft-cap band as a **WARN/CONFIRM** gate. Advisory only, **never a hard block**: over the soft cap → warn and ask to proceed; no telemetry history → degrade to "estimate unavailable — proceed?". It is a **whole-run** static estimate (not a per-subset admission controller) and is **provisional** until post-change telemetry re-accumulates. Skip below a small-run size threshold so small runs don't pay the fixed overhead.
4. **Delegate work** — specialists analyse, design, and implement, referencing inventory findings (extend-don't-create default applies).
5. **Grumpy review** — run outputs through all 9 reviewers, fanning out per the reconcile-after-return policy loop in `.claude/rules/fan-out-policy.md` (concurrency-aware batching B1, graceful degradation with one re-dispatch B2, and the liveness floor):
   - grumpy-code-reviewer, grumpy-standards-enforcer, grumpy-architecture-skeptic
   - grumpy-maintainability-curmudgeon, grumpy-security-nag, grumpy-performance-troll
   - grumpy-accessibility-auditor, grumpy-documentation-pedant, grumpy-testing-tyrant
   - The security + correctness floor (`grumpy-security-nag`, `grumpy-code-reviewer`, plus `grumpy-privacy-paranoid` on PII) is never dropped; a non-reporting floor member forces an `INCOMPLETE` result rather than a survivor-synthesised approval.
6. **Iterate** — route complaints back to specialists until grumps accept. Conflict priority: security > correctness > maintainability > performance > convenience. Defer out-of-scope items.
7. **Synthesise** — final solution + Deferred section.

## Output

### `plan` mode
- Path to written plan artifact (`.project-files/plans/<slug>.md`)
- Inventory summary
- Recommended approach + key trade-offs
- Suggested next command (`/roadmap-add-item`, `/implement-task-list`, `/summon-council implement`, etc.)

### `implement` mode
- Summary of goal and approach
- Inventory summary
- Areas the council focused on
- Final solution (code + recommendations)
- Trade-offs, Deferred items, caveats

## Notes

- Parallel fan-out to specialists and reviewers is more reliable on Claude Code v2.1.128+, where a failing sibling tool call no longer cancels its parallel peers. How non-reporting members are detected and recovered (batching, one re-dispatch, liveness floor, `INCOMPLETE` on floor non-report) is single-sourced in `.claude/rules/fan-out-policy.md`.
- The inventory pass uses the `Explore` agent (read-only). It is fast and does not pollute the main context window.
