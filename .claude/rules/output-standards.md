# Parliament of Chaos Output Standards

## Review Output Format

All grumpy reviewers must use this structure:

1. **Summary** - High-level assessment (2-3 sentences)
2. **Issues** - Problems with severity (Critical/High/Medium/Low) and rationale
3. **Recommendations** - Suggested fixes with specific references
4. **Verdict** - An explicit final verdict line — `REJECT`, `APPROVE-WITH-NOTES`, `APPROVE`, or `NO-FINDINGS` — with clear reasoning. The four-token vocabulary is mandated by fan-out-policy.md B6: a review without an explicit verdict line is classified Non-reporting

The four tokens are ordered most-severe first and are not interchangeable:

- `REJECT` — Critical or High findings only. Reserve it for: it is broken, it is a security or
  data-loss risk, or it will break something in production. If you would not hold a release for
  it, it is not a `REJECT`.
- `APPROVE-WITH-NOTES` — you found Medium or Low issues. Record them; they do not block the
  merge. This is the expected verdict for most reviews.
- `APPROVE` — reviewed, nothing worth recording.
- `NO-FINDINGS` — reviewed, nothing in your domain applied.

`APPROVE-WITH-NOTES` exists to make review converge. Under the previous three-token vocabulary a
reviewer holding one Low-severity nit had exactly one verdict available to it — `REJECT` — so a
nine-member panel had no fixed point: every round mutated the code, and every mutation generated
nits that did not exist in the round before. A verdict that records a finding **without** blocking
the merge is what terminates that loop.

`APPROVE-WITH-NOTES` is a distinct token, **not** an instance of `APPROVE`. A reviewer definition
that names only `APPROVE-WITH-NOTES` has not thereby named `APPROVE`, and vice versa.

The four-token requirement governs the **form** of a reviewer's verdict instruction, not one
particular phrasing of it. Every reviewer definition must name all four tokens as exact
uppercase literals, and any formulation that fails to offer the non-blocking outcomes
(`APPROVE-WITH-NOTES`, `NO-FINDINGS`) is non-conformant however it is spelled:

- **Synonym pairs** — "approve or object", "approve or decline".
- **Nominalised pairs** — "approval or rejection", "approved or rejected".
- **Negative gating** — "no approval until all issues are addressed", "approve only when
  resolved". The most dangerous class: it makes approval conditional while never offering
  `APPROVE-WITH-NOTES` or `NO-FINDINGS`, so a reviewer that reviewed and holds only a nit — or
  found nothing at all — has no conformant way to say so and falls silent, which B6 classifies
  as Non-reporting, forcing `INCOMPLETE` on a floor reviewer.

Conditional and gating grammar is itself **permitted**: what item 4 forbids is a construction that
never offers the non-blocking tokens, not the word "until". A verdict instruction may gate each
token on its own condition provided all four appear as exact uppercase literals — "`REJECT` only
for Critical or High; `APPROVE-WITH-NOTES` while any Medium or Low finding stands; never `APPROVE`
until there is nothing worth recording; `NO-FINDINGS` only when nothing in the domain applied" is
conformant, whereas the same sentence stopping at "`REJECT` otherwise" is not.

### Finding budget and the cost of a round-trip

Report at most **5** findings, ranked by severity. Anything beyond that goes to **Deferred**. A
long list is not a thorough review; it is an unranked one.

This is a two-person team. Weigh every finding against the cost of the round-trip: if fixing it
costs more than living with it, record it as Medium or Low and return `APPROVE-WITH-NOTES` — do
not spend a `REJECT` on it.

This section is **authoritative** for the finding budget and the round-trip cost test, but the two
are single-sourced differently, on purpose:

- **The round-trip cost test above is single-sourced here and nowhere else.** No agent definition
  restates it; they inherit it by reading this file. Keep it that way.
- **The 5-finding budget sentence is deliberately mirrored** into the `## Fan-Out Contract` block
  of all 29 fan-out-capable agents. That block exists to travel *with* a dispatched member, whose
  context is not guaranteed to include this file, so a contract that pointed here for its own
  budget would be incomplete exactly when it is needed. The duplication is the cost of making the
  contract self-contained.

**Consequence for maintainers**: changing the number `5` means changing it here *and* in the 29
contract blocks in the same commit. It is not enough to edit this file. Nothing in CI enforces the
pairing today (`conformance.py` check 6 spot-checks only the circuit-breaker threshold and the
version floor), so this paragraph is the guard — do not delete it.

This rule is mirrored by `scripts/ci/conformance.py` check 7 (`reviewer-verdicts`). Policy is
widened here first; the pattern there follows. Never the other way round.

## Council Output Format

1. **Agents Consulted** - Each agent and why involved
2. **Review Summary** - Issues raised and fixes applied per round; the verdict each reviewer returned, and whether any `REJECT` remains outstanding
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
