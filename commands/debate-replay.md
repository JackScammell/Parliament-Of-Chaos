---
description: Deterministically replay a past debate from a session snapshot — regression tests the deliberation engine
effort: medium
argument-hint: "<session-id> [--snapshot <path>] [--strict] [--compare-to <session-id>]"
---

# Debate Replay

Replay a past `/debate-topic` session from its snapshot and verify that the deliberation engine produces the same outcome. If the replay diverges, either the engine regressed or a model change has perturbed convergence — both are actionable signals.

This command depends on `/session-snapshot` (Tier 4 — item 4.1). Without a snapshot, there is nothing to replay; the command will report clearly when snapshot infrastructure is absent.

## Usage

```
/debate-replay <session-id> [--snapshot <path>] [--strict] [--compare-to <session-id>]
```

**Examples**:
```
/debate-replay fc777472
/debate-replay fc777472 --strict                  # Fail loudly on any divergence
/debate-replay fc777472 --compare-to ea113388     # Compare two runs of the same topic
```

## Options

- `<session-id>` (required): The original debate session to replay.
- `--snapshot <path>` (optional): Explicit path to the snapshot. Defaults to `${CLAUDE_PLUGIN_DATA}/sessions/<session-id>/snapshot.json`.
- `--strict` (optional): Exit non-zero if the replay's verdict, convergence trajectory, or vote distribution differs from the original.
- `--compare-to <session-id>` (optional): Compare against a different session rather than the snapshot's own original. Useful for A/B testing prompt changes.

## Process

1. **Load snapshot**
   - Resolve the snapshot path, default `${CLAUDE_PLUGIN_DATA}/sessions/<id>/snapshot.json`
   - Fail clearly with a pointer to `/session-snapshot` if missing
2. **Recreate context**
   - Read the snapshot's `topic`, `mode`, `participants`, `seed`, and `round_inputs`
   - Restore the agent roster exactly — same versions, same effort tiers, same `disallowedTools`
3. **Run the debate**
   - Invoke `deliberation-conductor` with the recorded topic and mode
   - Feed the same seed to the sampler for determinism (model sampling is inherently non-deterministic, but deterministic seeds reduce variance)
4. **Diff the outcomes**
   - Compare per-round: novelty, overlap, convergence metrics
   - Compare final votes and verdict
   - Compute a divergence score: fraction of per-agent positions that shifted verdict
5. **Report**
   - Side-by-side table of original vs replay for each round
   - Highlight divergence points and classify (stochastic noise vs material disagreement)
6. **Persist**
   - Write the replay transcript to `${CLAUDE_PLUGIN_DATA}/sessions/<id>/replays/YYYY-MM-DDTHH-MM-SSZ.json`
   - Update `${CLAUDE_PLUGIN_DATA}/sessions/<id>/replays/INDEX.json` for future comparisons

## Output

```
# Debate Replay — session fc777472

**Original**: 2026-04-17 (10/10 APPROVE, convergence 0.88 at round 3)
**Replay**:   2026-04-19 (10/10 APPROVE, convergence 0.86 at round 3)
**Divergence score**: 0.04 (below 0.15 noise threshold → no material disagreement)

## Round-by-round diff
| Round | Metric    | Original | Replay | Delta |
|-------|-----------|----------|--------|-------|
| 1     | novelty   | 0.78     | 0.76   | -0.02 |
| 1     | overlap   | 0.28     | 0.31   | +0.03 |
| 2     | convergence | 0.55   | 0.52   | -0.03 |
| 3     | convergence | 0.88   | 0.86   | -0.02 |

## Vote comparison
All 10 agents cast the same verdict (APPROVE). No agent changed position.

## Verdict
HOLD — replay is consistent with the original within the noise threshold.

Replay saved to: ${CLAUDE_PLUGIN_DATA}/sessions/fc777472/replays/2026-04-19T14-22-05Z.json
```

## Strict mode

With `--strict`, the command exits non-zero if:
- Final verdict differs
- Any agent changed its vote
- Divergence score exceeds 0.15
- Convergence fails to reach the mode's threshold (0.85 for consensus, 0.70 for fast, 0.90 for deep)

Strict mode is intended for CI — hooked into pre-release to catch deliberation-engine regressions.

## Notes

- Determinism is best-effort. Language models are stochastic; seeds and temperature reduce but do not eliminate variance.
- This command is the primary regression test for the deliberation engine — without it, prompt drift is invisible.
- Snapshot format is defined by `/session-snapshot` (Tier 4). If that contract changes, bump the snapshot schema version.
- Use `--compare-to` to A/B test prompt or agent changes: snapshot a baseline, change prompts, then replay the baseline against the new configuration.
