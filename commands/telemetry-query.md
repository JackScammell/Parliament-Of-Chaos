---
description: Ad-hoc query over activity.jsonl and the plugin data directory — read path for Parliament telemetry
effort: medium
---

# Telemetry Query

The `activity.jsonl` log and other files under `${CLAUDE_PLUGIN_DATA}/` are write-only today — hooks append but nothing reads them. This command is the missing read path: an ad-hoc query tool with filters, aggregations, and output formats suitable for piping into `/parliament-metrics` or human review.

## Usage

```
/telemetry-query [--event <name>] [--agent <name>] [--since <duration>] [--until <duration>] [--where <expr>] [--group-by <field>] [--limit <n>] [--json]
```

**Examples**:
```
/telemetry-query --event TaskCompleted --since 24h
/telemetry-query --agent grumpy-code-reviewer --since 7d --group-by session_id
/telemetry-query --event PermissionDenied --since 30d   # diagnose auto-mode denials
/telemetry-query --where 'duration_ms > 60000' --limit 20
/telemetry-query --event Stop --since 7d --group-by reason --json
```

## Options

- `--event <name>`: Filter by hook event name (e.g. `TaskCreated`, `TaskCompleted`, `Stop`, `PermissionDenied`, `SubagentStop`, `PostToolUse`, `DebateCompleted`).
- `--agent <name>`: Filter by the agent field where present.
- `--since <duration>` / `--until <duration>`: Time window. Accepts `Nh`, `Nd`, `Nw`, `Nmo`, or ISO timestamps. Defaults: `--since 7d`, `--until now`.
- `--where <expr>`: Post-filter expression over record fields. Supports simple comparisons (`==`, `!=`, `<`, `>`, `contains`). Whitelisted fields only — no arbitrary code execution.
- `--group-by <field>`: Aggregate counts by field (`agent`, `event`, `session_id`, `reason`, `tool`, etc.).
- `--limit <n>`: Cap result rows. Default 100.
- `--json`: Emit structured output.

## Data Sources

- `${CLAUDE_PLUGIN_DATA}/activity.jsonl` (primary)
- `${CLAUDE_PLUGIN_DATA}/activity.jsonl.old` (rotated previous window, merged transparently when the `--since` window reaches back into it)
- `${CLAUDE_PLUGIN_DATA}/debates/` (optional — surfaced via `--event DebateCompleted`)

If the plugin data directory falls back to `.project-files/.telemetry/` (older Claude Code without `CLAUDE_PLUGIN_DATA`), the fallback is used automatically.

## Process

1. **Resolve data dir** — use `${CLAUDE_PLUGIN_DATA}` if set, else `.project-files/.telemetry/`. Exit with a clear message if neither exists.
2. **Stream matching files** — parse NDJSON, honouring time window first to short-circuit reads.
3. **Apply filters** — in order: event → agent → where.
4. **Aggregate or list** — if `--group-by` supplied, emit counts per group; otherwise emit rows up to `--limit`.
5. **Format** — markdown table by default, JSON with `--json`.

## Output

Row listing:

```
# Telemetry Query

**Window**: 2026-04-10 → 2026-04-17 (7d)
**Filters**: event=TaskCompleted, agent=grumpy-code-reviewer
**Rows**: 42 (capped at 100)

| timestamp            | session_id  | duration_ms | turns | outcome  |
|---------------------|-------------|-------------|-------|----------|
| 2026-04-17T09:12:03Z | ab33e7…    | 41,820      | 4     | APPROVE  |
| 2026-04-17T09:08:11Z | ab33e7…    | 39,500      | 4     | REJECT   |
| ...                  | ...         | ...         | ...   | ...      |
```

Group-by:

```
# Telemetry Query

**Window**: 2026-04-10 → 2026-04-17 (7d)
**Filters**: event=Stop
**Group by**: reason

| reason              | count |
|---------------------|-------|
| converged           | 108   |
| max_turns_exceeded  |  12   |
| user_interrupt      |   7   |
| error               |   3   |
```

## Security

- `--where` expressions are parsed into a whitelisted AST. No shell-out, no `eval`.
- The command never writes to the plugin data directory — read-only.
- File paths are canonicalised; queries cannot escape `${CLAUDE_PLUGIN_DATA}`.

## Notes

- This is the foundational primitive for Tier 3. Both `/parliament-metrics` and `/cost-report` consume its JSON output.
- Performance: lines are streamed, not buffered. Large logs (>100 MB) are fine; memory stays bounded.
- If `jq` is available in the environment, it is used for acceleration; otherwise a pure-shell fallback handles parsing.
- Pair with `/agent-usage-stats` — that command is a convenience wrapper over the most common `/telemetry-query --group-by agent` pattern.
