---
description: Pre-flight and post-flight cost visibility with dry-run, soft caps, and expensive-command warnings
effort: medium
---

# Cost Report

Cost visibility and budget guardrails for Parliament. Answers two questions:

1. *Before running an expensive command* — what is this going to cost? (dry-run)
2. *After the fact* — what did my last N runs cost and am I within budget? (post-flight)

Addresses the Tier 3 gap flagged by `grumpy-budget-hawk` in the toolset-gaps debate: `/parliament-review` spawns 9 reviewers with no floor, dry-run, or soft cap.

## Usage

```
/cost-report
/cost-report estimate <command-with-args>
/cost-report last [--n <count>]
/cost-report budget set|show|clear [--scope session|daily|monthly] [--tokens <n>] [--usd <amount>]
```

**Examples**:
```
/cost-report                                           # Summary of last 7 days
/cost-report estimate /parliament-review               # Dry-run: estimated tokens and $
/cost-report estimate /debate-topic "migrate to X" --mode deep
/cost-report last --n 5                                # Last 5 runs detailed
/cost-report budget set --scope daily --usd 10         # Set a soft cap
/cost-report budget show
```

## Sub-commands

### `estimate <command-with-args>`

Dry-run a command without executing it. Walks the command's `Process` block to estimate:
- Which agents would be invoked
- Expected round count (for debates)
- Per-agent average token cost from `/agent-usage-stats --json`
- Upper and lower bounds based on historical variance

Output:

```
# Cost Estimate

**Command**: /parliament-review
**Estimated agents invoked**: 9 (all grumpy reviewers)
**Estimated tokens**: 380K–620K (p50: 465K)
**Estimated cost**: $1.72–$2.81 (p50: $2.10)

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

## Process

1. Parse sub-command.
2. For `estimate`: statically analyse the target command's `Process` block, look up historical per-agent cost, compute bounds.
3. For `last`: call `/telemetry-query --event TaskCompleted --since 7d --json`, sort, limit.
4. For `budget`: read/write `${CLAUDE_PLUGIN_DATA}/budgets.json`.
5. Render.

## Notes

- Estimates are heuristic; they use the p50/p95 from recent telemetry when available, and fall back to static defaults for commands with no history.
- Cost figures require `${CLAUDE_PLUGIN_DATA}/cost-rates.json`. If absent, tokens are shown but USD is `n/a`.
- This command never edits the cost-rates file — use `config-curator` or hand-edit for rate changes.
- Budget caps are per-scope soft limits. A "hard cap" variant was rejected in the toolset-gaps debate — it would break governance (convenience cannot override security or correctness work).
- Pair with `/parliament-metrics --focus cost` for the retrospective dashboard view.
