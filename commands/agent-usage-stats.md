---
description: Show frequency and effectiveness per agent — input to retirement and optimisation decisions
effort: medium
argument-hint: "[--since <duration>] [--agent <name>] [--json] [--underused]"
---

# Agent Usage Stats

Aggregate the activity log to produce per-agent usage and effectiveness statistics. Answers the question: *which agents are earning their seat at the table, and which should be retired?*

Reads `activity.jsonl` (plus rotated `activity.jsonl.old`) from the plugin data directory and emits a ranked report.

## Usage

```
/agent-usage-stats [--since <duration>] [--agent <name>] [--json] [--underused]
```

**Examples**:
```
/agent-usage-stats                        # Full report, default window 30 days
/agent-usage-stats --since 7d             # Last 7 days
/agent-usage-stats --agent doc-bard       # Detail for one agent
/agent-usage-stats --underused            # Only agents invoked < 3 times in window
/agent-usage-stats --json                 # Machine-readable, for /parliament-metrics
```

## Options

- `--since <duration>`: `Nd` (days), `Nw` (weeks), `Nmo` (months), or ISO date. Defaults to `30d`.
- `--agent <name>`: Restrict to one agent; shows detailed per-invocation breakdown.
- `--underused`: Filter to agents invoked fewer than 3 times in the window (retirement candidates).
- `--json`: Structured output.

## Data sources

- `${CLAUDE_PLUGIN_DATA}/activity.jsonl` (primary)
- `${CLAUDE_PLUGIN_DATA}/activity.jsonl.old` (rotated previous window, if present)
- Debate transcripts under `${CLAUDE_PLUGIN_DATA}/debates/` for per-agent vote and convergence contribution (optional — skipped if absent)

## Process

1. **Load events** — stream both log files, parse as NDJSON, filter by timestamp.
2. **Aggregate per agent**:
   - `invocations` — count of `TaskCreated` / `TaskCompleted` events
   - `avg_turns` — mean `maxTurns`-bounded actual turn count
   - `avg_duration_s` — mean wall-clock seconds
   - `token_cost` — summed token usage if present
   - `approval_rate` — fraction of reviewer invocations ending in a **non-blocking** verdict (`APPROVE-WITH-NOTES`, `APPROVE`, or `NO-FINDINGS`); only `REJECT` counts against it (reviewers only)
   - `convergence_contribution` — for agents appearing in debates, mean delta-convergence they produced per round
3. **Rank and classify**:
   - **Workhorses**: high invocation, predictable duration
   - **Specialists**: low invocation but high-value (e.g. used in critical decisions)
   - **Benchwarmers**: low invocation, no standout quality signal → retirement candidates
4. **Emit report**.

## Output

```
# Agent Usage Stats

**Window**: 2026-03-18 → 2026-04-17 (30d)
**Total agent invocations**: 1,284
**Unique agents active**: 31 of 33

## Workhorses (top 5)
| Agent | Invocations | Avg turns | Avg duration | Token cost |
|-------|-------------|-----------|--------------|-----------|
| senior-council | 142 | 22 | 318s | 1.8M |
| grumpy-code-reviewer | 128 | 4 | 42s | 420K |
| doc-bard | 98 | 11 | 156s | 610K |
| test-prophet | 87 | 13 | 180s | 720K |
| backend-goblin | 72 | 14 | 210s | 950K |

## Reviewers — approval rate
| Reviewer | Invocations | Non-blocking rate | Median severity raised |
|----------|-------------|--------------|------------------------|
| grumpy-code-reviewer | 128 | 58% | Medium |
| grumpy-security-nag | 44 | 71% | High |
| grumpy-i18n-nitpicker | 2 | 50% | High |

## Benchwarmers (retirement candidates)
| Agent | Invocations | Why flagged |
|-------|-------------|-------------|
| grumpy-i18n-nitpicker | 2 | Below 3-invocation floor; driver added in v1.10.0 — give one more window |

## Not invoked this window
- migration-monk — 0 invocations (last used 2026-02-12)

## Recommendations
- Keep grumpy-i18n-nitpicker on probation — new /i18n-audit driver shipped 2026-04-17; re-evaluate next window.
- Consider /decision-review adr:0005 (migration-monk scope) — agent dormant 60+ days.
```

## Notes

- This command is read-only; it never modifies agent files.
- Retirement is a policy decision — the report flags candidates, but action requires `/decision-review` followed by explicit removal.
- When `activity.jsonl` is absent (older Parliament versions without the log-rotation hook), the command reports "no data" rather than guessing.
- Pair with `/parliament-metrics` (Tier 3) for dashboards and with `/telemetry-query` for ad-hoc slicing.
- The `approval_rate` signal is only meaningful for reviewers — specialist agents are not scored on it.
