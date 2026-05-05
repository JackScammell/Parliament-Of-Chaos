---
description: Dashboard view — token attribution per agent, session cost, SLO status for background monitors, trend analysis
effort: medium
---

# Parliament Metrics

Aggregate dashboard over plugin telemetry. Pulls from `/telemetry-query` as its data source and renders four panels: cost, latency, SLO status, and trend.

This is the "observability" half of Tier 3 — it answers *is Parliament healthy and how much is it costing?*

## Usage

```
/parliament-metrics [--window <duration>] [--focus cost|latency|slo|trend|all] [--json] [--strict-duration] [--by-effort] [--by-trigger]
```

**Examples**:
```
/parliament-metrics                         # 7-day dashboard, all panels
/parliament-metrics --window 30d            # Month view
/parliament-metrics --focus cost            # Cost panel only
/parliament-metrics --focus slo --json      # Monitor health in JSON
/parliament-metrics --focus cost --by-effort # Cost panel split by effort tier
/parliament-metrics --focus cost --by-trigger # Cost panel split by invocation trigger
/parliament-metrics --by-effort --by-trigger  # Two-dimensional split (effort × trigger)
```

## Options

- `--window <duration>`: Lookback window. Defaults to `7d`. Accepts `Nh`, `Nd`, `Nw`, `Nmo`.
- `--focus <panel>`: Render only one panel. Useful in automation.
- `--json`: Machine-readable output — consumed by `/parliament-webhook` and external dashboards.
- `--strict-duration`: Latency panel uses only the `duration_ms` field captured by `PostToolUse` / `PostToolUseFailure` hooks. Rows without a captured value are dropped rather than inferred from event-pair timestamps. Recommended when comparing across recent windows where the hook was definitely wired.
- `--by-effort`: Group cost and latency panels by effort tier (`low` / `medium` / `high` / `xhigh`). Tier is sourced from the OTel `effort` attribute on `cost.usage` / `token.usage` / `api_request` / `api_error` events (Claude Code v2.1.117+) and from the status-line `effort.level` field (v2.1.119+). When neither is present, the row is grouped under `unknown`.
- `--by-trigger`: Group cost and latency panels by invocation trigger (`user-slash` / `claude-proactive` / `nested-skill`). Trigger is sourced from the `invocation_trigger` attribute on `claude_code.skill_activated` OTel events (Claude Code v2.1.126+); on older versions a heuristic fallback derives it from event ordering. Rows that resolve to neither source are grouped under `unknown`. Composable with `--by-effort` — passing both flags produces a two-dimensional split.

## Effort attribution (Claude Code v2.1.117+)

Telemetry written under Claude Code v2.1.117 and later carries the effort tier of the
session that produced each event. `/parliament-metrics` uses two sources, in order:

1. The `effort` attribute on `cost.usage` / `token.usage` / `api_request` / `api_error`
   OTel spans (v2.1.117).
2. The `effort.level` field in the status-line JSON event (v2.1.119).

When `${CLAUDE_EFFORT}` is set in the running session (v2.1.120), it is used as the
default for any newly emitted events that do not yet carry an explicit attribute. This
means `/parliament-metrics --by-effort` works uniformly across event ages without
requiring users to pass `--mode` flags. Older events without effort data fall under
`unknown` and are reported separately so partial historical data does not skew the
breakdown.

## Trigger attribution (Claude Code v2.1.126+)

Telemetry written under Claude Code v2.1.126 and later carries the invocation trigger
of the skill or command that produced each event. `/parliament-metrics` uses two
sources, in order:

1. The `invocation_trigger` attribute on `claude_code.skill_activated` OTel events
   (v2.1.126). Authoritative when present; values are `user-slash`,
   `claude-proactive`, or `nested-skill`.
2. A heuristic fallback for events emitted on Claude Code < v2.1.126, derived from
   event ordering: a `skill_activated` event immediately following a user message is
   attributed to `user-slash`; one emitted while another skill is already active is
   attributed to `nested-skill`; otherwise the event is attributed to
   `claude-proactive`.

The heuristic is best-effort, not authoritative — it can misclassify cases where the
event stream is interleaved (e.g. parallel skill activations, or a user message that
arrives mid-skill). Rows where neither the attribute nor the heuristic resolves a
trigger fall under `unknown` and are reported separately so partial historical data
does not skew the breakdown. When comparing trigger mix across windows that span the
v2.1.126 boundary, prefer windows that fall entirely on one side, or filter to the
authoritative source by checking the `source` column where surfaced.

## Panels

### 1. Cost

Token attribution by agent and session.

```
## Cost (window: 7d)

**Total tokens**: 4.82M (input: 3.14M, output: 1.68M)
**Estimated spend**: $18.40

### Top 10 agents by token cost
| Agent              | Invocations | Tokens | % of total | Δ vs prior window |
|--------------------|-------------|--------|------------|-------------------|
| senior-council     | 28          | 1.21M  | 25.1%      | +4.2%             |
| deliberation-conductor | 4       | 890K   | 18.5%      | +11.0%            |
| doc-bard           | 19          | 410K   | 8.5%       | -2.1%             |
| ...                | ...         | ...    | ...        | ...               |

### Most expensive sessions
| session_id | command          | tokens | duration | cost est. |
|-----------|------------------|--------|----------|-----------|
| fc777472  | /debate-topic    | 680K   | 14m12s   | $2.58     |
| 2a9f11c8  | /parliament-review | 420K | 9m04s    | $1.60     |
```

### 2. Latency

Per-command p50 / p95 / max. As of Parliament v1.14.0 (Claude Code v2.1.119+), this panel
prefers the `duration_ms` field captured on `PostToolUse` / `PostToolUseFailure` events
when available, falling back to event-pair inference (`SubagentStart` → `Stop`) on older
versions or for commands not surfaced through the tool-use payload.

```
## Latency (window: 7d)

| Command              | count | p50    | p95    | max    | source        |
|----------------------|-------|--------|--------|--------|---------------|
| /summon-council      | 14    | 4m12s  | 11m40s | 18m22s | duration_ms   |
| /parliament-review   | 22    | 2m50s  | 6m30s  | 9m04s  | duration_ms   |
| /format-code         | 41    | 3s     | 12s    | 28s    | duration_ms   |
| /summon-specialist   | 8     | 1m05s  | 3m20s  | 4m11s  | inferred*     |
```

`*inferred` indicates the row was computed from event-pair timestamps because no
`duration_ms` value was logged for that invocation (Claude Code < v2.1.119 or the
PostToolUse hook was not wired). The `--strict-duration` flag drops inferred rows.

### 3. SLO status (background monitors)

For monitors launched via `/parliament-monitor` or `/parliament-loop`.

```
## SLO Status

| Monitor             | uptime | last run          | next run          | status |
|---------------------|--------|-------------------|-------------------|--------|
| /changelog-review   | 100%   | 2026-04-17T09:00Z | 2026-04-24T09:00Z | OK     |
| /track-debt         | 92%    | 2026-04-17T06:00Z | 2026-04-18T06:00Z | WARN   |
| /security-scan      | 98%    | 2026-04-17T04:00Z | 2026-04-18T04:00Z | OK     |

WARN detail: /track-debt — 2 failures in last 30 days, both exceeded 5-minute timeout.
```

### 4. Trend

Rolling comparisons against the previous equal-length window.

```
## Trend (7d vs prior 7d)

| Metric                    | Current | Prior  | Δ       |
|---------------------------|---------|--------|---------|
| Total agent invocations   | 612     | 541    | +13.1%  |
| Total tokens              | 4.82M   | 4.11M  | +17.3%  |
| Debate avg convergence    | 0.84    | 0.79   | +0.05   |
| Reviewer APPROVE rate     | 62%     | 58%    | +4.0pp  |
| Monitor failure count     | 2       | 5      | -60%    |
```

## Process

1. Call `/telemetry-query --json` with the specified window for each required event type.
2. Aggregate per panel. When `--by-effort` is set, partition each row by effort tier using the attribution rules above; when `--by-trigger` is set, partition each row by invocation trigger using the trigger-attribution rules. When both flags are set, the partitions compose into a two-dimensional split (effort tier × trigger).
3. Fetch previous-window figures for trend deltas.
4. Render markdown tables (or JSON if `--json`).

## Data sources

- `/telemetry-query` output (primary)
- `/agent-usage-stats --json` for reviewer approval rates
- `${CLAUDE_PLUGIN_DATA}/monitors/` state files for SLO status (optional — falls back to "no monitors configured")

## Notes

- Cost figures use a configurable price table (`${CLAUDE_PLUGIN_DATA}/cost-rates.json`) — if missing, tokens are shown but spend is marked `n/a`.
- The command is read-only. It never mutates telemetry.
- Pair with `/cost-report` for the forward-looking budget view; `/parliament-metrics` is the retrospective view.
- Exit is always 0 — this is a reporting command, not a gate. Use `/cost-report --strict` for budget enforcement.
- Webhook delivery of the dashboard is handled by `/parliament-webhook` subscribing to a schedule.
