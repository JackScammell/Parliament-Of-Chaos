# Agent Frontmatter Standards

All Parliament of Chaos agents must include standardised frontmatter fields. This ensures consistent behaviour, cost optimisation, and proper resource allocation across the 33-agent fleet (2 orchestrators, 16 specialists, 12 grumpy reviewers, 2 planning agents, 1 utility agent).

> **Enforced by The Gate (v1.26.0)**: the tables in this file are machine-checked by
> `scripts/ci/conformance.py` in CI. Any change to a table here must update that script's
> constants in the same commit; this file remains authoritative — if the two disagree, fix
> the script. (Mirrors the `commands/manifest.yaml` ↔ `/parliament-doctor` pattern.)

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
| Grumpy reviewers | `[Edit, Write, NotebookEdit, Bash, Task, Agent, SendMessage]` | Read-only: critique only, never modify code, never spawn or laterally message |
| system-architect | `[Edit, Write, NotebookEdit, Bash, Task, Agent, SendMessage]` | Advisory: designs architecture, does not implement, does not spawn or message |
| All other specialists & planning agents | `[Task, Agent, SendMessage]` | Full tool access for implementation work, but only orchestrators spawn or coordinate |
| task-executor | `[Task, Agent, SendMessage]` + explicit `tools:` whitelist (`Read, Write, Edit`, native task tools) | Utility under senior-council; whitelist plus denial is belt-and-braces |
| Orchestrators (senior-council, deliberation-conductor) | None (whitelist via `tools:`) | The only agents permitted to spawn — enforced structurally, not just by `governance.md` prose |

> **Why `Task`, `Agent`, and `SendMessage` are denied fleet-wide (v1.24.0)**: upstream Claude
> Code re-enabled nested subagent spawning **by default** (depth 3) in v2.1.219, so the harness
> default no longer backs `governance.md`'s "only orchestrators spawn" rule. Denying the spawn
> primitive on every non-orchestrator turns that rule back into a structural guarantee — the
> same mechanism that enforces read-only on reviewers. **Both spawn-tool names are denied**
> (`Task` — the historic name this plugin's own `tools:` lists use — and `Agent`, the name
> newer harnesses surface) because a denial keyed to a stale name is a no-op. `SendMessage` is
> denied for the same reason the spawn ban exists: a lateral channel between fanned-out members
> bypasses orchestrator tallying, and messaging an orchestrator-context agent is spawn-by-proxy.
> Without these, a nested spawn or lateral message would corrupt `/parliament-metrics`
> per-member attribution and the B4 circuit-breaker's member identity model.
>
> **Known residual channel (documented, not denied)**: the `Skill` tool can invoke
> `context: fork` commands, which create a forked execution context outside `disallowedTools`'
> reach. `Skill` is *not* denied fleet-wide because specialists legitimately use non-forking
> skills; the guard here is `governance.md`'s delegation rule plus the fact that Parliament's
> fork commands are orchestrator entry points whose first act is top-level coordination — a
> nested fork surfaces immediately in `/parliament-metrics` attribution. Users wanting a hard
> cap can set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` (guide-don't-ship).

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
> on **Sonnet 5** — sonnet keeps `effort` valid while remaining materially cheaper per token
> than the inherit-tier model (consult current Claude API pricing for exact figures; absolute
> prices are deliberately not recorded here because they drift). The deviation is **reversible in one frontmatter line**, and
> review quality under the downgrade is to be measured after the fact via
> `/parliament-metrics --by-effort`. `/parliament-optimize` flags any reviewer still on
> `inherit` as a downgrade candidate, respecting the floor exclusion.

## Isolation

| Field | Value | Agents | Purpose |
|-------|-------|--------|---------|
| `isolation: worktree` | Present | Implementation specialists | Work in isolated git branches without conflicts |
| Not present | — | Read-only agents, orchestrators | No isolation needed for analysis/coordination |

> **Worktree branching baseline — data-loss correction (supersedes the v2.1.128 note)**: A previous version of this note told contributors to "treat v2.1.128 as the minimum safe version" for workflows that spawn `isolation: worktree` specialists from a local feature branch with unpushed commits. **That guidance is no longer sufficient and acting on it risks silently losing unpushed local commits.** History: on Claude Code < v2.1.128, `EnterWorktree` branched from the remote tracking head, so unpushed local commits could be dropped; v2.1.128 changed it to branch from local HEAD. However, as of **v2.1.133** the worktree base is governed by the `worktree.baseRef` setting, whose default is `fresh` (origin-based). On v2.1.133+ with the default in effect, a worktree-isolated specialist spawned from a local feature branch with unpushed work branches from `origin` again and that work is not visible in the worktree. **The safe configuration is Claude Code ≥ v2.1.133 _with_ an explicit `worktree.baseRef: "head"` setting** — the version floor alone is not enough. Parliament does **not** ship a `worktree.baseRef` setting (it ships no settings file at all as of v1.25.0): settings/permission policy is the user's responsibility (no-policy stance, reaffirmed in the v1.14.0 audit). This note guides the user to set `worktree.baseRef: "head"` themselves before relying on worktree-isolated specialists with unpushed local work; it does not prescribe it.

## Background Execution

| Field | Agents | Purpose |
|-------|--------|---------|
| `background: true` | Grumpy reviewers | Can run as background review tasks |

> **Parliament's invariants (documented explicitly because upstream defaults keep flipping)**:
> Parliament pins the behaviour it depends on rather than tracking upstream defaults:
>
> 1. **Interactive commands stay foreground.** All twelve `context: fork` commands set `background: false` explicitly (since v1.22.0) — a forked orchestrator that silently backgrounded would break the round-by-round review UX (`governance.md`: "Present genuine trade-offs to user"). This holds regardless of what the harness's background default is.
> 2. **One spawn level.** Only `senior-council` and `deliberation-conductor` orchestrate; every non-orchestrator agent carries `Task`, `Agent`, and `SendMessage` in `disallowedTools` (structural enforcement, since v1.24.0) in addition to the `governance.md` prohibition. This matters because **nested spawning is no longer disabled by default upstream** (as of v2.1.219 the harness default is nesting-on, depth 3) — the harness default is not a guard any more; Parliament's own denial is.
> 3. **No shipped caps.** Consistent with the no-policy stance, Parliament ships none of the `CLAUDE_CODE_MAX_*` env vars. Users who want defence-in-depth on top of Parliament's structural denial can set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` themselves (same guide-don't-prescribe precedent as `worktree.baseRef`).
>
> Upstream lineage, for the record (consult the Claude Code changelog for current behaviour — these defaults have already flipped more than once):
>
> | Version | Change |
> |---------|--------|
> | v2.1.198 | Subagents background-by-default; `Task` `mode` param deprecated |
> | v2.1.212 | Per-session spawn cap added (default 200) |
> | v2.1.217 | `context: fork` skills background-by-default; `background: false` opt-out |
> | v2.1.218 | Nested spawning disabled by default; concurrency cap 20 |
> | v2.1.219+ | Nested spawning **re-enabled** by default (depth 3); session cap removed |

## Council Fan-Out and Hang-Recovery

The full council fan-out policy — dispatch loop, the security-critical liveness floor, the
per-member terminal-state detection table, batching, and graceful degradation — lives in its single source,
`.claude/rules/fan-out-policy.md`. Two facts about it belong in the frontmatter standards:

> **Dispatch is detached; completion notifications are the primitive**: subagent dispatch is
> background-by-default (upstream v2.1.198+) — a `Task(...)` call returns immediately and the
> harness re-invokes the orchestrator with a notification as each member finishes. The fan-out
> loop is therefore **reconcile-on-notification** (`.claude/rules/fan-out-policy.md`): a member
> with a live task is *Working*, silence is not a signal, and the orchestrator must never
> substitute its own review for a live fan-out. Claude Code still offers **no** per-subagent
> wall-clock timeout and **no** auto-retry primitive — no frontmatter field, no settings knob,
> no harness default will time out or retry a hung member for you. Hang-recovery is the
> out-of-band `Monitor` watchdog (B4) in `fan-out-policy.md`, which tails `activity.jsonl`
> alongside the session and opens a per-member circuit breaker. Do not assume a hung member
> will be reaped automatically; nothing reaps it.

> **Prompt-standard — state assumptions, do not ask (B5); end with an explicit verdict (B6)**:
> Council members dispatched into a detached fan-out must **state their assumptions and
> proceed**; they must **never** ask clarifying questions. In a fan-out context a member blocked
> waiting on input is indistinguishable from a hung member and cannot be recovered by the
> orchestrator. Every member must also **end its run with an explicit verdict** — `APPROVE`,
> `REJECT`, or `NO-FINDINGS` — because the reconcile loop treats a completed task without a
> verdict as Non-reporting; silence is never a pass, and availability pings are not verdicts.
> These are standing prompt-authoring standards for every agent that can be fanned out under
> the council. See `.claude/rules/fan-out-policy.md` (B5, B6).

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

Parliament ships **no `settings.json` at all** (the root one was removed in v1.25.0 — Claude
Code ignores a plugin-root `settings.json` for everything except `agent`/`subagentStatusLine`
keys, so its hooks block had never been registered). Hooks are **auto-loaded from `hooks/hooks.json`** (the conventional path; do NOT also
reference it from `plugin.json`'s `hooks` field — that double-registers it and the plugin
fails to load, the v1.25.0→v1.25.1 hotfix). It contains hook events **only** — no
`permissions.allow`/`permissions.deny`, no env vars. Permission policy is the user's
responsibility, not the plugin's. This decision was reaffirmed in the v1.14.0 audit triggered
by Claude Code v2.1.113.

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
disallowedTools:
  - Task
  - Agent
  - SendMessage
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
  - Task
  - Agent
  - SendMessage
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
  - Task
  - Agent
  - SendMessage
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
initialPrompt: >-
  First-turn prompt that starts the interview/scoping workflow (see Initial Prompts)
disallowedTools:
  - Task
  - Agent
  - SendMessage
```
