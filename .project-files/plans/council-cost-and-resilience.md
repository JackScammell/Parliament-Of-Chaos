# Plan: Council Cost Control & Member Fault-Tolerance

**Status:** Final v2 — Round 1 grumpy review incorporated; three trade-offs ruled on by the user (see "Decisions locked" and the Trade-offs section).
**Date:** 2026-07-24

## Decisions locked (user, 2026-07-24)

1. **No hard budget cap.** Warn/confirm only. **A5 (opt-in ceiling) is dropped.**
2. **Downgrade the 5 advisory reviewers' model now**, measure quality after. **A1 proceeds as written.**
3. **Commit to B4** (out-of-band watchdog for true mid-flight hang-recovery). It is promoted from "Phase 4, only if needed" to committed scope; **P1 (`TaskCompleted` telemetry) becomes a hard, non-optional prerequisite.**
**Trigger:** User reports (A) council reviews exhaust the usage window and block further work, and (B) council members sometimes hang/fail and must be re-spawned by hand.
**Mode:** Plan only — no implementation in this pass.

---

## What changed from v1 (why you're reading a rewrite)

Five plan-mode reviewers rejected v1. Their findings were convergent and, where they made factual claims, **verified against the codebase** before acting on them:

- **v1 over-sold the scope.** It framed the whole thing as a low-risk "wiring job" composing three existing halves. Verification (`grep`) confirmed two of the three do **not** exist in shipped code: `active_council` is `null` with no writer (`session-snapshot.md:87`), and `TaskCompleted` is **not** written to `activity.jsonl` (routes only to `notify_teams.sh`; absent from `log_event.sh`'s case statement). Part A (cost) genuinely *is* mostly reuse; **Part B (reliability) is mostly net-new engineering** and is now labelled as such.
- **v1 specified a state machine that the substrate can't run.** A `pending→running→terminal` lifecycle *with wall-clock deadlines and mid-flight watchdog checks* was placed in markdown prose interpreted by an LLM. But `Task()` fan-out is **blocking** from the orchestrator's view — there is no clock and no supervisory loop running *while it's blocked on synthesis*. The ledger is demoted from a **timer-driven state machine** to a **reconcile-after-return policy loop** (detect non-return *after* the batch resolves, not mid-flight).
- **v1's sequencing was backwards for the stated pain.** It led with cost *visibility* (which reduces zero tokens) and buried the actual token-*reducers*. Part A is reordered by dollar-per-effort.
- **v1 had a silent security hole.** The "floor never waives" guarantee held for up-front selection but **failed** on timeout-driven degradation: a hung `grumpy-security-nag` could fall through to a survivor-synthesised `APPROVE` with security absent. The floor is now a **liveness** guarantee, not just a selection guarantee.
- **v1 duplicated a correctness invariant across three prose files.** Single-sourced into one rule file (below).

---

## Problem Statement

- **(A) Cost hunger.** `/parliament-review` and `/summon-council implement` fan out to all 9 grumpy reviewers unconditionally, each dispatched cold on the whole target. A run projects ~590K–960K tokens ($2.66–$4.36 per `/cost-report`'s registry). Enough runs exhaust the window and block work.
- **(B) Hangs/failures.** A council member (`Task` subagent) can hang or fail with no recovery; the orchestrator blocks on synthesis, so one non-returning member stalls the review and the user re-spawns by hand.

Both problems live at the **orchestrator's fan-out boundary** — the seam where it decides *which* members to spawn (cost = admission control) and *how* to handle each outcome (reliability = completion control). That shared seam is a genuine and useful framing. What v1 got wrong was implying the seam is already instrumented; it is not.

## Guiding Constraints (non-negotiable)

1. **Governance priority:** security > correctness > maintainability > performance > convenience. No shortcut drops the security or correctness axis — including on *timeout*, not just on selection.
2. **No hard blocks by default.** A hard budget cap was rejected by governance (`cost-report.md:177`). Budget gates are **warn/confirm**. (An *opt-in, user-owned* ceiling is offered as a documented option — see A5 — which is the user exercising their own final word, not Parliament imposing policy.)
3. **No-policy stance.** Parliament ships no `permissions` and no `CLAUDE_CODE_MAX_*` env vars in `settings.json`. Reliability env vars reach the user by guidance only.
4. **Extend where genuine; build where honest.** Part A extends existing commands. Part B requires **net-new** telemetry writers and (for real recovery) an out-of-band watchdog — stated plainly, not disguised as wiring.

---

## The fan-out policy loop (demoted from v1's "ledger state machine")

Specify only what an LLM orchestrator in a blocking turn can actually do:

1. **Before dispatch** — enumerate the intended member set; run **one** cost estimate on that set; if over the soft cap, surface floor-preserving trim options (warn/confirm).
2. **Dispatch** the set (respecting the concurrency cap — see B1).
3. **After the fan-out returns** — reconcile *returned* vs *expected*. Any expected member that did not return a verdict is **non-reporting**.
4. **Re-dispatch each non-reporting member once**, then stop retrying.
5. **Synthesize from survivors, subject to the floor** (below).

There are **no mid-flight wall-clock deadlines** in this loop — that language is removed because there is no clock to honour it. True *mid-flight* hang-detection requires the out-of-band watchdog in B4, which is explicitly net-new. Everything before B4 reduces **queueing/starvation and post-return non-reporting**, not live hangs — an honest limit, stated up front.

**Single-sourced.** This loop and the floor rule live in **one** new file, `.claude/rules/fan-out-policy.md`, and are *referenced* (not copy-pasted) from `agents/senior-council.md`, `commands/parliament-review.md`, and `commands/summon-council.md`, so the invariant can't diverge across three files.

### The floor as a *liveness* guarantee (security fix)
- Floor members — `grumpy-security-nag` + `grumpy-code-reviewer` (+ `grumpy-privacy-paranoid` on PII) — are **tagged as floor** in the enumerated set.
- A floor member may **never** be dropped by relevance-tiering (A2) **or** budget-trim (A4) **or** non-reporting degradation.
- If a floor member is non-reporting after its one re-dispatch, the run does **not** synthesise a verdict from survivors. It returns **`INCOMPLETE`** — a non-blocking terminal state that tells the user "security/correctness did not run," never a false `APPROVE`. This is the exact gap v1 left open.
- **"Queued → do not re-spawn" is a security invariant, not a cost optimisation:** a floor member merely waiting behind the concurrency cap must be waited for, never dropped or double-dispatched.

---

## Part A — Cost Control (mostly genuine reuse; reordered by dollar-per-effort)

### A1 — Effort/model audit of the review path *(config-only, highest saving-per-effort; do first)*
- **Model:** all `grumpy-*` are `model: inherit`, so an Opus session runs 9 Opus reviewers. Downgrade the **5 advisory** reviewers (performance, accessibility, docs, i18n, budget) to a cheaper tier — a ~5× per-token cut on ~half the panel that **stacks** with every other item. **Never** the floor (security, code). Per budget-hawk: this is a *reversible price cut*, so measure the **quality** delta *after* via `/parliament-metrics --by-effort` (revert = one frontmatter line), rather than gating on a *before* benchmark. Requires a documented deviation from `agent-standards.md`'s `model: inherit` default — surfaced through `/parliament-optimize`.
- **Effort:** audit what effort tier the fan-out inherits (`senior-council` is `high` = 1.55× vs `low` = 0.55×, an ~2.8× swing that multiplies across members). Document the minimum that preserves verdict quality.

### A2 — Relevance-tiered reviewer selection as the default *(pure policy; member elimination = dominant cost driver)*
Run only reviewers whose domain the diff touches, reusing `fast-track.md`'s existing detection heuristics. `/parliament-review --all` forces the full 9 ("maximum scrutiny" becomes a deliberate opt-in, matching the command's own description). Floor always present (see liveness rule). Skipped reviewers logged to Deferred, as `fast-track` does. This is the cleanest win — it removes whole members, not just their input tokens.

### A3 — Shared inventory/diff pass *(reduces input duplication; do not over-claim)*
Add one shared `Explore`/diff pass (mirroring `senior-council`'s existing discovery) and hand the scoped changeset to each reviewer. **Honest scope of the saving** (per performance-troll): 9× is a *ceiling*, not the measured duplication, and this trims only **input** tokens — the 9 independent *reasoning* passes remain. So it is a real but *bounded* input-side saving, **not** "the biggest reduction" as v1 claimed (A1's model downgrade and A2's member elimination are larger). Default scope = diff + touched-file neighbourhood + inventory (not raw diff — architecture/maintainability reviewers need surrounding context).

### A4 — Pre-flight cost gate *(visibility; deliberately last, with corrections)*
Wire `/cost-report`'s existing soft-cap band into the review path as a warn/confirm gate.
- **Ordering fix (H3):** this comes *after* A2/A3, because those change the cost structure and would leave a telemetry-sourced estimate systematically wrong until history re-accumulates. Until then the gate's estimate is marked **provisional**.
- **Interface honesty (H2):** `/cost-report estimate` is a *whole-command static estimator*, not a per-subset admission controller. Either (a) keep A4 as a pre-flight **whole-run** gate (what the tool actually does — recommended), or (b) add a new per-subset estimate entry point to `/cost-report` as explicit net-new work. Do **not** claim boundary-level batch admission from the existing tool.
- **Small-review skip (performance):** A3 and A4 are fixed overhead; skip both below a size threshold so small reviews don't go net-negative.

### A5 — ~~Opt-in, user-owned session ceiling~~ *(DROPPED per user decision)*
Considered and declined: user ruled warn/confirm is sufficient and does not want a hard ceiling, even an opt-in one. Left here for the record; not implemented.

### A6 — Repeat-run reuse *(attacks the actual failure mode: repeated runs)*
Your pain is *repeated* runs exhausting a window. Add: (a) prompt-cache the shared A3 inventory/diff; (b) skip files unchanged since the last review of the same target. This is the only lever aimed at *cross-run* cost, not just within-run.

---

## Part B — Member Fault-Tolerance (mostly NET-NEW; scoped honestly)

**Prerequisites (net-new, not "free").** Before any recovery logic can read member state, two telemetry gaps must be closed — both verified absent today:
- **P1:** add a `TaskCompleted` case to `log_event.sh` so completion is written to `activity.jsonl` (today it goes only to `notify_teams.sh`).
- **P2:** add an `active_council` **writer** (the field is `null` with no producer) if member-by-member resume (B3) is wanted.

Without P1/P2, the detection table below cannot be evaluated and B3/B4 are dead. They are prerequisite work items, not config tweaks.

### Detection (post-return, not mid-flight)
After the batch resolves, classify each expected member from queryable signals:

| Signal state | Verdict | Action |
|---|---|---|
| Returned a verdict | **Done** | tally |
| `SubagentStart` seen, no verdict, `StopFailure` logged | **Failed** | re-dispatch once |
| `TaskCreated` but no `SubagentStart` (queued behind cap) | **Queued** | wait — never re-spawn (security invariant for floor members) |
| `SubagentStart` seen, no verdict, no `StopFailure` | **Non-reporting** | re-dispatch once, then INCOMPLETE if floor / drop-with-notice if non-floor |

(Requires P1 for the "returned a verdict" column to be telemetry-visible rather than inferred from the orchestrator's own turn.)

### B1 — Concurrency-aware batching *(policy; corrected)*
Cap self-fan-out to avoid queue-starvation. **Correction (performance-troll):** cap at the **selected-set size**, and only engage batching **above** the concurrency cap — don't serialise a 9-grump panel into two waves by default (that adds latency to fix a problem that isn't present below the cap). Batch width is an in-prompt constant **cross-checked by `/env-doctor`** against the live `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` so the two can't silently diverge (M6).

### B2 — Graceful degradation with the liveness floor *(policy)*
On post-return non-reporting: re-dispatch once; then drop **non-floor** members with a loud notice in Reviewer Notes/Deferred; **floor** members that stay non-reporting force **`INCOMPLETE`** (never survivor-`APPROVE`). This is B2 done safely per the security fix above.

### B3 — Member-by-member resume *(net-new; needs P2)*
Persist the enumerated set + verdicts into `active_council` so a crashed/compacted council resumes from surviving verdicts. Net-new writer (P2), not "free."

### B4 — Out-of-band watchdog for *true* hang-recovery *(COMMITTED per user decision; net-new)*
**This is the only thing that actually recovers a mid-flight hang** — the user's literal complaint, and they have committed to building it. It requires the harness `Monitor` tool tailing `activity.jsonl` out-of-band (the orchestrator can't watch itself while blocked), opening a per-member circuit breaker after repeated failures, surfaced in `/parliament-metrics`. It is an interactive-session pattern and net-new. **Dependency:** hard-requires **P1** (`TaskCompleted` in telemetry) so the watchdog can distinguish "completed" from "still running" while tailing the log. B1/B2 remain the cheap first layer (queueing + post-return non-reporting); B4 is the layer that closes the actual mid-flight-hang gap.

### Config exposure (no-policy compliant)
`/env-doctor` reports whether `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` is set, warns if `< 9` (serialises the panel), confirms Claude Code ≥ v2.1.128. `/settings-audit` offers a confirmation-gated opt-in `env` snippet for the user's own file. Document in `agent-standards.md` that Claude Code offers no per-subagent timeout and no auto-retry — so B3/B4 are genuine engineering, not config.

### B5 — Prompt-standards rule
Council members must **state assumptions and proceed**, never ask clarifying questions in a detached fan-out context (a member blocked on input looks hung and can't be recovered by any of the above). This is a correctness requirement — it goes in the reviewer/specialist prompt standards, not buried as a footnote.

---

## Recommended sequencing

**Phase 1 — cheap, safe, high-saving (ship together):**
- A1 (effort/model audit), A2 (relevance-tiering default) — the two biggest cost reducers, pure config/policy.
- B1 (batching, corrected) + B2 (degradation with liveness floor) — pure policy; single-sourced into `.claude/rules/fan-out-policy.md`.
- B5 (prompt-standards rule).

**Phase 2 — real reductions & recovery groundwork:**
- A3 (shared context, with small-review skip), A6 (repeat-run reuse). *(A5 dropped.)*
- **P1 (`TaskCompleted` telemetry) — now a committed prerequisite, since B4 depends on it.**

**Phase 3 — visibility & durability (after structure settles):**
- A4 (pre-flight gate, provisional estimate), P2 (`active_council` writer) + B3 (resume).

**Phase 4 — true hang-recovery (COMMITTED, not conditional):**
- B4 (Monitor watchdog + circuit breaker) — the honest home of "stop members hanging on me." Depends on P1. Sequenced last only because it needs P1's telemetry in place; it is in scope regardless of whether Phases 1–3 leave residual hangs.

---

## Trade-offs — ruled on by user (2026-07-24)

1. **Hard cap vs warn/confirm** → **warn/confirm.** No hard cap, not even opt-in. A5 dropped.
2. **Model downgrade risk (A1)** → **downgrade now, measure after.** The 5 advisory reviewers move to a cheaper model immediately; security/code floor stays strong; quality delta checked via `/parliament-metrics --by-effort` post-hoc; revert = one frontmatter line.
3. **Depth of hang-recovery** → **commit to B4.** The user wants the actual mid-flight hang stopped, so the out-of-band watchdog is in scope (Phase 4), with P1 as its committed prerequisite.

## Explicit non-goals / honest limits

- No hard cap *by default* (A5 is opt-in only).
- Phases 1–2 do not recover a genuinely hung member — only B4 does.
- A3 trims input tokens only, not the 9 reasoning passes; its saving is bounded, not headline.
- Advisory soft caps warn, they don't stop spend.

## Files touched (when implemented)

New: `.claude/rules/fan-out-policy.md` (single-sourced loop + floor).
Core: `agents/senior-council.md`, `commands/parliament-review.md`, `commands/summon-council.md` (reference the rule).
Cost: `agents/grumpy-*.md` (A1 model/effort), `commands/parliament-optimize.md`, `commands/cost-report.md` (A4).
Reliability: `src/hooks/log_event.sh` (P1), `commands/session-snapshot.md` (P2/B3), `commands/env-doctor.md` (B1 cross-check), `commands/parliament-metrics.md` (B4), `.claude/rules/agent-standards.md` (documented gaps).
