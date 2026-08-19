---
description: Grumpy-reviewer review — relevance-tiered by default; --all forces the full 9-member panel (privacy-paranoid joins on personal data, making 10)
effort: high
context: fork
background: false
agent: senior-council
argument-hint: "[target] [--all]"
---

# Parliament Review

Full review using the 9-member default panel (of 12 reviewers total). By default, relevance-tiered to the reviewers whose domain the diff touches; `--all` forces the full 9 for maximum scrutiny — and `grumpy-privacy-paranoid` additionally joins whenever the diff carries personal data, so an `--all` run on PII dispatches **10**. Dispatch follows the reconcile-on-notification loop in `.claude/rules/fan-out-policy.md`: members run detached and report back via completion notifications — a member that has not answered yet is Working, and the run must not be declared INCOMPLETE while any member's task is live.

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
/parliament-review [target] [--all]
```

- `--all` — force the full 9-member panel ("maximum scrutiny"); +privacy-paranoid on personal data = 10. Without it, review is relevance-tiered (see step 1a).

## Process

1. **Identify review target** (code, file, PR, design).

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

    The **floor** — `grumpy-security-nag` and `grumpy-code-reviewer`, plus `grumpy-privacy-paranoid` on personal-data changes — is **always present** regardless of tiering; it can never be tiered out. `--all` overrides tiering and runs the full 9. Log every reviewer skipped by tiering to the **Deferred** section (mirror fast-track's skipped-reviewer pattern).

1b. **Pre-flight cost gate (A4)** — before fan-out, apply the existing `/cost-report estimate` soft-cap band as a **WARN/CONFIRM** gate. This is advisory only and **never a hard block**: over the soft cap → warn and ask to proceed; no telemetry history → degrade to "estimate unavailable — proceed?". This is a **whole-run** estimate — `/cost-report estimate` is the existing whole-command static estimator, not a per-subset admission controller, so do not claim per-reviewer or batch-boundary admission from it. The estimate is **provisional**: relevance-tiering (1a) changes the cost structure, so a telemetry-sourced figure stays approximate until post-change history re-accumulates. **Skip this gate below a small-review size threshold** so small reviews don't pay its fixed overhead net-negative.

2. **Fan out to the selected reviewers** following the **reconcile-on-notification** policy loop in `.claude/rules/fan-out-policy.md` — dispatch prompts carry disk-verified paths (B7) and demand an explicit `APPROVE`/`REJECT`/`NO-FINDINGS` verdict (B6); members run detached and are tallied as their completion notifications arrive; a member with a live task is **Working** and must be waited for, never nudged, never given up on. Only at a member's terminal state does classification apply: a completed run without an explicit verdict, or a failed task, gets its one fresh full-context re-dispatch (B2). A **floor** member still unresolved after that forces `INCOMPLETE` (never a survivor-synthesised `APPROVE`); an unresolved non-floor member is dropped with a loud notice in Reviewer Notes/Deferred. The orchestrator must never substitute its own hand-done review for a live fan-out.
3. Collect and deduplicate findings.
4. Rank by severity.

## Output

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
Out-of-scope recommendations logged for future work.

## Notes

- **Upstream `/code-review` distinction**: Claude Code's built-in `/code-review` (including `/code-review ultra`, for which the older `/ultrareview` is a deprecated alias) is a separate upstream feature with its own review model — it does not run the grumpy fleet or honour the fan-out policy floor. This command is the Parliament governance flow.

- Parallel fan-out reliability has a Claude Code version floor (non-cascading sibling failures) and the detection/recovery behaviour (batching, one re-dispatch, liveness floor, `INCOMPLETE` on floor non-report) — both are single-sourced in `.claude/rules/fan-out-policy.md`; see the *Parallel fan-out version floor* and degradation sections there rather than restating the version here.
