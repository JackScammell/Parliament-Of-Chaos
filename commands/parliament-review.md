---
description: Grumpy-reviewer review — relevance-tiered by default, --all forces the full 9
effort: high
context: fork
background: false
agent: senior-council
argument-hint: "[target] [--all]"
---

# Parliament Review

Full review using the 9 grumpy reviewers. By default, relevance-tiered to the reviewers whose domain the diff touches; `--all` forces the full 9 for maximum scrutiny.

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

- `--all` — force the full 9 reviewers ("maximum scrutiny"). Without it, review is relevance-tiered (see step 1a).

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

2. **Fan out to the selected reviewers** following the reconcile-after-return policy loop in `.claude/rules/fan-out-policy.md` — concurrency-aware batching (B1), graceful degradation with one re-dispatch of any non-reporting member (B2), and the liveness floor. A non-reporting **floor** member forces an `INCOMPLETE` result (never a survivor-synthesised `APPROVE`); a non-reporting non-floor member is dropped with a loud notice in Reviewer Notes/Deferred.
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

- Parallel fan-out reliability has a Claude Code version floor (non-cascading sibling failures) and the detection/recovery behaviour (batching, one re-dispatch, liveness floor, `INCOMPLETE` on floor non-report) — both are single-sourced in `.claude/rules/fan-out-policy.md`; see the *Parallel fan-out version floor* and degradation sections there rather than restating the version here.
