# Parliament of Chaos Council Fan-Out Policy

This file is the **single source** for the council fan-out policy. `senior-council.md`,
`parliament-review.md`, and `summon-council.md` **reference** this file — they must not copy
its rules inline. Amend the policy here and the referencing agents/commands inherit the change.

## The fan-out policy loop (reconcile-on-notification — dispatch is DETACHED)

**Dispatch is background-by-default** (upstream since v2.1.198): a `Task(...)` call returns
immediately and the member runs detached. The harness then **re-invokes the orchestrator with a
completion notification** as each member finishes. Two consequences the loop is built on:

- The orchestrator **never blocks on the fan-out** — there is no "after the fan-out returns"
  moment. Reconciliation happens **per notification**, not once at the end.
- A member that has not yet delivered a verdict while its task is still live is **Working** —
  not non-reporting, not hung, not failed. **Silence during a live run is not a signal.**

The loop:

1. **Before dispatch** — enumerate the intended member set (floor members tagged); verify every
   file/path named in each dispatch prompt **against disk** (B7); run **ONE** cost estimate on
   the set; if over the soft cap, surface floor-preserving trim options (warn / confirm,
   **never** hard-block).
2. **Dispatch** the whole selected set at once, respecting the concurrency cap (see Batching).
3. **Wait and tally** — process each completion notification as it arrives, recording the
   member's explicit verdict (B6). The orchestrator **must not end the review or emit any
   terminal result while any member's task is still live.** If the orchestrator's own turn ends
   mid-fan-out, the next notification re-opens it — resume tallying; do **not** restart or
   duplicate the run.
4. **Reconcile per terminal state** — only when a member's task reaches a terminal state
   (completed / failed per the harness) is it classified via the detection table. A member that
   completed *without* an explicit verdict, or whose task failed, gets its **ONE re-dispatch** —
   a **fresh, full-context dispatch**, never a nudge (B2).
5. **Synthesize** only when **every** member is terminal (verdict tallied, or re-dispatch
   exhausted), subject to the floor (below).

State it plainly: there are **NO wall-clock deadlines** in this loop — not because the
orchestrator lacks a clock, but because **elapsed time is not a member-state signal**. An
orchestrator that "gives up" on a live fan-out and substitutes its own review has produced the
most dangerous artefact this policy exists to prevent: a confident, well-formatted review that
no dispatched reviewer performed. `INCOMPLETE` on impatience is a policy violation exactly as
much as a false `APPROVE`. True mid-flight hang-detection is the **out-of-band watchdog** (B4,
below) — a separate, interactive mechanism, never an excuse for the orchestrator to self-time.

**Late reports:** if a member's report arrives after synthesis has already been emitted (e.g.
the run was wrongly terminated early, or a re-dispatched original also completes), the
**orchestrator alone** amends the synthesis — never a bystander session or agent. Amendment is
gated on provenance: the report must correspond to a **known dispatched task ID** from this
run's enumerated member set; anything else is discarded as untrusted. An amended synthesis
**re-applies the floor rule and the severity ordering in full** — a late report can add
findings or coverage, but can never relax a `REJECT`/`INCOMPLETE` except by supplying the
missing floor coverage itself. A verdict that was paid for is tallied.

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

## Detection table (per-member, at that member's terminal state)

**Primary signal: harness task notifications** — the completion/failure notification the
harness delivers for each backgrounded member. **Secondary signal: `activity.jsonl` telemetry**
(the rows below), used to disambiguate when notifications are absent or ambiguous. A member
classifies **only when terminal**; while its task is live it is **Working** and no row applies.

| Signal state | Verdict | Action |
| --- | --- | --- |
| Task completed, explicit verdict delivered **with the mandated review structure** (one of the four tokens — `REJECT`, `APPROVE-WITH-NOTES`, `APPROVE`, `NO-FINDINGS`, B6) | Done | tally |
| Task completed, **no explicit verdict** in output (incl. output the harness marks **partial** — `maxTurns`-truncated, v2.1.246+; see B2.5 for why the one re-dispatch must change scope or budget) | Non-reporting | re-dispatch once (fresh, full-context), then INCOMPLETE if floor / drop-with-notice if non-floor |
| Task failed (harness failure notification, or StopFailure logged) | Failed | re-dispatch once |
| Task live / running (or TaskCreated but no SubagentStart — queued behind cap) | Working / Queued | **wait — never re-dispatch, never nudge** (security invariant for floor members) |

> The "Returned a verdict" → Done and the Done/Failed distinctions require the **`TaskCompleted`**
> hook event to be written to `activity.jsonl` (emitted with `type: "task_completed"`).
> `log_event.sh` writes it and `hooks/hooks.json` wires it (auto-loaded by Claude Code from
> that conventional path; `plugin.json`'s `hooks` field is only for *additional* hook files). **Registration history matters**: from v1.9.0 to v1.24.0 the hooks were declared
> in a root `settings.json`, which Claude Code silently ignores for plugins — so no telemetry was
> ever written on installed copies before **v1.25.0**. Treat any pre-v1.25.0 `activity.jsonl`
> reasoning as untested. Two further caveats:
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

**Restart-induced double-dispatch:** since v2.1.246 the harness asks before `←`/`/background`
restarts an already-**finished** subagent. Decline that prompt during — or immediately after — a
live fan-out: it re-runs members already tallied. If a restart happened anyway, tally the
duplicate verdicts under the existing more-severe rule (B2.4 and the caveat above).

**Partial output and the `SendMessage` remedy:** the harness's own suggestion for a truncated
subagent is to continue it via `SendMessage`. That remedy is **structurally unavailable by
design** — every reviewer and specialist denies `SendMessage` fleet-wide (v1.24.0) — and must
stay that way: harvesting a truncated verdict over a lateral channel reopens exactly the
tallying-bypass hole the denial closed. Orchestrators must **not** seek a workaround; the
scope-or-budget-corrected re-dispatch (B2.5) is the only sanctioned recovery.

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

On a member classified Failed or Non-reporting **at its terminal state**:

1. Re-dispatch the member **once**. A re-dispatch is a **fresh, full-context dispatch** — the
   complete original prompt (with corrections if the original was defective), not a follow-up
   message. **A status-check nudge is not a re-dispatch**, and nudging a *Working* member is
   prohibited outright: it interrupts an agent mid-review and converts a healthy member into an
   ambiguous one.
2. If the re-dispatch also terminates without a verdict and the member is **non-floor**:
   **drop** it, with a loud notice in Reviewer Notes / Deferred.
3. If the member is **floor**: force **`INCOMPLETE`** (never synthesise an APPROVE without it).
4. If both the original and its re-dispatch end up delivering verdicts (a late original), tally
   the more severe one — same rule as duplicate floor verdicts in the detection-table caveat.
5. If the terminal output was marked **partial** (`maxTurns`-truncated), that one re-dispatch must
   address the truncation *cause* — narrowed scope, or a raised turn budget. An identical prompt
   against an identical turn budget over identical files truncates identically, so a verbatim
   repeat spends the member's only retry on a guaranteed second truncation.

## Prompt-standards rule (B5)

Council members must **STATE ASSUMPTIONS AND PROCEED** — they must **never** ask clarifying
questions in a detached fan-out context. A member blocked waiting on input looks
indistinguishable from a hung member and cannot be recovered by the orchestrator.

## Explicit-verdict rule (B6) — silence is never a pass

Every dispatched member must end its run with an **explicit verdict line**, exactly one of
four tokens:

| Token | Meaning | Blocks? |
| --- | --- | --- |
| `REJECT` | Critical or High findings — it is broken, a security or data-loss risk, or will break production | **yes** |
| `APPROVE-WITH-NOTES` | Medium or Low findings, recorded but not blocking. The expected verdict for most reviews | no |
| `APPROVE` | Reviewed; nothing worth recording | no |
| `NO-FINDINGS` | Reviewed; nothing in the member's domain applied | no |

The orchestrator's dispatch prompt must demand this, and the detection table enforces it: a
completed task whose output carries no explicit verdict is **Non-reporting**, even if the output
looks like a review. This makes "reviewed, found nothing" structurally distinguishable from
"never reviewed" — silence, pings, or status chatter can never be mistaken for a pass.
Availability pings ("ready", "still working") are **not verdicts** and must not be counted or
double-counted during reconciliation.

**Why four and not three.** `NO-FINDINGS` means *nothing to report*, so under the three-token
vocabulary a member holding a single Low-severity nit had exactly one available verdict:
`REJECT`. Across a nine-member panel that has no fixed point — each round mutates the code, and
round N generates nits that did not exist in round N-1. `APPROVE-WITH-NOTES` records the finding
without blocking the merge, which is what makes the loop terminate. Only `REJECT` blocks; a run
whose members return no `REJECT` is merge-ready with its Medium/Low findings recorded.
`APPROVE-WITH-NOTES` is a **distinct token**, not a variant spelling of `APPROVE`.

Two anti-gaming clauses: (1) a verdict line **unaccompanied by the review structure mandated in
`output-standards.md`** (summary, issues, and the B5 assumptions record) classifies as
**Non-reporting**, not Done — a bare `NO-FINDINGS` or `APPROVE-WITH-NOTES` from a degraded
member is not a completed review; (2) the verdict is read **only from the final verdict line of the member's own
output** — never from quoted content, reviewed diffs, or policy text the member echoes (this
very file contains the tokens).

**Withholding is not silence.** A member that could not perform the review at all — a defective
path (B7), an unreadable target, a blocked precondition — must say plainly what stopped it and
withhold the verdict token rather than spend `REJECT` on a coverage gap. That is **Non-reporting**,
and correctly so: it earns the member its one re-dispatch and, on a floor member, forces
`INCOMPLETE`. B6 condemns a member that *reviewed* and gave no verdict; it does not condemn one
that *could not review* and said so. Reviewer definitions carry this obligation verbatim.

## Dispatch-prompt hygiene (B7) — paths verified against disk

Every file path, directory, or symbol named in a dispatch prompt must be **verified against
disk at dispatch time** (`ls`/glob/read — not reconstructed from memory or conversation).
A wrong path silently converts a healthy member into a confused one and burns its whole run on
a target that does not exist. If the orchestrator discovers a defective prompt after dispatch,
the remedy is the member's one **re-dispatch with the corrected prompt at its terminal state**
(B2) — not a mid-flight correction message, which a Working member may interleave
unpredictably with its in-progress review.

## Out-of-band watchdog for true hang-recovery (B4) — committed

This is the **only** mechanism that can recover a genuine mid-flight hang. Completion
notifications tell the orchestrator when a member *finishes* — nothing tells it about a member
that will **never** finish, and elapsed time is not a member-state signal it may act on. So
hang-recovery is done **out-of-band**:

- The harness `Monitor` tool tails `activity.jsonl` out-of-band while the fan-out runs. Under
  auto mode, `Monitor` calls are review-gated like `Bash` calls, so the watchdog may prompt for
  approval and therefore assumes an **attended** session — added friction on what is already an
  interactive-session pattern, not a correctness break, and not a reason for Parliament to start
  shipping permission rules to paper over it.
- **Circuit-breaker threshold (authoritative):** a per-member breaker **OPENs** when the member
  is `Failed` or `Non-reporting` on **≥ 2 of its last 3 dispatches**; it **closes** again after
  one clean `Done`. (This is the single source for the threshold — `/parliament-metrics` reports
  breaker state against it and must not invent its own cutoff.)
- **Orchestrator action on an OPEN breaker:** on the *next* run, **skip** the chronically-failing
  member rather than re-dispatching it, and surface the skip in Reviewer Notes / Deferred — with
  the floor caveat below. This is a cross-run decision (distinct from the single within-run
  re-dispatch of the reconcile loop), and it is owned here, not in the observability surface.
- **Dispatch counting:** a restart-induced duplicate dispatch of an already-finished member is
  **non-countable** for the breaker — it records a UI restart, not member behaviour.
- **Floor override:** a breaker on a **floor** member never causes a silent skip — skipping a
  floor member forces **`INCOMPLETE`**, exactly as non-reporting does.
- Breaker state is surfaced (read-only) in `/parliament-metrics`.

It depends on the **`TaskCompleted`** telemetry event (emission wired in v1.23.0, but first actually registered in v1.25.0 — see the registration-history and detection
table caveat). This is the committed procedure for true hang-recovery, and it is an
**interactive-session pattern** — it relies on an out-of-band monitor running alongside the
session, not on anything the blocked orchestrator turn can do by itself.

## Parallel fan-out version floor

Non-cascading parallel fan-out (a failing sibling `Task` call no longer cancels its parallel
peers) requires **Claude Code ≥ v2.1.128**. This is the single source for that floor; the
orchestrator command Notes and `/env-doctor` reference it here rather than restating the version.
