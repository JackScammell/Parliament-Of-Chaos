# Parliament of Chaos Council Fan-Out Policy

This file is the **single source** for the council fan-out policy. `senior-council.md`,
`parliament-review.md`, and `summon-council.md` **reference** this file — they must not copy
its rules inline. Amend the policy here and the referencing agents/commands inherit the change.

## The fan-out policy loop (reconcile-after-return, NOT a timer-driven state machine)

An LLM orchestrator sitting in a blocking turn has **no clock and no mid-flight watchdog**.
It cannot poll, sleep, or wake itself while a fan-out is in flight. So the policy specifies
only what the orchestrator can actually do — act *before* dispatch and *after* return:

1. **Before dispatch** — enumerate the intended member set; run **ONE** cost estimate on that
   set; if it is over the soft cap, surface floor-preserving trim options (warn / confirm,
   **never** hard-block).
2. **Dispatch** respecting the concurrency cap (see Batching).
3. **After the fan-out returns** — reconcile *returned* vs *expected*. Any expected member with
   no verdict is **non-reporting**.
4. **Re-dispatch** each non-reporting member **ONCE**, then stop.
5. **Synthesize** from the survivors, subject to the floor (below).

State it plainly: there are **NO mid-flight wall-clock deadlines** in this loop — there is no
clock to honour them. True mid-flight hang-detection is the **out-of-band watchdog** (B4,
below), which is a separate, interactive mechanism — not part of this blocking loop.

## The floor as a LIVENESS guarantee (security-critical)

Floor members are `grumpy-security-nag` + `grumpy-code-reviewer` (+ `grumpy-privacy-paranoid`
when PII is present). They are **tagged as floor** in the enumerated member set.

A floor member may **NEVER** be dropped — not by relevance-tiering, not by budget-trim, not by
non-reporting degradation. If a floor member is still non-reporting after its one re-dispatch,
the run does **NOT** synthesise a verdict from the survivors. It returns **`INCOMPLETE`** — a
non-blocking terminal state meaning "security/correctness did not run" — and **never** a false
`APPROVE`.

"Queued → do not re-spawn" is a **SECURITY INVARIANT**, not merely a cost optimisation: a floor
member that is only *waiting behind the concurrency cap* must be **waited for**, never dropped
and never double-dispatched.

## Detection table (post-return, from queryable `activity.jsonl` signals)

| Signal state | Verdict | Action |
| --- | --- | --- |
| Returned a verdict | Done | tally |
| SubagentStart seen, no verdict, StopFailure logged | Failed | re-dispatch once |
| TaskCreated but no SubagentStart (queued behind cap) | Queued | wait — never re-spawn (security invariant for floor members) |
| SubagentStart seen, no verdict, no StopFailure | Non-reporting | re-dispatch once, then INCOMPLETE if floor / drop-with-notice if non-floor |

> The "Returned a verdict" → Done and the Done/Failed distinctions require the **`TaskCompleted`**
> hook event to be written to `activity.jsonl` (emitted with `type: "task_completed"`).
> `log_event.sh` writes it and `settings.json` wires it — shipped as of v1.23.0. Two caveats:
>
> 1. On a Claude Code build old enough that the `TaskCompleted` hook is not fired, Failed vs
>    Non-reporting cannot be cleanly disambiguated from signals alone.
> 2. **Event-provenance uncertainty (v2.1.233)**: it is *not documented* whether
>    `TaskCreated`/`TaskCompleted` fire from the subagent `Task`-dispatch lifecycle or from the
>    task-list (Todo) tool system. v2.1.233 removed the Todo tools by default on newer models
>    (`CLAUDE_CODE_ENABLE_TODO_TOOLS=1` restores them) — if the events are tool-tied, they go
>    dark there and the Done/Failed and Queued rows degrade silently. `/env-doctor` probes for
>    exactly this signature (`subagent_start` records present with zero `task_completed`
>    siblings) and warns.
>
> **Fallback semantics (robust by design, with one documented sacrifice):** if these signals
> are absent for any reason, a member with no verdict collapses into **Non-reporting** → one
> re-dispatch → `INCOMPLETE` if floor. Degraded telemetry loses disambiguation *quality* (and
> the B4 breaker's Failed counting), but the security-critical liveness floor — never a false
> `APPROVE` — holds without them.
>
> The sacrifice: with `TaskCreated` dark, a member that is merely **queued** behind the
> concurrency cap is indistinguishable from Non-reporting, so the fallback can **re-dispatch a
> queued floor member** — a double-dispatch this policy otherwise forbids as a security
> invariant, risking two live instances returning conflicting verdicts. Mitigation: when
> `/env-doctor` has WARNed on the dark-telemetry asymmetry signature **and** the dispatched set
> exceeded the live concurrency cap, the orchestrator must **confirm with the user before
> re-dispatching any floor member** (the only state in which queued-vs-non-reporting is
> ambiguous). If two instances of a floor member do return verdicts, tally the more severe one.

## Concurrency-aware batching (B1)

There is **no fixed batch-width constant**. The effective width is the live concurrency cap,
`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (default **20**); the selected-set size is variable
(relevance-tiering changes it per run, 2–9 for the reviewer panel). Rule: dispatch the whole
selected set at once, and only engage batching **when the selected-set size exceeds the live
cap** — that is the sole case where members would otherwise queue and appear hung. Do **NOT**
serialise a sub-cap panel into waves by default; that adds latency to fix a problem that does not
exist below the cap. `/env-doctor` cross-checks this by warning when the live cap is **below the
selected-set size it would dispatch**, not against any hard-coded number.

> **Prefix-stagger (v2.1.234, harness-automatic)**: identical-prefix parallel dispatches are
> staggered by the harness for prompt-cache reuse. This shifts `SubagentStart` timestamps within
> a wave — do not read small start-time gaps between members of one dispatch as queueing; the
> Queued verdict comes from the *absence* of `SubagentStart`, not from start-time spread.

## Graceful degradation (B2)

On post-return non-reporting:

1. Re-dispatch the member **once**.
2. If still non-reporting and the member is **non-floor**: **drop** it, with a loud notice in
   Reviewer Notes / Deferred.
3. If still non-reporting and the member is **floor**: force **`INCOMPLETE`** (never synthesise
   an APPROVE without it).

## Prompt-standards rule (B5)

Council members must **STATE ASSUMPTIONS AND PROCEED** — they must **never** ask clarifying
questions in a detached fan-out context. A member blocked waiting on input looks
indistinguishable from a hung member and cannot be recovered by the orchestrator.

## Out-of-band watchdog for true hang-recovery (B4) — committed

This is the **only** mechanism that can recover a genuine mid-flight hang. The orchestrator
cannot watch itself while blocked, so hang-recovery is done **out-of-band**:

- The harness `Monitor` tool tails `activity.jsonl` out-of-band while the fan-out runs.
- **Circuit-breaker threshold (authoritative):** a per-member breaker **OPENs** when the member
  is `Failed` or `Non-reporting` on **≥ 2 of its last 3 dispatches**; it **closes** again after
  one clean `Done`. (This is the single source for the threshold — `/parliament-metrics` reports
  breaker state against it and must not invent its own cutoff.)
- **Orchestrator action on an OPEN breaker:** on the *next* run, **skip** the chronically-failing
  member rather than re-dispatching it, and surface the skip in Reviewer Notes / Deferred — with
  the floor caveat below. This is a cross-run decision (distinct from the single within-run
  re-dispatch of the reconcile loop), and it is owned here, not in the observability surface.
- **Floor override:** a breaker on a **floor** member never causes a silent skip — skipping a
  floor member forces **`INCOMPLETE`**, exactly as non-reporting does.
- Breaker state is surfaced (read-only) in `/parliament-metrics`.

It depends on the **`TaskCompleted`** telemetry event (shipped in v1.23.0; see the detection
table caveat). This is the committed procedure for true hang-recovery, and it is an
**interactive-session pattern** — it relies on an out-of-band monitor running alongside the
session, not on anything the blocked orchestrator turn can do by itself.

## Parallel fan-out version floor

Non-cascading parallel fan-out (a failing sibling `Task` call no longer cancels its parallel
peers) requires **Claude Code ≥ v2.1.128**. This is the single source for that floor; the
orchestrator command Notes and `/env-doctor` reference it here rather than restating the version.
