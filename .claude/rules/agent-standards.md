# Agent Frontmatter Standards

All Parliament of Chaos agents must include standardised frontmatter fields. This ensures consistent behaviour, cost optimisation, and proper resource allocation across the 33-agent fleet (2 orchestrators, 16 specialists, 12 grumpy reviewers, 2 planning agents, 1 utility agent).

## Required Fields

Every agent must include:
- `name` — Unique identifier (kebab-case)
- `description` — One-line summary of the agent's role
- `model` — Model selection (`inherit` uses the parent session's model)
- `color` — Visual identifier for UI display
- `permissionMode` — Permission level (`default` for most agents)
- `effort` — Reasoning effort tier (see below)
- `maxTurns` — Maximum conversation turns before auto-stop

## Effort Tiers

Effort levels control reasoning depth and token cost. Assign based on agent role:

| Tier | Effort | Agents | Rationale |
|------|--------|--------|-----------|
| **Reserved** | `effort: xhigh` | _(none currently)_ | Opus 4.7 tier sitting between `high` and `max` (Claude Code v2.1.111). Reserved for future deliberation-conductor deep-mode runs if measurements justify the extra cost. Do not adopt without before/after benchmarks. |
| **High** | `effort: high` | Orchestrators (senior-council, deliberation-conductor) | Complex multi-agent coordination requiring deep reasoning |
| **Medium** | `effort: medium` | Specialists (16), Planning agents (2), and task-executor | Domain analysis, implementation, and scoping work |
| **Low** | `effort: low` | Grumpy reviewers (12) | Read-only critique with focused, concise output |

> **Note**: As of Claude Code v2.1.94 the global default `effort` is `high` (previously `medium`). Parliament sets `effort` explicitly on every agent, so this default never applies — but new contributors reading upstream docs should be aware the implicit fallback changed.

## maxTurns Guidelines

| Role | maxTurns | Rationale |
|------|----------|-----------|
| Orchestrators | 30 | Coordinate multiple specialists and reviewers across iterations |
| Planning agents | 20 | Interactive Q&A and scoping require extended dialogue |
| task-executor | 20 | Task-mechanics utility under senior-council; task loading + progress tracking spans many small turns |
| Specialists | 15 | Focused domain analysis and implementation |
| Grumpy reviewers | 5 | Concise critique: summary, issues, recommendations, verdict |

## Memory Scopes

| Scope | Agents | Purpose |
|-------|--------|---------|
| `memory: project` | Orchestrators, specialists, planning agents, task-executor | Accumulate project-specific knowledge across sessions |
| `memory: user` | Grumpy reviewers | Accumulate review preferences and patterns across projects |

## Tool Restrictions

| Role | disallowedTools | Rationale |
|------|----------------|-----------|
| Grumpy reviewers | `[Edit, Write, NotebookEdit, Bash]` | Read-only: critique only, never modify code |
| system-architect | `[Edit, Write, NotebookEdit, Bash]` | Advisory: designs architecture, does not implement |
| All other specialists | None | Full tool access for implementation work |

> **MCP inheritance (v2.1.101)**: Subagents now inherit MCP tools from the parent session automatically. Parliament specialists no longer need to re-declare MCP servers; any MCP tool available to the user is available to spawned agents unless explicitly listed in `disallowedTools`. Sandboxed subagents also now resolve worktree paths correctly.

## Model Selection

The fleet default is `model: inherit` (subagents run on the parent session's model). Two
deliberate deviations apply.

| Tier | Agents | `model` | Rationale |
|------|--------|---------|-----------|
| **Advisory reviewers** | grumpy-performance-troll, grumpy-accessibility-auditor, grumpy-documentation-pedant, grumpy-i18n-nitpicker, grumpy-budget-hawk | `sonnet` | Measured cost deviation — see note below |
| **Floor reviewers** | grumpy-security-nag, grumpy-code-reviewer | `inherit` | Security/correctness floor stays on the strongest available model |
| **All other agents** | remaining reviewers, specialists, orchestrators, planning | `inherit` | Default — no deviation |

> **Advisory-tier `sonnet` pin (measured cost deviation)**: The five **advisory** grumpy
> reviewers (performance, accessibility, documentation, i18n, budget) are pinned to
> `model: sonnet` rather than the `model: inherit` default. This is a deliberate, measured cost
> deviation, not a standards violation. The **floor** reviewers (`grumpy-security-nag`,
> `grumpy-code-reviewer`) and every other reviewer stay `inherit` so security and correctness
> keep the strongest model. `sonnet` is chosen over `haiku` specifically because these reviewers
> carry `effort: low`, and the `effort` parameter **errors on Haiku 4.5** but is fully supported
> on **Sonnet 5** — sonnet keeps `effort` valid while still cutting per-token cost (Opus
> $5/$25 → Sonnet $3/$15 per Mtok). The deviation is **reversible in one frontmatter line**, and
> review quality under the downgrade is to be measured after the fact via
> `/parliament-metrics --by-effort`. `/parliament-optimize` flags any reviewer still on
> `inherit` as a downgrade candidate, respecting the floor exclusion.

## Isolation

| Field | Value | Agents | Purpose |
|-------|-------|--------|---------|
| `isolation: worktree` | Present | Implementation specialists | Work in isolated git branches without conflicts |
| Not present | — | Read-only agents, orchestrators | No isolation needed for analysis/coordination |

> **Worktree branching baseline — data-loss correction (supersedes the v2.1.128 note)**: A previous version of this note told contributors to "treat v2.1.128 as the minimum safe version" for workflows that spawn `isolation: worktree` specialists from a local feature branch with unpushed commits. **That guidance is no longer sufficient and acting on it risks silently losing unpushed local commits.** History: on Claude Code < v2.1.128, `EnterWorktree` branched from the remote tracking head, so unpushed local commits could be dropped; v2.1.128 changed it to branch from local HEAD. However, as of **v2.1.133** the worktree base is governed by the `worktree.baseRef` setting, whose default is `fresh` (origin-based). On v2.1.133+ with the default in effect, a worktree-isolated specialist spawned from a local feature branch with unpushed work branches from `origin` again and that work is not visible in the worktree. **The safe configuration is Claude Code ≥ v2.1.133 _with_ an explicit `worktree.baseRef: "head"` setting** — the version floor alone is not enough. Parliament does **not** ship `worktree.baseRef` in `settings.json`: settings/permission policy is the user's responsibility (no-policy stance, reaffirmed in the v1.14.0 audit). This note guides the user to set `worktree.baseRef: "head"` themselves before relying on worktree-isolated specialists with unpushed local work; it does not prescribe it.

## Background Execution

| Field | Agents | Purpose |
|-------|--------|---------|
| `background: true` | Grumpy reviewers | Can run as background review tasks |

> **Background-by-default baseline & the `background: false` opt-out (v2.1.198 → v2.1.218)**: Upstream Claude Code moved subagents and forked skills to *background-by-default* over several releases, and this supersedes any earlier note that described subagents as running foreground or nesting "5 levels deep" by default. The relevant history:
>
> - **v2.1.198** — subagents run in the **background by default** (the `Task` tool's `mode` parameter is now deprecated/ignored). Claude keeps working while the subagent runs and is notified on completion.
> - **v2.1.212** — per-session spawn cap `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` (default **200**); `/clear` resets the budget.
> - **v2.1.217** — skills / slash commands with `context: fork` also **background by default**. The documented opt-out is `background: false` in the command's frontmatter (booleans now also accept `no`/`off`/`0`).
> - **v2.1.218** — subagents **no longer spawn nested subagents by default** (gated behind `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, default disabled), plus a concurrency cap `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (default **20**).
>
> **Parliament impact.** Parliament ships **twelve** `context: fork` commands and, as of v1.22.0, every one sets `background: false` to preserve the interactive contract the plugin is built on — a forked orchestrator that silently backgrounded would break the round-by-round review UX (`governance.md`: "Present genuine trade-offs to user"). The nesting block in v2.1.218 is **inert for Parliament**: `governance.md` already forbids specialists and reviewers from spawning sub-agents (only `senior-council` and `deliberation-conductor` orchestrate), and those orchestrators run **top-level** via slash commands, one spawn level deep — well inside the default concurrency cap. Consistent with the standing no-policy stance, Parliament does **not** ship any of these `CLAUDE_CODE_MAX_*` env vars in `settings.json`; the defaults are safe for the fleet as designed. A future release that fanned specialists out beyond one nesting level would need to set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` explicitly.

## Council Fan-Out and Hang-Recovery

The full council fan-out policy — dispatch loop, the security-critical liveness floor, the
post-return detection table, batching, and graceful degradation — lives in its single source,
`.claude/rules/fan-out-policy.md`. Two facts about it belong in the frontmatter standards:

> **No wall-clock timeout, no auto-retry primitive**: Claude Code offers **no** per-subagent
> wall-clock timeout and **no** auto-retry primitive. There is no frontmatter field, no
> `settings.json` knob, and no harness default that will time out or retry a hung council
> member for you. Hang-recovery is therefore **genuine engineering**, not configuration — it is
> the out-of-band `Monitor` watchdog (B4) documented in `.claude/rules/fan-out-policy.md`, which
> tails `activity.jsonl` alongside the session and opens a per-member circuit breaker. Do not
> assume a hung member will be reaped automatically; nothing reaps it.

> **Prompt-standard — state assumptions, do not ask (B5)**: Council members dispatched into a
> detached fan-out must **state their assumptions and proceed**; they must **never** ask
> clarifying questions. In a fan-out context a member blocked waiting on input is
> indistinguishable from a hung member and cannot be recovered by the orchestrator. This is a
> standing prompt-authoring standard for every agent that can be fanned out under the council.
> See `.claude/rules/fan-out-policy.md`.

## Initial Prompts

| Field | Agents | Purpose |
|-------|--------|---------|
| `initialPrompt` | Planning agents (project-oracle, scope-weaver) | Auto-submit a first turn to start the interview/scoping workflow. Only for agents that drive conversation without needing input first. Not for orchestrators that react to a topic. |

## Effort for Slash Commands

Skills and slash commands also support `effort` frontmatter (since Claude Code v2.1.80). Assign based on command complexity:

| Tier | Effort | Commands | Rationale |
|------|--------|----------|-----------|
| **High** | `effort: high` | summon-council, debate-topic, parliament-review, implement-task-list | Multi-agent orchestration spawning multiple specialists and reviewers |
| **Medium** | `effort: medium` | plan-project, changelog-review, security-scan, summon-specialist, etc. (17 total) | Single-domain analysis, planning, or scoped implementation work |
| **Low** | `effort: low` | list-agents, version, readme, format-code, run-tests, etc. (13 total) | Simple display, single-tool execution, or delegating to an external tool |

### Reading session effort at runtime (`${CLAUDE_EFFORT}`)

As of Claude Code v2.1.120, every skill / slash command receives the *current session*
effort tier via the `${CLAUDE_EFFORT}` environment variable. Parliament commands use it
as the default baseline for cost projections and effort-aware reporting:

- `/cost-report estimate` — uses `${CLAUDE_EFFORT}` as the third-priority source (after the explicit `--effort` flag and the target command's frontmatter `effort:`).
- `/parliament-metrics --by-effort` — partitions cost / latency rows by effort tier; events without an attribute fall back to `${CLAUDE_EFFORT}` for newly emitted records.

Authors of new commands that vary in token cost by depth should prefer reading
`${CLAUDE_EFFORT}` directly over re-introducing `--mode fast/consensus/deep` plumbing.
The `--mode` flag remains the right surface for *deliberation depth* (round count,
voting rules) on `/debate-topic`, `/decision-review`, and `/changelog-review`; it is
orthogonal to `${CLAUDE_EFFORT}`, which controls reasoning effort per turn.

## Permissions

Parliament's `settings.json` deliberately ships **no** `permissions.allow` or `permissions.deny`
rules. The plugin only configures hooks; permission policy is the user's responsibility, not the
plugin's. This decision was reaffirmed in the v1.14.0 audit triggered by Claude Code v2.1.113.

### Claude Code v2.1.113 hardening — verified safe

Three behaviour changes in v2.1.113 narrow how Bash allow/deny rules match. Parliament's stance
on each:

| Change | Parliament impact | Verdict |
|--------|-------------------|---------|
| `Bash(find:*)` allow rules no longer auto-approve `find -exec` and `find -delete` | Parliament has no `Bash(find:*)` allow rule | No change required |
| Deny rules now match commands wrapped in `env`/`sudo`/`watch`/`ionice`/`setsid` | Parliament has no `Bash(...)` deny rules | No change required (strict tightening — any user-defined deny rule is now harder to bypass, which is desired) |
| macOS `/private/{etc,var,tmp,home}` paths treated as dangerous removal targets | Parliament hooks never write to `/private/...` | No change required |

If a future Parliament release introduces permission rules, the new semantics must be assumed.
In particular: **never** rely on the pre-v2.1.113 behaviour where a wrapper command like
`sudo rm -rf /` could bypass a deny rule on `Bash(rm:*)`.

### Hook-script invocation

Hook scripts are invoked by Claude Code directly (not via `Bash(...)` permission rules), so they
are unaffected by allow/deny narrowing. The relevant guard for hooks is `/env-doctor`, which
verifies hook-script location, executable bit, shebang, and `${CLAUDE_PLUGIN_DATA}` fallback.

## Plugin State Storage

Parliament maintains two distinct storage locations:

| Location | Contents | Lifecycle |
|----------|----------|-----------|
| `${CLAUDE_PLUGIN_DATA}/` | Plugin telemetry, logs, analytics, review state | Survives plugin updates, owned by the plugin |
| `.project-files/` | User-facing project artifacts (roadmaps, specs, outlines) | Owned by the user, lives with the project |

These are separate concerns. Never mix machine-generated telemetry with user-curated documents.

> **`claude project purge` interaction (v2.1.126+)**: `claude project purge` clears Claude-managed plugin state, which includes `${CLAUDE_PLUGIN_DATA}/chaos-parliament-of-chaos/` (telemetry — plugin-owned and disposable, safe to wipe). `.project-files/` lives in the user's project tree and is not part of Claude-managed state, so it is not touched by current `purge` behaviour. Parliament's two-location split reflects this intended separation; preservation of `.project-files/` is a property of `purge`'s scope, not a Parliament-side guarantee.

Hook scripts use a shared helper (`src/hooks/_common.sh`) that resolves the data directory with a fallback for older Claude Code versions where `CLAUDE_PLUGIN_DATA` is not set:

```bash
HOOK_DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOOK_PROJECT_DIR/.project-files/.telemetry}"
```

The fallback writes to `.project-files/.telemetry/` (not the `.project-files/` root) to maintain separation from user planning data.

## Frontmatter Template

### Orchestrator
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: high
maxTurns: 30
tools:
  - Task(agent-name)
```

### Specialist (with implementation)
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: medium
maxTurns: 15
isolation: worktree
```

### Specialist (read-only advisory)
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: medium
maxTurns: 15
disallowedTools:
  - Edit
  - Write
  - NotebookEdit
  - Bash
```

### Grumpy Reviewer
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: user
background: true
effort: low
maxTurns: 5
disallowedTools:
  - Edit
  - Write
  - NotebookEdit
  - Bash
```

### Planning Agent
```yaml
name: agent-name
description: Brief role description
model: inherit
color: [color]
permissionMode: default
memory: project
effort: medium
maxTurns: 20
```
