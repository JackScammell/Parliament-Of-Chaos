---
description: Minimum-review-floor bypass — runs only security + correctness reviewers, never waives them
effort: medium
argument-hint: "<change-description> [--scope <path>] [--reason <text>] [--link <url>]"
---

# Fast Track

A disciplined alternative to hotfix. The toolset-gaps debate rejected `/hotfix` as a review-safety hazard; `/fast-track` is the replacement. It shortens review to the **minimum governance-compliant floor** — security and correctness reviewers only — and never below.

Think of it as "fast enough to ship a same-day fix without silently trading away safety."

## Usage

```
/fast-track <change-description> [--scope <path>] [--reason <text>] [--link <url>]
```

**Examples**:
```
/fast-track "Null-check userId before lookup in Auth.ts"
/fast-track "Fix CVE-2025-1234 in dep X" --reason "public exploit in the wild"
/fast-track "Rollback broken migration" --scope db/migrations/ --link https://github.com/org/repo/issues/404
```

## Options

- `<change-description>` (required, positional): One-line change description.
- `--scope <path>` (optional): Limit the change to a path. Reviewers only inspect within this scope.
- `--reason <text>` (optional): Why fast-track is warranted. Recorded in telemetry and the PR body.
- `--link <url>` (optional): Link to the incident, CVE, or tracking issue.

## Governance floor (never waivable)

Per governance: security > correctness > maintainability > performance > convenience. Fast-track drops the lower three but keeps the top two:

| Reviewer | Role | Status |
|----------|------|--------|
| `grumpy-security-nag` | Security | **Required** |
| `grumpy-code-reviewer` | Correctness | **Required** |
| `grumpy-standards-enforcer` | Conventions | Skipped |
| `grumpy-maintainability-curmudgeon` | Long-term health | Skipped |
| `grumpy-architecture-skeptic` | Systemic design | Skipped |
| `grumpy-performance-troll` | Performance | Skipped |
| `grumpy-accessibility-auditor` | A11y | Skipped |
| `grumpy-documentation-pedant` | Docs | Skipped |
| `grumpy-testing-tyrant` | Tests | Skipped |
| `grumpy-privacy-paranoid` | Privacy | Required **if change touches personal data** (detected heuristically) |
| `grumpy-i18n-nitpicker` | I18n | Skipped |
| `grumpy-budget-hawk` | Cost | Skipped |

Both required reviewers must APPROVE. If either REJECTs, fast-track is aborted and the change routes to the normal `/parliament-review` path.

## Process

1. **Record intent** — log a `FastTrackStart` event with description, scope, reason, link.
2. **Detect sensitive patterns** — scan the change for personal-data indicators (emails, names, phone numbers, SSNs, medical data). If present, add `grumpy-privacy-paranoid` to the required reviewer set.
3. **Run the floor** — invoke required reviewers in parallel via `Task()`.
4. **Consolidate verdict** — both APPROVE → proceed. Any REJECT → abort and suggest `/parliament-review`.
5. **Mandatory deferred queue** — record the skipped reviewers and the change in `${CLAUDE_PLUGIN_DATA}/fast-track-debt.json`. A follow-up `/parliament-review` of the same change must be scheduled within 7 days.
6. **Emit PR body** — produce a templated description including the reason, the reviewers consulted, the skipped reviewers, and the deferred-review date.

## Output

```
# Fast Track

**Change**: Null-check userId before lookup in Auth.ts
**Scope**: src/auth/
**Reason**: production NPE reported in incident INC-142

## Reviewer floor (required)
- grumpy-security-nag — APPROVE (no new secrets or auth weaknesses introduced)
- grumpy-code-reviewer — APPROVE (null check is correct; no logic regression)

## Skipped reviewers (deferred to follow-up review)
- grumpy-standards-enforcer
- grumpy-maintainability-curmudgeon
- grumpy-architecture-skeptic
- grumpy-performance-troll
- grumpy-accessibility-auditor
- grumpy-documentation-pedant
- grumpy-testing-tyrant
- grumpy-i18n-nitpicker
- grumpy-budget-hawk

## Deferred follow-up scheduled
`/parliament-review` of this change by 2026-04-24. Tracked in ${CLAUDE_PLUGIN_DATA}/fast-track-debt.json.

## Verdict
APPROVED on security + correctness floor. Proceed.
```

## Hard limits

Fast-track refuses to run when any of these apply:

- **Change touches authentication/authorisation code without a linked CVE or incident** — requires full review.
- **Change touches migrations or destructive DB operations** — requires full review.
- **Change exceeds 200 lines of diff** — not a "fix", is a feature.
- **Fast-track has been used on this scope within the last 24h** — prevents repeated floor-level bypass on the same area.

These limits are non-negotiable and not configurable by flags. The debate's budget-hawk argued for them; the governance priority enforces them.

## Notes

- Fast-track produces **debt**. Every use is logged, and a full review is mandatory within 7 days. `/parliament-metrics` surfaces fast-track frequency as an SLO.
- The command replaces the rejected `/hotfix` proposal. Same urgency, enforced safety floor.
- Use `/summon-council` for changes needing the full deliberation. `/fast-track` is for surgical, time-critical fixes only.
- When in doubt, run the full review. Fast-track is a sharp tool.
