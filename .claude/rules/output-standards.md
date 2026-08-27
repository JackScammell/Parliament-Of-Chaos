# Parliament of Chaos Output Standards

## Review Output Format

All grumpy reviewers must use this structure:

1. **Summary** - High-level assessment (2-3 sentences)
2. **Issues** - Problems with severity (Critical/High/Medium/Low) and rationale
3. **Recommendations** - Suggested fixes with specific references
4. **Verdict** - An explicit final verdict line — `APPROVE`, `REJECT`, or `NO-FINDINGS` (reviewed, nothing to report) — with clear reasoning. The three-token vocabulary is mandated by fan-out-policy.md B6: a review without an explicit verdict line is classified Non-reporting

The three-token requirement governs the **form** of a reviewer's verdict instruction, not one
particular phrasing of it. Every reviewer definition must name all three tokens as exact
uppercase literals, and a binary formulation is non-conformant however it is spelled:

- **Synonym pairs** — "approve or object", "approve or decline".
- **Nominalised pairs** — "approval or rejection", "approved or rejected".
- **Negative gating** — "no approval until all issues are addressed", "approve only when
  resolved". The most dangerous class: it makes approval conditional while never offering
  `NO-FINDINGS`, so a reviewer that reviewed and found nothing has no conformant way to say
  so and falls silent — which B6 classifies as Non-reporting, forcing `INCOMPLETE` on a floor
  reviewer.

Conditional and gating grammar is itself **permitted**: what item 4 forbids is a construction that
never offers `NO-FINDINGS`, not the word "until". A verdict instruction may gate each token on its
own condition provided all three appear as exact uppercase literals — "Never `APPROVE` until all
issues are addressed; `REJECT` while any remain; `NO-FINDINGS` only when the review surfaced none"
is conformant, whereas the same sentence stopping at "`REJECT` otherwise" is not.

This rule is mirrored by `scripts/ci/conformance.py` check 7 (`reviewer-verdicts`). Policy is
widened here first; the pattern there follows. Never the other way round.

## Council Output Format

1. **Agents Consulted** - Each agent and why involved
2. **Review Summary** - Issues raised and fixes applied per round; when all approved
3. **Final Solution** - Code, design, or decision approved by all
4. **Trade-offs** - Context, compromises made, and future recommendations

## Deliberation Output Format

1. **Round Positions** - Each agent's stance with confidence scores
2. **Meta-Analysis** - Novelty, overlap, and convergence metrics per round
3. **Voting Results** - Outcome table with agent votes and reasoning
4. **Performance Metrics** - Tokens, rounds, latency, convergence trajectory
5. **Key Insights** - Major agreements, conflicts, and final recommendation

## Severity Definitions

- **Critical**: Security vulnerability, data loss risk, or broken core functionality
- **High**: Significant bug, major standards violation, or architectural flaw
- **Medium**: Code smell, minor bug, or maintainability concern
- **Low**: Style issue, minor improvement, or documentation gap
