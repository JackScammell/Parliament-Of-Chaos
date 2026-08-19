---
description: Re-evaluate a prior ADR, debate, or council ruling when context has changed
effort: medium
argument-hint: "<target> [--trigger <text>] [--mode fast|consensus|deep]"
---

# Decision Review

Revisit a past decision — an ADR, a `/debate-topic` outcome, or a `/summon-council` ruling — when the assumptions behind it may no longer hold. Produces a verdict: **hold** (decision still stands), **amend** (decision needs modification), or **supersede** (decision should be replaced with a new one).

This command is the missing "feedback loop" identified in the toolset-gaps debate. Without it, Parliament makes decisions but never revisits them.

## Usage

```
/decision-review <target> [--trigger <text>] [--mode fast|consensus|deep]
```

Target forms:
- `adr:NNNN` — a specific ADR number
- `debate:<session-id>` — a past debate session
- `council:<session-id>` — a past council run
- `path:<file>` — any markdown artefact carrying a decision record

**Examples**:
```
/decision-review adr:0007
/decision-review debate:fc777472 --trigger "new Claude Code hook event"
/decision-review adr:0003 --mode deep
```

## Options

- `<target>` (required): What to re-evaluate. See forms above.
- `--trigger <text>` (optional): Why are we reviewing now? Captures the context shift (new feature, incident, metric change, upstream breakage). If omitted, the review is framed as a routine health check.
- `--mode` (optional): Deliberation depth — `fast` (default, 3 rounds), `consensus` (5 rounds), `deep` (7–10 rounds).

## Process

1. **Load the original decision**
   - For `adr:` — read `.project-files/adrs/NNNN-*.md`
   - For `debate:` or `council:` — read the transcript from `${CLAUDE_PLUGIN_DATA}/` or `.project-files/`
   - For `path:` — read the specified file
2. **Extract invariants** — identify the load-bearing assumptions, constraints, and trade-offs that justified the original decision.
3. **Probe current state** — check each invariant against present reality. Read `CHANGELOG.md`, recent ADRs (for supersession chains), and `/parliament-metrics` if available.
4. **Delegate to `deliberation-conductor`** — run a structured debate with the agents listed in the original decision (plus `grumpy-architecture-skeptic` as a standing challenger). Framing question: *"Given the trigger, does this decision still hold?"*
5. **Produce a verdict** — one of:
   - **Hold**: invariants intact; record the review in the ADR as `Last reviewed: YYYY-MM-DD`.
   - **Amend**: invariants partially shifted; produce an amended ADR (new revision of the same number is not allowed — file becomes a new ADR that `Supersedes: NNNN-partial`).
   - **Supersede**: invariants broken; scaffold the replacement with `/adr-new --supersedes NNNN`.
6. **Record the review** — append a `## Reviews` section to the original ADR with date, trigger, verdict, and link to the deliberation output.

## Output

```
# Decision Review — adr:0007

**Title**: Adopt hardcoded command list for /list-commands
**Original date**: 2025-09-14
**Trigger**: toolset-gaps debate identified 11 orphaned commands

## Invariants checked
| Invariant | Original | Current | Drift |
|-----------|----------|---------|-------|
| Command count ≤ 20 | yes | no (46) | broken |
| Categories fit on one screen | yes | no | broken |
| Low maintenance burden | yes | drift observed | partial |

## Deliberation
Conducted with system-architect, config-curator, grumpy-maintainability-curmudgeon.
Convergence: 0.91 at round 3. See ${CLAUDE_PLUGIN_DATA}/decisions/reviews/2026-04-17-adr-0007.md

## Verdict
SUPERSEDE — the hardcoded-list invariant is broken. Proposed replacement: manifest-driven listing (see ADR-0012).

## Follow-up actions
- /adr-new "Manifest-driven command listing" --supersedes 0007
- Update /list-commands to read commands/manifest.yaml
```

## Notes

- This command is **not** a destructive edit. It never rewrites the original decision — it either ratifies it or scaffolds a successor via `/adr-new`.
- Verdicts are advisory in `proposed` state until a human or `/summon-council` accepts them.
- Pair with `/parliament-loop 1mo /decision-review adr:0003` for recurring health checks of load-bearing decisions.
- Deliberation outputs are archived under `${CLAUDE_PLUGIN_DATA}/decisions/reviews/` for audit.
