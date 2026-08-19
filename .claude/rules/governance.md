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
- Iterate until all reviewers approve or trade-offs are documented and accepted by user

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
