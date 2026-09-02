---
description: Dashboard view — token attribution per agent, session cost, SLO status for background monitors, trend analysis
effort: medium
argument-hint: "[--window <duration>] [--focus cost|latency|slo|trend|all] [--json] [--strict-duration] [--by-effort] [--by-trigger]"
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
- `--focus <panel>`: Render only one panel. Useful in automation. `--focus slo` also renders the member-reliability / circuit-breaker sub-view (see panel 3).
- `--json`: Machine-readable output — consumed by `/parliament-webhook` and external dashboards.
- `--strict-duration`: Latency panel uses only the `duration_ms` field captured by `PostToolUse` / `PostToolUseFailure` hooks. Rows without a captured value are dropped rather than inferred from event-pair timestamps. Recommended when comparing across recent windows where the hook was definitely wired.
- `--by-effort`: Group cost and latency panels by effort tier (`low` / `medium` / `high` / `xhigh`). Tier is sourced from the OTel `effort` attribute on `cost.usage` / `token.usage` / `api_request` / `api_error` events (Claude Code v2.1.117+), the status-line `effort.level` field (v2.1.119+), and the `effort_level` field written onto hook-emitted `activity.jsonl` events by `log_event.sh` (Claude Code v2.1.133+). When none is present, the row is grouped under `unknown`.
- `--by-trigger`: Group cost and latency panels by invocation trigger (`user-slash` / `claude-proactive` / `nested-skill`). Trigger is sourced from the `invocation_trigger` attribute on `claude_code.skill_activated` OTel events (Claude Code v2.1.126+); on older versions a heuristic fallback derives it from event ordering. Rows that resolve to neither source are grouped under `unknown`. Composable with `--by-effort` — passing both flags produces a two-dimensional split.

## Effort attribution (Claude Code v2.1.117+)

Telemetry written under Claude Code v2.1.117 and later carries the effort tier of the
session that produced each event. `/parliament-metrics` uses three sources, in order:

1. The `effort` attribute on `cost.usage` / `token.usage` / `api_request` / `api_error`
   OTel spans (v2.1.117).
2. The `effort.level` field in the status-line JSON event (v2.1.119).
3. The `effort_level` field on hook-emitted `activity.jsonl` events. `log_event.sh`
   reads `effort.level` from the hook payload (Claude Code v2.1.133+) and writes it
   additively onto every event it logs, so hook-only events (e.g. `SubagentStart`,
   `PostToolUse`) carry their own effort tier without needing a co-located OTel span
   or status-line event. Absent on telemetry written under older Claude Code.

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

## Fresh-install guard

Before rendering any panel, check that `${CLAUDE_PLUGIN_DATA}/agent-logs/activity.jsonl` (or the `.project-files/.telemetry/` fallback) exists and is non-empty. If not, report **"no telemetry recorded yet"** with the paths checked, note that records appear once hook events fire, and render only panels that have a real data source. Never fabricate metrics or render zero-filled panels as though they were measured.

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

#### Member reliability / circuit breaker (B4 watchdog surface)

Rendered as part of the SLO panel (and under `--focus slo`). This is the observability
surface for the B4 out-of-band watchdog: it makes a chronically-failing council member
visible so the fan-out loop can **skip** it rather than re-spawn it forever. It reconciles
per-member outcomes from `activity.jsonl`, using the `task_completed` events `log_event.sh`
writes as of v1.23.0 alongside the existing `SubagentStart` and `StopFailure` events. Fields are
read best-effort: a member with no `agent_id` (older Claude Code) is grouped under `unknown`.

**Detection semantics** follow `.claude/rules/fan-out-policy.md` (single-sourced there so
this view and the orchestrator can't diverge). Per member, over the window:

- **completed** — a `task_completed` event (verdict returned / Done).
- **failed** — `SubagentStart` seen, no `task_completed`, `StopFailure` logged.
- **non-reporting** — `SubagentStart` seen, no `task_completed`, no `StopFailure`
  (the mid-flight-hang class the watchdog exists to catch).

Members are keyed by the additive `agent_id` field on the envelope (present on
`SubagentStart` / `task_completed` from Claude Code v2.1.139+). Events without `agent_id`
(older Claude Code, or top-session hooks) are grouped under `unknown` and reported
separately so partial history does not skew per-member counts.

**Circuit-breaker state** is a rolling summary, not a live gate (this command is read-only —
it reports the breaker, it does not open or trip it):

- **closed** — the member is healthy under the policy threshold.
- **open** — the member crossed the breaker threshold **defined in `fan-out-policy.md`**
  (`Failed` or `Non-reporting` on ≥ 2 of its last 3 dispatches). Per that policy the fan-out loop
  skips it on the next run (floor members excepted — they force `INCOMPLETE` instead). This view
  only **reports** the state; the skip decision and its floor override are owned by the policy,
  not by this read-only command.

```
## Member reliability (window: 30d)

| Member                  | dispatched | completed | failed | non-reporting | breaker |
|-------------------------|-----------|-----------|--------|---------------|---------|
| grumpy-security-nag     | 42        | 42        | 0      | 0             | closed  |
| grumpy-code-reviewer    | 42        | 41        | 1      | 0             | closed  |
| grumpy-i18n-nitpicker   | 38        | 12        | 3      | 23            | OPEN    |
| (unknown agent_id)      | 6         | 6         | 0      | 0             | n/a     |

OPEN detail: grumpy-i18n-nitpicker — 23 non-reporting + 3 failed of 38 dispatched over 30d;
             breaker OPEN per fan-out-policy.md (unhealthy on ≥ 2 of its last 3 dispatches).
             Per policy the fan-out loop skips it on the next run rather than re-dispatching.
             A floor member in this state would instead force INCOMPLETE (never a survivor-
             synthesised APPROVE).
```

Floor members (`grumpy-security-nag`, `grumpy-code-reviewer`, and `grumpy-privacy-paranoid`
on PII) are labelled as such in the row; an OPEN breaker on a floor member is surfaced as the
highest-priority signal because the fan-out loop must return `INCOMPLETE` rather than skip it.

### 4. Trend

Rolling comparisons against the previous equal-length window.

```
## Trend (7d vs prior 7d)

| Metric                    | Current | Prior  | Δ       |
|---------------------------|---------|--------|---------|
| Total agent invocations   | 612     | 541    | +13.1%  |
| Total tokens              | 4.82M   | 4.11M  | +17.3%  |
| Debate avg convergence    | 0.84    | 0.79   | +0.05   |
| Reviewer non-blocking rate| 62%     | 58%    | +4.0pp  |
| Monitor failure count     | 2       | 5      | -60%    |
```

## Process

1. Call `/telemetry-query --json` with the specified window for each required event type.
2. Aggregate per panel. When `--by-effort` is set, partition each row by effort tier using the attribution rules above; when `--by-trigger` is set, partition each row by invocation trigger using the trigger-attribution rules. When both flags are set, the partitions compose into a two-dimensional split (effort tier × trigger).
3. Fetch previous-window figures for trend deltas.
4. For the SLO panel's member-reliability sub-view, reconcile per-member `SubagentStart` /
   `task_completed` / `StopFailure` events from `activity.jsonl` into completed / failed /
   non-reporting counts (keyed on `agent_id`), then derive each member's circuit-breaker
   state using the thresholds in `.claude/rules/fan-out-policy.md`.
5. Render markdown tables (or JSON if `--json`).

## Data sources

- `/telemetry-query` output (primary)
- `/agent-usage-stats --json` for reviewer approval rates
- `${CLAUDE_PLUGIN_DATA}/monitors/` state files for SLO status (optional — falls back to "no monitors configured")
- `activity.jsonl` `SubagentStart` / `task_completed` / `StopFailure` events for the member-reliability sub-view (per-member counts + circuit-breaker state)
- `.claude/rules/fan-out-policy.md` for the member-reliability detection semantics and circuit-breaker thresholds

## Notes

- Cost figures use a configurable price table (`${CLAUDE_PLUGIN_DATA}/cost-rates.json`) — if missing, tokens are shown but spend is marked `n/a`.
- The command is read-only. It never mutates telemetry.
- Pair with `/cost-report` for the forward-looking budget view; `/parliament-metrics` is the retrospective view.
- Exit is always 0 — this is a reporting command, not a gate. Use `/cost-report --strict` for budget enforcement.
- Webhook delivery of the dashboard is handled by `/parliament-webhook` subscribing to a schedule.
