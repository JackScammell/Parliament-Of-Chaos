# Parliament of Chaos Governance Rules

## Conflict Resolution Priority

When reviewers or agents disagree, apply this priority hierarchy:

1. **Security** - Always wins
2. **Correctness** - Must be right
3. **Maintainability** - Must be sustainable
4. **Performance** - Should be fast
5. **Convenience** - Nice to have

## Review Process

- All implementation work must pass through grumpy review before approval
- Out-of-scope recommendations: log to "Deferred" section, do not block approval
- Present genuine trade-offs to user when reviewers disagree
- Only `REJECT` blocks. A reviewer holding Medium or Low findings returns `APPROVE-WITH-NOTES`
  and the change is merge-ready with those findings recorded — see the four-token vocabulary in
  `.claude/rules/output-standards.md`
- Severity is capped by category before any verdict is chosen, and "it must land" is never grounds
  for `REJECT`. See **Blocking eligibility** in `.claude/rules/output-standards.md`
- Iteration is **bounded**: a `REJECT` earns one delta-focused second pass from the reviewers that
  rejected **plus the floor**, and an invocation never runs a third pass. Anything still open after
  it is Deferred to the debt register, not a merge block. An unbounded "iterate until all approve" loop
  has no fixed point, because each round mutates the code and each mutation generates findings the
  previous round could not have raised. On a PR target, rounds are also counted **across
  invocations**. See **PR review rounds** below
- The **floor is unconditional in the second pass** — it reviews the round-1 fixes even when it
  returned a non-blocking verdict in round 1, because otherwise those fixes merge without security
  or correctness ever having read them, which "Security always wins" does not permit. Mechanics
  and full rationale: `commands/parliament-review.md` Process step 5

## PR review rounds

This section is the single source for how review scales across repeated invocations on one pull
request. `commands/parliament-review.md` holds the mechanics: the `gh` commands, the round marker,
and the dispatch prompt.

### Review target: the full PR, with the delta as the focus

- Every reviewer receives the **full PR diff**: merge-base to head (`gh pr diff <n>`, or
  `git diff $(git merge-base origin/<base> HEAD)..HEAD`). This applies in every round.
- In a follow-up round, the **delta since the last reviewed commit** is the reviewer's **focus**.
  The full diff is required context. A review is **never delta-only**. A delta read without the
  rest of the change produces wrong fixes and misses conflicts, including an unreviewed merge
  commit.
- Reviewing the full diff is not permission to re-trawl it. The blocking rule for the round decides
  what can block. Anything the full-diff context turns up outside that rule goes to Deferred.

### Round counting

On a PR target, the invocation **is** a round. Its number is 1 plus the number of prior Parliament
reviews already posted on that PR (the counting procedure, including its fallback for reviews posted
before the round marker existed, is in `parliament-review.md`). A whole invocation is **one** round,
including any in-session second pass it runs; it posts one marker carrying the final head. The next
invocation is the next round.

- **Only trusted markers count.** A round is counted only from a review posted by the reviewing
  account. Markers in anyone else's review (including the PR author's) are ignored, because the round
  number decides what may block and must not be settable by the party being reviewed.
- **Uncertainty resolves strict.** When the count is ambiguous, take the **lower** round. A lower
  round blocks more, and "Security always wins".
- **A run that did not complete is not a round.** A prior review whose verdict was `INCOMPLETE` is
  not counted: the floor did not run, so the next invocation repeats that round rather than
  advancing past it.

| Round | What can block (`REJECT`) | Everything else |
| --- | --- | --- |
| 1 | Critical or High, after the blocking-eligibility caps | Recorded as notes or Deferred |
| ≥ 2 | **Critical security or data-loss** from anywhere in the PR; any **still-unresolved blocker** from an earlier round; and Critical or High findings **introduced by the changes since the last review** | Deferred |

- **Critical security or data-loss findings block in every round.** This holds even when the
  finding was present in round 1 and missed there, because "Security always wins".
- **An unresolved blocker keeps blocking.** A finding that blocked an earlier round and has not been
  fixed still blocks. The round narrowing applies only to findings raised for the first time;
  otherwise re-running the review without changing anything would turn a `REJECT` into an Approve.
- **New code is always reviewable.** Code pushed after the last review has never been read, so a
  Critical or High finding located in it blocks in every round. What the rounds stop is a re-trawl
  of code that earlier rounds already saw, not scrutiny of code nobody has seen. This converges
  because only new code can raise a new blocker.
- **"Introduced since the last review"** means the finding is located in, or caused by, the delta.
  Examples: a new defect in a round-1 fix, a merge that brought in a conflict, or a fix that breaks
  a caller. A defect that round 1 could have seen and did not raise does not qualify, unless it is
  Critical security or data-loss.
- The floor stays unconditional in every follow-up round, exactly as in the second pass. The floor
  reviews the delta with the full diff as context, and a non-reporting floor member forces
  `INCOMPLETE`.
- The round number never lowers the severity of a finding. It changes only whether the finding
  **blocks**. A Deferred High finding is still recorded as High.

### Proportionate review

A change qualifies for the proportionate tier if it has **fewer than 50 changed lines**
(additions plus deletions over the full PR diff, excluding lockfiles and generated files), or if it
is **docs-only**. It then gets:

- **A single round.** If that round returns `REJECT`, the fix gets a **confirmation** and not a new
  round, run by the floor plus the reviewer that raised the blocker. The confirmation answers only
  two questions: is the blocking finding resolved, and does any code added since the last review
  contain a new Critical or High finding? It raises nothing else.
- **The tier is re-measured on every invocation.** Size is taken over the full PR diff each time.
  A PR that has grown out of the tier gets a normal round at its counted round number, with the
  relevance-tiered panel.
- **The floor only.** That is `grumpy-security-nag` and `grumpy-code-reviewer`, plus
  `grumpy-privacy-paranoid` when personal data is present, plus `grumpy-documentation-pedant` when
  the change is docs-only. The floor is never dropped for size.
- **No mutation-testing demands.** Reviewers do not ask for mutation runs or for surviving mutants
  to be killed.

**Docs-only** means that every changed file is prose that no runtime loads as instructions: a
README, a CHANGELOG, or pages under `docs/`. Markdown that is loaded as agent, command, skill, or
rule prompts (`agents/`, `commands/`, `.claude/`, skill files) is code, even though it is `.md`.
An explicit `--all` overrides the proportionate tier, because it is a deliberate request for
maximum scrutiny. `--all` changes **who** reviews, not what can block: the round table still
applies.

## Agent Hierarchy

- **senior-council**: Orchestrates specialists and reviewers. Coordinates, does not implement.
- **deliberation-conductor**: Orchestrates structured debates with convergence detection.
- **Specialists** (16): Domain experts who analyse and implement solutions.
- **Grumpy reviewers** (12): Quality gates who critique but never implement. Read-only access enforced. (The "9-grump implement panel" used by `/summon-council implement` is a deliberate subset — privacy-paranoid, i18n-nitpicker, and budget-hawk are relevance-tiered in rather than part of the default panel.)
- **task-executor**: Utility agent for task mechanics. Works under senior-council.
- **project-oracle**: Interviews users and generates project planning artifacts.
- **scope-weaver**: Breaks roadmap items into detailed specifications.

## Delegation Rules

- Only orchestrators (senior-council, deliberation-conductor) may spawn sub-agents — enforced structurally via `Task` in every non-orchestrator's `disallowedTools` (v1.24.0), not just by this rule
- Specialists and reviewers must not spawn other agents
- Non-orchestrator agents (specialists, reviewers, planning agents, task-executor) must not message other fanned-out agents laterally (the harness's cross-session SendMessage / @-mention primitives) — enforced structurally via `SendMessage` in their `disallowedTools` (v1.24.0). All coordination flows through the orchestrator — a lateral channel would bypass verdict tallying and corrupt per-member attribution, the same reason spawning is banned
- Reviewers must not modify code — they only read and critique
