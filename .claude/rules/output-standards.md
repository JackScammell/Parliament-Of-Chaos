# Parliament of Chaos Output Standards

## Review Output Format

All grumpy reviewers must use this structure:

1. **Summary** - High-level assessment (2-3 sentences)
2. **Issues** - Problems with severity (Critical/High/Medium/Low) and rationale
3. **Recommendations** - Suggested fixes with specific references
4. **Verdict** - Approve or reject with clear reasoning

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
