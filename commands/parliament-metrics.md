---
description: Dashboard view — token attribution per agent, session cost, SLO status for background monitors, trend analysis
effort: medium
---

# Parliament Metrics

Aggregate dashboard over plugin telemetry. Pulls from `/telemetry-query` as its data source and renders four panels: cost, latency, SLO status, and trend.

This is the "observability" half of Tier 3 — it answers *is Parliament healthy and how much is it costing?*

## Usage

```
/parliament-metrics [--window <duration>] [--focus cost|latency|slo|trend|all] [--json]
```

**Examples**:
```
/parliament-metrics                         # 7-day dashboard, all panels
/parliament-metrics --window 30d            # Month view
/parliament-metrics --focus cost            # Cost panel only
/parliament-metrics --focus slo --json      # Monitor health in JSON
```

## Options

- `--window <duration>`: Lookback window. Defaults to `7d`. Accepts `Nh`, `Nd`, `Nw`, `Nmo`.
- `--focus <panel>`: Render only one panel. Useful in automation.
- `--json`: Machine-readable output — consumed by `/parliament-webhook` and external dashboards.

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

Per-command p50 / p95 / max.

```
## Latency (window: 7d)

| Command              | count | p50    | p95    | max    |
|----------------------|-------|--------|--------|--------|
| /summon-council      | 14    | 4m12s  | 11m40s | 18m22s |
| /parliament-review   | 22    | 2m50s  | 6m30s  | 9m04s  |
| /format-code         | 41    | 3s     | 12s    | 28s    |
```

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
2. Aggregate per panel.
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
