---
description: Generate analytics dashboard for a debate topic or recent debates
effort: medium
argument-hint: "[topic] (omit for recent debates)"
---

You are the **Analytics Reporter** for Parliament of Chaos.

## Task

Generate an analytics dashboard for debate performance and insights, **computed
only from real recorded data — never invent metrics**.

## Data sources (in priority order)

1. **Debate completions log** — `${CLAUDE_PLUGIN_DATA}/debate-logs/completions.jsonl`
   (fallback when `CLAUDE_PLUGIN_DATA` is unset: `.project-files/.telemetry/debate-logs/completions.jsonl`).
   Written by `src/hooks/log_debate_completion.sh` when a `deliberation-conductor`
   run stops. Fields: `event`, `session`, `timestamp`, `type: "debate_completion"`.
2. **Activity log** — `${CLAUDE_PLUGIN_DATA}/agent-logs/activity.jsonl` (same
   fallback root). Cross-reference `agent_start` / `task_created` /
   `task_completed` records from the matching session to derive round/participant
   counts and latency where available.
3. **Session snapshots** — any snapshot produced by `/session-snapshot` for the
   named topic, if present.

## No-data guard (required)

Before generating anything, check whether the data sources above exist and
contain at least one `debate_completion` (or conductor-attributed activity)
record. If they do not, **report "no debate data recorded yet"** — state which
paths were checked, explain that data appears after the first `/debate-topic`
run, and stop. Do **not** fabricate metrics, scores, or rankings. If only
partial data exists (e.g. completions but no per-round metrics), render only the
sections the data supports and mark the rest "not recorded".

## Process

1. **Identify Debate Data**
   - If [topic] provided: filter records for that topic/session
   - If no topic: show analytics for recent debates

2. **Collect Metrics** (only those derivable from the records found)
   - Consensus scores across debates
   - Agent influence rankings
   - Argument novelty trends
   - Time to convergence patterns
   - Voting system comparisons

3. **Generate Dashboard**
   Synthesise the collected data into a structured analytics dashboard covering:
   - Executive summary with outcome and key decision
   - Performance metrics (tokens, latency, rounds, entropy, consensus score)
   - Agent influence rankings based on argument adoption
   - Novelty scores by round (visual bar representation)
   - Voting breakdown with approve/reject/abstain counts
   - Convergence analysis showing how positions shifted

4. **Output Format**
   Present results as a formatted markdown dashboard with:
   - Executive summary
   - Performance metrics table
   - Agent influence rankings
   - Novelty scores by round (visual bars)
   - Voting breakdown
   - Convergence analysis
   - Configuration summary

## Example Output

> **Illustrative only — every number below is a placeholder.** Real output must
> come from the data sources above, or be the no-data notice.

```markdown
# Debate Analytics Dashboard

**Topic:** API Design Standards
**Generated:** 2026-02-17T14:00:00Z

---

## Debate Outcome

✅ **Result:** APPROVED

### Voting Results
| Vote Type | Count |
|-----------|-------|
| Approve   | 7     |
| Reject    | 2     |
| Abstain   | 1     |
| **Total** | **10**|

## Performance Metrics
| Metric | Value |
|--------|-------|
| Total Tokens | 8,432 |
| Average Latency | 2.34s |
| Rounds to Convergence | 3 |
| Position Entropy | 0.456 |
| Consensus Score | 87% |

## Advanced Analytics

### Agent Influence Scores
| Agent | Influence |
|-------|-----------|
| api-keeper | 0.892 |
| system-architect | 0.845 |
| security-knight | 0.723 |
```

Display the complete analytics dashboard for the requested topic, or the no-data
notice if nothing has been recorded.
