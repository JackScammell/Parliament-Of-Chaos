---
description: Pre-flight and post-flight cost visibility with dry-run, soft caps, and expensive-command warnings
effort: medium
argument-hint: "[estimate <command>] [budget] [session] [--effort low|medium|high|xhigh|max]"
---

# Cost Report

Cost visibility and budget guardrails for Parliament. Answers two questions:

1. *Before running an expensive command* — what is this going to cost? (dry-run)
2. *After the fact* — what did my last N runs cost and am I within budget? (post-flight)

Addresses the Tier 3 gap flagged by `grumpy-budget-hawk` in the toolset-gaps debate: `/parliament-review` spawns 9 reviewers with no floor, dry-run, or soft cap.

## Usage

```
/cost-report
/cost-report estimate <command-with-args> [--effort low|medium|high|xhigh|max]
/cost-report last [--n <count>]
/cost-report budget set|show|clear [--scope session|daily|monthly] [--tokens <n>] [--usd <amount>]
```

**Examples**:
```
/cost-report                                           # Summary of last 7 days
/cost-report estimate /parliament-review               # Dry-run: estimated tokens and $
/cost-report estimate /debate-topic "migrate to X" --mode deep
/cost-report estimate /parliament-review --effort high # Override session effort for the estimate
/cost-report last --n 5                                # Last 5 runs detailed
/cost-report budget set --scope daily --usd 10         # Set a soft cap
/cost-report budget show
```

## Effort awareness (Claude Code v2.1.120+)

Since Claude Code v2.1.120, skills receive the current session effort via the
`${CLAUDE_EFFORT}` environment variable. `/cost-report estimate` now reads it as the
default effort baseline so estimates reflect the session that the user is actually in:

| Resolution order | Source |
|------------------|--------|
| 1 | `--effort <level>` flag on the `estimate` invocation (explicit override) |
| 2 | `${CLAUDE_EFFORT}` from the running session (Claude Code v2.1.120+) |
| 3 | Target command's `effort:` frontmatter — reached **only** when `${CLAUDE_EFFORT}` is *absent* (pre-v2.1.120 harness) |
| 4 | `medium` — **only** when `${CLAUDE_EFFORT}` is absent *and* the target declares no `effort:` |

**Why the session outranks the target's frontmatter.** Every Parliament slash command carries an
explicit `effort:` (mandated by `.claude/rules/agent-standards.md`, enforced by conformance
check 3), so a frontmatter-first order would terminate at that step for *every* valid target —
making both the `${CLAUDE_EFFORT}` step and the `unknown` handling below structurally
unreachable. The session value is also the live dial the user just turned with `/effort`,
whereas frontmatter is a static authoring default; an estimator's job is to project *this* run
in *this* session. When the two disagree, use the session value and name the target's declared
level alongside it: `**Effort baseline**: low (source: ${CLAUDE_EFFORT}; target declares high)`.

Steps 3–4 are scoped strictly to an **absent** `${CLAUDE_EFFORT}`. If the variable is *present*
but carries a value not in the multiplier table below, report the effort baseline as `unknown`
(`**Effort baseline**: unknown (source: ${CLAUDE_EFFORT}=<value>; no multiplier — projection
suppressed)`) and omit the token/USD projection rather than silently assuming `medium` — and
rather than silently falling through to the target's frontmatter, which is the same defect
wearing a different source label. A fallback on an unrecognised (probably *higher*) tier
under-projects the run at exactly the moment cost visibility matters most; an absent estimate
beats a confidently wrong one. This matches `/parliament-metrics --by-effort`, which already has
an explicit `unknown` bucket. Budget and soft-cap panels still render; only the effort-scaled
projection is withheld.

The chosen value is reflected in the estimate output (`**Effort baseline**: high
(source: ${CLAUDE_EFFORT})`) so the user can see which level the projection used. No
plumbing or `--mode` re-flag is required for the common case where the user has already
selected an effort via `/effort` for the session.

Effort multipliers applied to the historical p50/p95 token bounds:

| Effort | Multiplier (vs `medium` baseline) |
|--------|-----------------------------------|
| `low`   | 0.55× |
| `medium`| 1.00× (baseline) |
| `high`  | 1.55× |
| `xhigh` | 2.10× (reserved tier — used only when an agent or command explicitly opts in; requires thinking enabled, and the harness errors when it is off, v2.1.243) |
| `max`   | 2.75× (heuristic, as with every row here — the highest documented tier in `.claude/rules/agent-standards.md`; reachable via `${CLAUDE_EFFORT}` on a session set to `max`) |

Multipliers are heuristic and refined as telemetry accumulates per effort level; they are
stored in `${CLAUDE_PLUGIN_DATA}/cost-rates.json` under `effort_multipliers` and override
the defaults above when present.

## Sub-commands

### `estimate <command-with-args>`

Dry-run a command without executing it. Walks the command's `Process` block to estimate:
- Which agents would be invoked
- Expected round count (for debates)
- Per-agent average token cost from `/agent-usage-stats --json`
- Upper and lower bounds based on historical variance
- The effort baseline used (see *Effort awareness* above)

Output:

```
# Cost Estimate

**Command**: /parliament-review
**Effort baseline**: high (source: ${CLAUDE_EFFORT})
**Estimated agents invoked**: 9 (all grumpy reviewers)
**Estimated tokens**: 590K–960K (p50: 720K)
**Estimated cost**: $2.66–$4.36 (p50: $3.25)

## Budget check
- Current daily budget: $10.00
- Spent today: $3.40 (34%)
- Projected after this run: $5.50 (55%) — OK

## Suggested alternatives (cheaper)
- /summon-grumpy-reviewer grumpy-code-reviewer    — est. $0.40
- /summon-council (curated reviewers)             — est. $0.90–$1.30

Proceed with /parliament-review? (confirmation required when estimate > soft-cap)
```

### `last [--n <count>]`

Show the actual cost of the last N commands from telemetry.

```
# Last 5 Runs

| When                 | Command              | Tokens | Cost  |
|----------------------|----------------------|--------|-------|
| 2026-04-17T09:12Z    | /debate-topic        | 680K   | $2.58 |
| 2026-04-17T08:05Z    | /summon-council      | 210K   | $0.78 |
| 2026-04-16T16:40Z    | /parliament-review   | 420K   | $1.60 |
| 2026-04-16T11:22Z    | /format-code         | 18K    | $0.08 |
| 2026-04-15T14:08Z    | /update-dependencies | 92K    | $0.35 |

Total: 1.42M tokens / $5.39
```

### `budget set|show|clear`

Soft-cap management. Budgets are advisory warnings, not hard stops (hard-stop enforcement would conflict with governance — security > convenience).

Config file: `${CLAUDE_PLUGIN_DATA}/budgets.json`

```json
{
  "session": { "tokens": 1000000, "usd": 5.00 },
  "daily":   { "tokens": 5000000, "usd": 20.00 },
  "monthly": { "tokens": 100000000, "usd": 500.00 }
}
```

### No sub-command

Default view is a seven-day cost report (equivalent to `/parliament-metrics --focus cost`).

## Soft-cap behaviour

When `/cost-report estimate` shows a projected run would exceed a soft cap:

| Cap exceeded by | Behaviour |
|-----------------|-----------|
| 0–25% over | Warning; run proceeds without confirmation |
| 25–100% over | Explicit confirmation required |
| >100% over | Explicit confirmation + suggestion to use a cheaper alternative |

The user always has the final word. Governance priority: convenience never trumps user choice — the command only warns, never blocks.

## Expensive-command registry

`/cost-report estimate` treats these as "expensive" by default and auto-warns when invoked without explicit confirmation:

- `/summon-council`
- `/parliament-review`
- `/debate-topic --mode deep`
- `/implement-task-list`
- `/changelog-review --full`

The registry is editable in `${CLAUDE_PLUGIN_DATA}/cost-rates.json` under `expensive_commands`.

## Fresh-install guard

Historical spend panels depend on `${CLAUDE_PLUGIN_DATA}/agent-logs/activity.jsonl` (or the `.project-files/.telemetry/` fallback). If it is absent or empty, report **"no telemetry recorded yet"** for those panels rather than fabricating figures; pre-flight estimates (which need no history) still work.

## Process

1. Parse sub-command.
2. For `estimate`:
   1. Resolve effort baseline using the four-step order documented under *Effort awareness*.
   2. Statically analyse the target command's `Process` block, look up historical per-agent cost.
   3. If the baseline resolved to a level in the multiplier table, apply that multiplier to the
      p50/p95 bounds. If it resolved to `unknown`, **skip this step** and suppress the
      token/USD projection entirely (see *Effort awareness*) — never substitute a multiplier.
   4. Compute soft-cap delta and render the baseline source for transparency (including the
      target's declared `effort:` when it differs from the session baseline).
3. For `last`: call `/telemetry-query --event TaskCompleted --since 7d --json`, sort, limit.
4. For `budget`: read/write `${CLAUDE_PLUGIN_DATA}/budgets.json`.
5. Render.

## Notes

- Estimates are heuristic; they use the p50/p95 from recent telemetry when available, and fall back to static defaults for commands with no history.
- Cost figures require `${CLAUDE_PLUGIN_DATA}/cost-rates.json`. If absent, tokens are shown but USD is `n/a`.
- **Every USD figure here is a Parliament-derived estimate, and two known biases push it away from what you are actually billed.** (a) Parliament reads only its own `cost-rates.json`; it does **not** read the upstream managed `modelPricing` configuration, so on a managed org the two diverge and Parliament's is the wrong one — and because the `budgets.json` soft caps are USD-denominated, a cost guardrail can fire (or fail to fire) on rates the user is not billed at. (b) The v2.1.239 US-only-inference **1.1× premium** is the same defect class: a second systematic bias baked into the same derived figure. Native `/cost` (and the org's billing surface) is authoritative; set `cost-rates.json` to the org's contracted rates if you rely on the USD column.
- **`subagentPromptCacheTtl` is a genuinely council-shaped lever** — a 9–18-member fan-out shares one large identical dispatch prefix, and the default 5-minute subagent cache TTL is shorter than a `/parliament-review` panel's span, so late-finishing members and every B2 re-dispatch miss the cache entirely. Two preconditions before it helps: it is gated to API-key / cloud-provider users, and an extended TTL raises the cache-**write** multiplier — so it is a **trade**, not a saving, and only pays off when reuse actually spans the window. Described, not prescribed: Parliament ships no settings file (standing no-policy stance, reaffirmed in the v1.14.0 audit); set it yourself if you measure a win.
- This command never edits the cost-rates file — use `config-curator` or hand-edit for rate changes.
- Budget caps are per-scope soft limits. A "hard cap" variant was rejected in the toolset-gaps debate — it would break governance (convenience cannot override security or correctness work).
- Pair with `/parliament-metrics --focus cost` for the retrospective dashboard view.
- For the plugin's own packaged-token footprint (commands/agents/skills shipped by the plugin, distinct from per-run usage), see `claude plugin details` — Claude Code v2.1.139+ reports a token projection there. Pointer only; `/cost-report` does not read or integrate that figure.
