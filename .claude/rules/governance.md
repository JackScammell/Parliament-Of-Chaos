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
- **Grumpy reviewers** (9): Quality gates who critique but never implement. Read-only access enforced.
- **task-executor**: Utility agent for task mechanics. Works under senior-council.
- **project-oracle**: Interviews users and generates project planning artifacts.
- **scope-weaver**: Breaks roadmap items into detailed specifications.

## Delegation Rules

- Only orchestrators (senior-council, deliberation-conductor) may spawn sub-agents
- Specialists and reviewers must not spawn other agents
- Reviewers must not modify code — they only read and critique
