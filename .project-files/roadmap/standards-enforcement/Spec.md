# Spec: Standards Enforcement

## Overview

Enhance all specialist agents to enforce strict technology standards by:
1. Requiring conformance to official language/framework conventions
2. Consulting official documentation when uncertain
3. Producing output that follows established best practices

## Problem Statement

Currently, specialist agents provide recommendations based on general knowledge but don't explicitly:
- Reference official documentation for the technology being used
- Enforce language-specific idioms and conventions
- Verify their suggestions against current best practices

This can lead to:
- Non-idiomatic code suggestions
- Outdated patterns when frameworks evolve
- Inconsistent adherence to community standards

## Requirements

### Functional Requirements

1. **Documentation Consultation**
   - Agents MUST use WebSearch/WebFetch to consult official docs when uncertain
   - Agents MUST cite sources for non-obvious recommendations
   - Agents SHOULD prefer official documentation over third-party guides

2. **Standards Conformance**
   - Agents MUST follow official style guides for the detected language/framework
   - Agents MUST use idiomatic patterns for the technology stack
   - Agents MUST flag when their suggestions deviate from standards (with justification)

3. **Technology Detection**
   - Agents SHOULD detect the technology stack from context (package.json, composer.json, etc.)
   - Agents SHOULD adapt recommendations to the specific framework version when detectable

### Non-Functional Requirements

1. **Token Efficiency**
   - New instructions must be concise (follow agent-token-optimization guidelines)
   - Target: <5 additional lines per agent

2. **Backward Compatibility**
   - Existing agent behavior preserved
   - New behavior is additive, not replacing

## Technical Approach

### Option A: Shared Standards Section (Recommended)

Add a universal "Standards Compliance" section to all 16 specialist agents:

```markdown
## Standards Compliance

- Follow official docs and style guides for detected technology
- Use WebSearch to verify uncertain recommendations against current best practices
- Cite sources for non-obvious patterns
- Flag any intentional deviation from standards with justification
```

**Pros**: Consistent, easy to maintain, single source of truth
**Cons**: Slight duplication across agents

### Option B: Inheritance via Reference

Create a shared standards file that agents reference.

**Pros**: DRY principle
**Cons**: Claude Code may not support file includes in agent prompts

### Option C: Grumpy Reviewer Enhancement Only

Enhance grumpy-standards-enforcer to catch non-compliant suggestions from specialists.

**Pros**: No changes to specialist agents
**Cons**: Reactive rather than proactive; issues caught late in review cycle

## Affected Agents

All 16 specialist agents:
- api-keeper
- backend-goblin
- config-curator
- data-warlock
- dependency-detective
- doc-bard
- migration-monk
- observability-oracle
- package-wizard
- pipeline-engineer
- refactor-ranger
- resilience-tamer
- security-knight
- system-architect
- test-prophet
- ui-ux-guru

## Out of Scope

- Grumpy reviewers (they review, not produce)
- Planning agents (project-oracle, scope-weaver, task-executor)
- Orchestrator (senior-council)

## Success Criteria

1. All 16 specialist agents include standards enforcement instructions
2. Agents demonstrably consult documentation when asked about specific technologies
3. Output includes source citations for framework-specific recommendations
4. No regression in agent token efficiency (maintain optimization targets)

## Dependencies

- None (standalone enhancement)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Token bloat | Medium | Medium | Strict 5-line limit for new section |
| Over-reliance on web search | Low | Low | "when uncertain" qualifier |
| Inconsistent implementation | Medium | Medium | Use identical text across agents |

## Related Work

- `agent-token-optimization` - Established guidelines for concise agent prompts
- `grumpy-standards-enforcer` - Existing reviewer that checks standards compliance
