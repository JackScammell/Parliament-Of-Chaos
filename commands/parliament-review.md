---
description: Grumpy-reviewer review — relevance- and size-tiered by default, PR rounds counted across invocations; --all forces the full 9-member panel (privacy-paranoid joins on personal data, making 10)
effort: high
context: fork
background: false
agent: senior-council
argument-hint: "[target | PR number] [--all] [--round <n>]"
---

# Parliament Review

Full review using the 9-member default panel (of 12 reviewers total). By default, relevance-tiered to the reviewers whose domain the diff touches; `--all` forces the full 9 for maximum scrutiny — and `grumpy-privacy-paranoid` additionally joins whenever the diff carries personal data, so an `--all` run on PII dispatches **10**. Small (under 50 changed lines) and docs-only changes get a single floor-only round. On a PR, rounds are counted across invocations, and each follow-up round narrows what can block (`.claude/rules/governance.md` **PR review rounds**). Dispatch follows the reconcile-on-notification loop in `.claude/rules/fan-out-policy.md`: members run detached and report back via completion notifications — a member that has not answered yet is Working, and the run must not be declared INCOMPLETE while any member's task is live.

## Reviewers

1. grumpy-code-reviewer - Code quality
2. grumpy-standards-enforcer - Standards compliance
3. grumpy-architecture-skeptic - Architecture decisions
4. grumpy-maintainability-curmudgeon - Maintenance burden
5. grumpy-security-nag - Security oversights
6. grumpy-performance-troll - Performance issues
7. grumpy-accessibility-auditor - WCAG/inclusive design
8. grumpy-documentation-pedant - Documentation gaps
9. grumpy-testing-tyrant - Test coverage/quality

## Usage

```
/parliament-review [target | PR number] [--all] [--round <n>]
```

- `--all` — force the full 9-member panel ("maximum scrutiny"); +privacy-paranoid on personal data = 10. Without it, review is relevance-tiered (see step 1a) and size-tiered (step 1-PR).
- `--round <n>` — PR targets only: override the counted round number (step 1-PR) when the count is wrong. An override may always **lower** the round. Raising it above the counted value is more lenient, so ask the user to confirm first. Record every override in Reviewer Notes and in the posted body.

## Process

1. **Identify review target** (code, file, PR, design).

1-PR. **PR targets** — when the target is a pull request, apply `.claude/rules/governance.md` **PR review rounds** (the policy: review target, round table, proportionate tier). Mechanics:
    - **Full diff, always.** Resolve `baseRefName`, `headRefOid`, `additions`, `deletions`, and `files` via `gh pr view <n> --json baseRefName,headRefOid,additions,deletions,files`. The review target is the full PR diff (`gh pr diff <n>`, or `git diff $(git merge-base origin/<base> <head>)..<head>`) in **every** round. It is never delta-only.
    - **Count the round.** Run `gh pr view <n> --json reviews` and consider only reviews whose `author.login` is the reviewing account (`gh api user --jq .login`). Markers in anyone else's review, including the PR author's, are ignored. Count those reviews whose body carries the round marker `<!-- parliament-review round=`, excluding any whose marker says `verdict=INCOMPLETE`. This invocation is round `count + 1`. **Fallback** for PRs reviewed before the marker existed: if no trusted review carries the marker, count the reviewing account's prior reviews that have state `CHANGES_REQUESTED` or `APPROVED`, or state `COMMENTED` with a non-empty body. Empty-bodied `COMMENTED` reviews are inline replies, not rounds. If the count is ambiguous, take the **lower** plausible count: a lower round is stricter. `--round <n>` overrides both methods, subject to the guard in Usage.
    - **Find the focus.** The last reviewed commit is the `head=` SHA in the newest trusted marker, or else the `commit.oid` of the newest counted review. The SHA must be an ancestor of the current head (`git merge-base --is-ancestor <last-sha> <head>`); if it is not, treat it as unreachable. The focus is `git diff <last-sha>..<head>`. If `<last-sha>` is no longer reachable (the branch was rebased or force-pushed), try `git fetch origin <last-sha>`. If that fails, the focus is the full diff, and "introduced since the last review" is judged against the findings the previous review body recorded: a finding that the previous round raised, or that was visible to it, is not new.
    - **Proportionate tier.** Apply the tier as `governance.md` **Proportionate review** defines it, re-measured on every invocation. The PR-level `additions` and `deletions` include lockfiles and generated files, so compute the size from the per-file entries in `files` with those excluded.
    - **Previous per-reviewer verdicts.** Read them from the previous marked review body (Output lists them). If they cannot be recovered, round ≥2 dispatches the floor plus the reviewers whose domain the **delta** touches (step 1a applied to the delta).

1a. **Relevance-tiered reviewer selection (A2, default)** — run only the reviewers whose domain the diff touches. This reuses `fast-track.md`'s pattern for the **mandatory floor** only (a fixed security + correctness floor, plus binary personal-data detection that conditionally adds `grumpy-privacy-paranoid`) — fast-track has no per-reviewer domain detection, so the per-domain signals below are **new to this command**, not inherited:
    - frontend / markup / UI / template change → `grumpy-accessibility-auditor`
    - user-facing strings, locale, or date/number formatting → `grumpy-i18n-nitpicker`
    - perf-sensitive paths (loops, queries, hot paths, resource limits) → `grumpy-performance-troll`
    - documentation / `*.md` change → `grumpy-documentation-pedant`
    - infrastructure-as-code, cloud config, or resource provisioning → `grumpy-budget-hawk`
    - test files or testable behaviour change → `grumpy-testing-tyrant`
    - architecture / module-boundary / dependency change → `grumpy-architecture-skeptic`
    - long-term maintainability / tech-debt surface → `grumpy-maintainability-curmudgeon`
    - `grumpy-standards-enforcer` is treated as broadly relevant (conventions apply to almost any change).

    The **floor** — `grumpy-security-nag` and `grumpy-code-reviewer`, plus `grumpy-privacy-paranoid` on personal-data changes — is **always present** regardless of tiering; it can never be tiered out. The **proportionate tier** (step 1-PR; small or docs-only changes) takes precedence over the domain signals above and runs the floor only (+ documentation-pedant for docs-only). It applies to local targets as well as PRs, measured on the diff under review. `--all` overrides both tiers and runs the full 9. Log every reviewer skipped by tiering to the **Deferred** section (mirror fast-track's skipped-reviewer pattern).

1b. **Pre-flight cost gate (A4)** — before fan-out, apply the existing `/cost-report estimate` soft-cap band as a **WARN/CONFIRM** gate. This is advisory only and **never a hard block**: over the soft cap → warn and ask to proceed; no telemetry history → degrade to "estimate unavailable — proceed?". This is a **whole-run** estimate — `/cost-report estimate` is the existing whole-command static estimator, not a per-subset admission controller, so do not claim per-reviewer or batch-boundary admission from it. The estimate is **provisional**: relevance-tiering (1a) changes the cost structure, so a telemetry-sourced figure stays approximate until post-change history re-accumulates. **Skip this gate below a small-review size threshold** so small reviews don't pay its fixed overhead net-negative.

2. **Fan out to the selected reviewers** following the **reconcile-on-notification** policy loop in `.claude/rules/fan-out-policy.md` — dispatch prompts carry disk-verified paths (B7) and demand an explicit verdict from the four-token vocabulary — `REJECT`, `APPROVE-WITH-NOTES`, `APPROVE`, or `NO-FINDINGS` (B6). Every dispatch prompt also states the **round number**, the **full diff** as the review target, the **focus** (the delta since the last reviewed SHA, in round ≥2), the **blocking rule for that round** from `governance.md`, and whether the proportionate tier applies. It names the blocking-eligibility caps in `output-standards.md` too. A reviewer that is not told the round will apply the round-1 rule, and that is how follow-up rounds turn into re-trawls; members run detached and are tallied as their completion notifications arrive; a member with a live task is **Working** and must be waited for, never nudged, never given up on. Only at a member's terminal state does classification apply: a completed run without an explicit verdict, or a failed task, gets its one fresh full-context re-dispatch (B2). A **floor** member still unresolved after that forces `INCOMPLETE` (never a survivor-synthesised `APPROVE`); an unresolved non-floor member is dropped with a loud notice in Reviewer Notes/Deferred. The orchestrator must never substitute its own hand-done review for a live fan-out.
3. Collect and deduplicate findings.
4. Rank by severity, then **apply blocking eligibility** before tallying the run verdict. A reviewer's `REJECT` that rests only on findings which are capped (`output-standards.md` Blocking eligibility) or ineligible for this round (`governance.md` round table) is **re-classified** as `APPROVE-WITH-NOTES`. Each re-classified finding must cite the specific cap row or round rule applied, and Reviewer Notes records the reviewer's original severity beside it. Findings move to notes or Deferred. The orchestrator has **no discretion** over three kinds of finding, which are never re-classified: a Critical security or data-loss finding, a finding in executable text (SQL, deploy or rollback steps, migration commands), and a still-unresolved blocker from an earlier round. When it is unclear whether a finding was introduced since the last review, it is treated as introduced. This is the orchestrator enforcing the published rule. It is not a survivor synthesis: the reviewer did report, and only the blocking effect changes. It never applies to a floor member's missing verdict, which still forces `INCOMPLETE`.
5. **Bounded re-review** — a `REJECT` earns **one** second pass per invocation and no more:
    - The second pass **focuses on the delta**, the changes made in response to round 1, and reviewers receive the **full diff as required context**. It is never delta-only: a reviewer that sees only the delta cannot tell whether a fix is right for the code around it. The full diff is context, not a licence to re-trawl. Only findings that are blocking-eligible under the round rule in `governance.md` can block; everything else goes to Deferred.
    - **On a PR target**, a whole invocation is one round (step 1-PR), including an in-session second pass. What can block from round 2 onward follows the round table in `governance.md` **PR review rounds**. A proportionate-tier PR gets a confirmation instead of round 2.
    - Dispatch the reviewers that returned `REJECT`, **plus the floor** — `grumpy-security-nag`, `grumpy-code-reviewer`, and `grumpy-privacy-paranoid` where personal data is present — even when the floor returned a non-blocking verdict in round 1. A non-floor reviewer that returned `APPROVE-WITH-NOTES`, `APPROVE`, or `NO-FINDINGS` is done and is **not** re-dispatched; re-running it only harvests nits that did not exist when it last looked.
    - **Why the floor is unconditional here**: the round-1 fixes are new code that no reviewer has ever read. If the floor is dispatched only when it rejected, the common path — floor returns `APPROVE-WITH-NOTES`, some other reviewer returns `REJECT`, code is written to satisfy that reviewer — merges code the floor never saw. "Security reviewed the previous revision" does not satisfy `governance.md`'s "Security always wins". Under the old blocking-only vocabulary the floor was re-dispatched by construction, because any finding at all forced a `REJECT`; the four-token widening removes that accidental coverage, so it is restored explicitly here. The floor is 2–3 members over a small delta — the cheapest part of the run.
    - A floor member that does not report in the second pass forces **`INCOMPLETE`**, exactly as in round 1. It is never dropped and never assumed to still hold its round-1 verdict.
    - There is **no third pass** within an invocation. Anything still open after the second goes to **Deferred** as a tracked item, not a merge block. Across invocations on a PR, later rounds are allowed but narrow (`governance.md` round table).

    This bound is the point of the four-token vocabulary. Under a blocking-only vocabulary each round mutated the code and each mutation generated fresh Low-severity nits, so a nine-member panel had no fixed point. Two passes, delta-focused, terminates. Counting rounds across invocations closes the remaining route, where each fresh invocation started again at round 1.

## Output

### Severity and blocking

Only **Critical** and **High** findings block. The run verdict is:

- **`REJECT`** — at least one reviewer returned a `REJECT` that survives blocking eligibility (Process step 4). Fix the blocking findings and take the bounded second pass (Process step 5).
- **`APPROVE-WITH-NOTES`** — no blocking-eligible `REJECT` remains. The change is **merge-ready**; the Medium and Low findings are recorded, not gates. This is the expected outcome of most runs.
- **`INCOMPLETE`** — a floor reviewer did not report (see Summary below). Not a `REJECT`, and never a survivor-synthesised approval.

Severity definitions (single-sourced from `.claude/rules/output-standards.md`):

- **Critical** — security vulnerability, data-loss risk, or broken core functionality. Blocks.
- **High** — significant bug, major standards violation, or architectural flaw. Blocks.
- **Medium** — code smell, minor bug, or maintainability concern. Recorded, does not block.
- **Low** — style issue, minor improvement, or documentation gap. Recorded, does not block.

A reviewer that would not hold a release for a finding must not spend a `REJECT` on it. Severity is capped by category first (PR-body, comment, and reply wording at Low; test-quality gaps without a demonstrated live defect at Medium; pre-existing issues to Deferred), and "it must land" is never a reason to block. Both rules are single-sourced in `output-standards.md` **Blocking eligibility**.

### Posting to GitHub

When the target is a PR and the result is posted, follow `output-standards.md` **Posting a verdict to GitHub**. Post one review per invocation. Only a run `REJECT` becomes **Request changes**. `APPROVE-WITH-NOTES` becomes **Approve** with the notes in the body, `APPROVE` and `NO-FINDINGS` become **Approve**, and `INCOMPLETE` becomes **Comment**. The body's first line is the round marker:

```
<!-- parliament-review round=<n> head=<headRefOid> verdict=<RUN-VERDICT> -->
```

followed by each reviewer's verdict, the findings, and the Deferred list. Step 1-PR reads the marker back on the next invocation. Without it, the next invocation must fall back to guessing the round.

### Summary
High-level verdict from the parliament. If a **floor** reviewer (security / correctness, plus privacy on PII) did not report even after its one re-dispatch, the outcome is **`INCOMPLETE`** — a non-blocking terminal state meaning "security/correctness did not run," never a survivor-synthesised `APPROVE`. See the liveness floor in `.claude/rules/fan-out-policy.md`.

### Issues by Severity
**Critical**: [issues]
**High**: [issues]
**Medium**: [issues]
**Low**: [issues]

### Recommendations
Prioritised action items.

### Reviewer Notes
Notable disagreements or trade-offs between reviewers.

### Deferred
Out-of-scope recommendations, reviewers skipped by relevance-tiering, findings made ineligible to block by the round rule or the blocking-eligibility caps (each keeps its severity), pre-existing issues, "it must land" follow-ups, and anything still open after the bounded second pass. A pre-existing **Critical** is listed above Deferred, flagged for an immediate separate fix (`output-standards.md`).

**Destination**: Deferred feeds the **debt register** — `/track-debt` — and nothing else. It becomes a tracker issue only when a human picks the item up and decides it is worth one. Nothing in this section is filed, assigned, or escalated automatically; an auto-filed backlog is how a review loop that cannot converge turns into an issue tracker that nobody reads.

## Notes

- **Upstream `/code-review` distinction**: Claude Code's built-in `/code-review` (including `/code-review ultra`, for which the older `/ultrareview` is a deprecated alias) is a separate upstream feature with its own review model — it does not run the grumpy fleet or honour the fan-out policy floor. This command is the Parliament governance flow.

- Parallel fan-out reliability has a Claude Code version floor (non-cascading sibling failures) and the detection/recovery behaviour (batching, one re-dispatch, liveness floor, `INCOMPLETE` on floor non-report) — both are single-sourced in `.claude/rules/fan-out-policy.md`; see the *Parallel fan-out version floor* and degradation sections there rather than restating the version here.
