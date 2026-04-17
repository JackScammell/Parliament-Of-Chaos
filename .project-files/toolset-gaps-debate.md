# Toolset Gaps: Debate Outline and Tier Plan

**Source debate**: `/chaos:debate-topic "what is missing from this toolset?"` — session `fc777472-f0ef-4dea-81da-a98115d4c9ec` (2026-04-17)
**Mode**: consensus (5 rounds, balanced) / majority vote
**Outcome**: 10/10 APPROVE — consensus reached at round 3 (convergence 0.88 > 0.85 threshold)
**Status**: Planning — not yet on roadmap

---

## Executive Summary

The debate concluded that the loudest gap in the Parliament of Chaos toolset is **not missing features but orphaned features**. The `commands/` directory holds ~11 markdown files with no matching registered skill, while `grumpy-i18n-nitpicker` exists as an agent with no command to drive it. Before shipping anything new, the orphans must be reconciled.

Four tiers of work emerged. Tier 1 is gating: no new command ships until the manifest and reconciler exist.

---

## Agents Consulted

| Agent | Role | Lens |
|-------|------|------|
| system-architect | Orchestrator-advisory | Architectural gaps |
| senior-council | Chair (non-voting) | Synthesis |
| doc-bard | Specialist | Documentation & onboarding |
| test-prophet | Specialist | Testing strategy |
| observability-oracle | Specialist | Telemetry & monitoring |
| security-knight | Specialist | Security tooling |
| pipeline-engineer | Specialist | CI/CD & release |
| config-curator | Specialist | Configuration & env |
| grumpy-maintainability-curmudgeon | Reviewer | Long-term maintenance |
| grumpy-architecture-skeptic | Reviewer | Systemic design |
| grumpy-budget-hawk | Reviewer | Cost / scope |

---

## Round-by-Round Summary

### Round 1 — Opening Positions (divergent)

Each agent named the gap they saw most clearly:

- **system-architect** — No migration / resumability / state-sharing / rollback primitives across the plugin lifecycle.
- **doc-bard** — Docs tooling generates but does not audit; no ADR scaffolding; no `/explain-command` (asymmetry with `/explain-agent`).
- **test-prophet** — No deterministic debate replay; `generate-tests.md` and `mutation-test.md` exist but are not surfaced.
- **observability-oracle** — `activity.jsonl` is written but has no read path; no `/telemetry-query` or `/parliament-metrics`.
- **security-knight** — No `/threat-model`, `/sbom-generate`, `/secrets-rotate`, or `/permission-audit`.
- **pipeline-engineer** — `/cut-release.md` is orphaned; no `/release-notes-draft`, `/ci-watch`, `/bisect`, or `/hotfix`.
- **config-curator** — No `/settings-diff`, `/plugin-upgrade`, `/env-doctor`, or `/feature-flag-list`.
- **grumpy-maintainability-curmudgeon** — The fleet is too big already; orphans indicate stale surface; consolidation over addition.
- **grumpy-architecture-skeptic** — Parliament has no feedback loop — decisions never revisited, agents never benchmarked.
- **grumpy-budget-hawk** — No cost visibility, no soft-caps, no dry-run for expensive commands.

**Round 1 metrics**: novelty 0.78, overlap 0.28, convergence 0.22.

### Round 2 — Rebuttals (consolidation)

Overlapping positions began to merge:

- system-architect granted curmudgeon's point — but argued a `commands/manifest.yaml` registry is the true enabling primitive.
- doc-bard insisted `/adr-new` must precede `/decision-review` (can't review untyped decisions).
- test-prophet called deterministic replay a prerequisite for any release-notes automation.
- observability-oracle folded budget-hawk's `/cost-report` into their own `/telemetry-query` as a dependency chain.
- security-knight + config-curator merged `/permission-audit` and `/settings-diff` into one `/settings-audit`.
- pipeline-engineer offered `/session-snapshot` as a shared primitive for both resumability and release notes.
- grumpy-maintainability-curmudgeon demanded Tier-1 gating: no new command until 11 orphans are exposed or deleted.
- grumpy-architecture-skeptic backed the curmudgeon and proposed a **Skill-Manifest Reconciler** as the keystone command.
- grumpy-budget-hawk rejected `/hotfix` as a review-safety hazard; countered with `/fast-track` (minimum security+correctness floor).
- config-curator conceded the `/settings-audit` merge but kept `/env-doctor` as a distinct runtime-dir validator.

**Round 2 metrics**: novelty 0.45, overlap 0.58, convergence 0.55.

### Round 3 — Convergence

Priorities aligned cleanly around four tiers (below). Curmudgeon's conditional approval ("Tier 1 must be done FIRST") was accepted by all parties. Skeptic's addition of `/agent-usage-stats` was folded into Tier 2.

**Round 3 metrics**: novelty 0.15, overlap 0.82, convergence **0.88** — early-termination triggered.

---

## Final Vote

| Agent | Vote | Reasoning |
|---|---|---|
| system-architect | APPROVE | Manifest-first is the correct primitive |
| doc-bard | APPROVE | ADRs + /docs-audit closes the loop |
| test-prophet | APPROVE | /debate-replay unlocks regression testing |
| observability-oracle | APPROVE | Metrics bundle is coherent |
| security-knight | APPROVE | /settings-audit consolidates correctly |
| pipeline-engineer | APPROVE | /fast-track is safer than /hotfix |
| config-curator | APPROVE | /env-doctor preserved as distinct |
| grumpy-maintainability-curmudgeon | APPROVE (conditional) | Tier 1 FIRST |
| grumpy-architecture-skeptic | APPROVE | /agent-usage-stats included |
| grumpy-budget-hawk | APPROVE | Cost visibility in Tier 3 |

**Result**: 10/10 APPROVE (100%). Clears majority (>50%) and supermajority (≥66%) thresholds.

---

## Key Insights

1. **The loudest gap is orphaned features, not missing ones.** ~11 command markdown files exist but are not surfaced as registered skills. `grumpy-i18n-nitpicker` has no driver command.
2. **Parliament has no feedback loop.** No ADRs, no decision-review, no debate replay, no agent-usage stats.
3. **Observability is write-only.** `activity.jsonl` has no read path.
4. **Cost controls are absent.** `/parliament-review` runs 9 reviewers with no floor or dry-run.
5. **Documented release/migration footguns are untooled.** `feedback_release_process.md` and `feedback_hooks_location.md` describe known pain with no preventive command.

---

## Trade-offs Accepted

- Adding 18 commands contradicts the maintainability concern → **resolved via Tier-1 gating**.
- Manifest-first adds ceremony → **accepted to prevent ongoing drift**.
- `/fast-track` over `/hotfix` → **safety preferred over speed** (security > convenience per governance).
- `/debate-replay` requires snapshot infrastructure → **accepted; unlocks regression testing**.

**Rejected / Deferred**:
- `/hotfix` — rejected (bypasses review safety)
- `/bisect` — deferred (out of plugin scope)
- `/sbom-generate` — deferred (partially covered by `/security-scan` + `dependency-detective`)

---

# Tier Plan

The tiers form a strict dependency order: each tier depends on the previous. Tier 1 is a hard gate.

---

## Tier 1 — Hygiene (blocking gate)

**Theme**: Reconcile existing surface before shipping anything new.
**Gate**: No Tier 2-4 work begins until Tier 1 is complete and all orphans have an explicit decision.

| # | Item | Type | Depends on | Notes |
|---|------|------|------------|-------|
| 1.1 | `commands/manifest.yaml` | New artifact | — | Declarative registry: name, status (active/deprecated/experimental/orphaned), owner agent, skill-surface flag |
| 1.2 | `/parliament-doctor` | New command | 1.1 | Reconciles manifest against `commands/*.md` and registered skills; reports orphans and ghosts |
| 1.3 | Orphan triage | Decision batch | 1.2 | For each orphan: expose, delete, or mark experimental |
| 1.4 | `grumpy-i18n-nitpicker` resolution | Decision | — | Retire the agent OR add `/i18n-audit` to drive it |

**Known orphan candidates** (from debate; verify with `/parliament-doctor`):
`analyse-queries.md`, `coverage-audit.md`, `cut-release.md`, `generate-tests.md`, `git-workflow.md`, `incident.md`, `infra-review.md`, `mutation-test.md`, `retro.md`, `scaffold.md`, `test-health.md`, `track-debt.md`.

**Exit criteria**: Zero drift between manifest, `commands/*.md`, and registered skills.

---

## Tier 2 — Learning Loop

**Theme**: Give Parliament a feedback loop so it can improve itself.
**Depends on**: Tier 1 complete.

| # | Item | Type | Depends on | Notes |
|---|------|------|------------|-------|
| 2.1 | `/adr-new` | New command | Tier 1 | Scaffolds an architectural decision record |
| 2.2 | `/adr-supersede` | New command | 2.1 | Marks an ADR superseded and links the replacement |
| 2.3 | `/decision-review` | New command | 2.1 | Re-evaluates prior council/debate rulings when context changes |
| 2.4 | `/debate-replay` | New command | 4.1 (snapshot) | Deterministic replay of past debate from snapshot; regression-tests the deliberation engine |
| 2.5 | `/agent-usage-stats` | New command | Tier 1 | Frequency & effectiveness per agent; input to retirement decisions |

**Exit criteria**: Closed loop — decisions have typed records, past debates replay deterministically, underused agents can be identified with data.

---

## Tier 3 — Observability & Cost

**Theme**: Turn write-only telemetry into queryable, budget-aware signal.
**Depends on**: Tier 1 complete. `/debate-replay` (2.4) recommended but not required.

| # | Item | Type | Depends on | Notes |
|---|------|------|------------|-------|
| 3.1 | `/telemetry-query` | New command | Tier 1 | Ad-hoc query over `activity.jsonl` and plugin data directory |
| 3.2 | `/parliament-metrics` | New command | 3.1 | Dashboard: token attribution per agent, session cost, SLO status for background monitors, trend analysis |
| 3.3 | `/cost-report` + soft-caps | New command + wrapper | 3.1 | Dry-run mode + soft-cap warnings on expensive commands (`/summon-council`, `/parliament-review`, deep debates) |

**Exit criteria**: Cost of any command or session is knowable before and after execution. Background monitors have observable health.

---

## Tier 4 — Ops & Lifecycle

**Theme**: Tool the known footguns (release sync, hook location, session recovery, doc staleness).
**Depends on**: Tier 1 complete.

| # | Item | Type | Depends on | Notes |
|---|------|------|------------|-------|
| 4.1 | `/session-snapshot` + resume | New command + primitive | Tier 1 | Checkpoint/replay for crashed council runs; also used by 2.4 |
| 4.2 | `/docs-audit` | New command | Tier 1 | Detects stale/fabricated docs after code changes (symmetric to `/onboard-codebase`) |
| 4.3 | `/settings-audit` | New command | Tier 1 | Permissions + scope-diff + secret leakage + feature-flag inventory (merged from four proposals) |
| 4.4 | `/env-doctor` | New command | Tier 1 | Validates `${CLAUDE_PLUGIN_DATA}` resolution, fallback dir, hook script locations (per `feedback_hooks_location.md`) |
| 4.5 | `/fast-track` | New command | Tier 1 | Minimum-review-floor bypass (security + correctness only); replaces rejected `/hotfix` |
| 4.6 | `/release-notes-draft` | New command | Tier 1, 4.1 recommended | Auto-generates CHANGELOG entries from merged PRs |
| 4.7 | `/ci-watch` | New command | Tier 1 | Polls CI and surfaces status inside Claude |
| 4.8 | `/plugin-upgrade` | New command | Tier 1 | Version-sync migration helper addressing `feedback_release_process.md` |
| 4.9 | `/i18n-audit` | New command | 1.4 (only if kept) | Drives `grumpy-i18n-nitpicker` — skip if the reviewer is retired in 1.4 |

**Exit criteria**: All three user-memory footguns (release sync, hook location, session crash) have preventive tooling. Retired commands have a deprecation path.

---

## Proposed Roadmap Mapping

If adopted, these tiers map naturally onto roadmap phases. Suggested naming:

| Roadmap phase | Tier | Why |
|---|------|-----|
| **Phase 5: Toolset Hygiene** | Tier 1 | Blocking gate; self-contained |
| **Phase 6: Feedback Loop** | Tier 2 | Unlocks learning from past work |
| **Phase 7: Observability & Cost** | Tier 3 | Independent value once Tier 1 is done |
| **Phase 8: Ops & Lifecycle** | Tier 4 | Largest tier; can be sliced by sub-theme |

Target version window: v1.10.0 (Tier 1) → v1.13.0 (Tier 4 complete). Exact versioning to be set during `/roadmap-add-item` for each tier.

---

## Next Actions

1. **Run `/parliament-doctor` prerequisites first** — cannot currently run because it does not exist; but a manual audit can confirm the 11 orphan files in `commands/`.
2. **`/roadmap-add-item`** — add Tier 1 as a new roadmap phase (recommend: "Phase 5: Toolset Hygiene").
3. **`/roadmap-item-scope`** — design pass on items 1.1 (`manifest.yaml` shape) and 1.2 (`/parliament-doctor` behaviour).
4. **Governance decision on `grumpy-i18n-nitpicker`** before scoping 4.9.

---

## References

- Source debate transcript: session `fc777472-f0ef-4dea-81da-a98115d4c9ec` (2026-04-17)
- Related roadmap: `/Users/jack/Parliament-Of-Chaos/.project-files/Roadmap.md`
- Governance: `/Users/jack/Parliament-Of-Chaos/.claude/rules/governance.md` (conflict-resolution priority used to reject `/hotfix`)
- Release-sync footgun: `/Users/jack/.claude/projects/-Users-jack-Parliament-Of-Chaos/memory/feedback_release_process.md`
- Hook-location footgun: `/Users/jack/.claude/projects/-Users-jack-Parliament-Of-Chaos/memory/feedback_hooks_location.md`
