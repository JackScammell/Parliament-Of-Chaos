---
description: Checkpoint the current session so it can be resumed or replayed after a crash or interruption
effort: medium
argument-hint: "create [--label <text>]"
---

# Session Snapshot

Checkpoint the state of a running Parliament session so the work survives a crash, compaction, or deliberate pause. This is also the shared primitive that `/debate-replay` depends on — without snapshots, past debates cannot be deterministically re-run.

## Usage

```
/session-snapshot create [--label <text>]
/session-snapshot list
/session-snapshot resume <snapshot-id>
/session-snapshot show <snapshot-id>
/session-snapshot prune [--keep <n>] [--older-than <duration>]
```

**Examples**:
```
/session-snapshot create                                # Auto-labelled
/session-snapshot create --label "before risky refactor"
/session-snapshot list
/session-snapshot resume 2026-04-17T14-22-05Z
/session-snapshot prune --keep 20
```

## Sub-commands

### `create [--label <text>]`

Captures:
- Current conversation transcript (or a summary if it exceeds 50K tokens)
- Active council state: which agents are in flight, their last outputs
- Active debate state: topic, mode, round, per-round metrics, per-agent positions
- Open task list if `/implement-task-list` is in progress
- Environment: model, working directory, git HEAD, dirty-tree flag
- Random seed used by the sampler (best-effort; see `/debate-replay` notes)

Written to `${CLAUDE_PLUGIN_DATA}/sessions/<session-id>/snapshots/<timestamp>.json`.

### `list`

Show all snapshots for the current session, plus recent snapshots from other sessions.

```
| snapshot-id              | label              | created (UTC)        | size  |
|--------------------------|--------------------|----------------------|-------|
| 2026-04-17T14-22-05Z     | before risky refactor | 2026-04-17 14:22  | 180KB |
| 2026-04-17T13-11-44Z     | auto                | 2026-04-17 13:11     | 92KB  |
```

### `resume <snapshot-id>`

Load a snapshot and restore conversational context. For in-flight debates/councils, re-attaches the orchestrator and signals it to continue from the saved round. If the snapshot is from a different model version, the user is warned before resuming.

### `show <snapshot-id>`

Human-readable rendering of a snapshot's metadata without restoring it.

### `prune`

Remove old snapshots. `--keep N` retains the N most recent. `--older-than Nd` removes anything older than N days. At least 3 snapshots are always retained regardless of flags.

## Snapshot schema (v1)

```json
{
  "schema_version": 1,
  "session_id": "fc777472-f0ef-4dea-81da-a98115d4c9ec",
  "snapshot_id": "2026-04-17T14-22-05Z",
  "label": "before risky refactor",
  "created_at": "2026-04-17T14:22:05Z",
  "parliament_version": "1.13.0",
  "model": "claude-opus-4-7",
  "cwd": "/Users/jack/Parliament-Of-Chaos",
  "git": { "head": "acc5249", "dirty": false },
  "transcript_summary": "...",
  "active_debate": {
    "topic": "...",
    "mode": "consensus",
    "round": 3,
    "per_round_metrics": [...],
    "per_agent_positions": [...]
  },
  "active_council": null,
  "active_task_list": null,
  "seed": 1729183325
}
```

## Process

1. Resolve `${CLAUDE_PLUGIN_DATA}` (fall back to `.project-files/.telemetry/` with a warning — snapshots should really live in plugin data).
2. Probe the current session state via introspection hooks.
3. Serialise according to schema v1.
4. Write atomically (tmp file + rename) to avoid corrupt snapshots.
5. Update `${CLAUDE_PLUGIN_DATA}/sessions/<session-id>/snapshots/INDEX.json`.

## Recovery UX

If Parliament detects an unfinished council or debate from a previous crashed session at startup, it looks for the most recent snapshot and offers `/session-snapshot resume` as a suggestion. This addresses the "session crash" footgun from `feedback_release_process.md` and related memory.

## Notes

- Snapshots include conversational context. Treat them as sensitive — do not check them into public git. The `.project-files/.telemetry/` fallback directory should be gitignored (the plugin already does this for `.telemetry/`).
- Schema version is explicit. When a new field is added, bump `schema_version` and update the reader in `/debate-replay`.
- Atomic writes prevent a crash-during-snapshot from corrupting state.
- `/debate-replay` is the primary consumer of this command's output.
- Auto-snapshots: `/parliament-loop 15m /session-snapshot create` is a reasonable default for long-running work.
