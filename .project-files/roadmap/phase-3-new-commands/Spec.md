# Spec: Phase 3 - New Commands + Command Optimization

## Overview

Phase 3 delivers improved agent discoverability, direct agent access, and optimizes all existing commands for minimal token usage. This phase unblocks users from navigating the growing agent roster and establishes command design patterns for future development.

## Goals

1. **Discoverability**: Users can list and understand available agents
2. **Direct Access**: Users can invoke specialists without going through council
3. **Full Review**: Coordinated review using all 9 grumpy reviewers
4. **Token Efficiency**: All commands follow optimization guidelines (~30-35 lines)

---

## Command Specifications

### 1. cmd-list-agents

**Purpose**: Display all available agents organized by category

**Behavior**:
- List all agents in `.claude/agents/parliament-of-chaos/`
- Group by category: Specialists, Grumpy Reviewers, Orchestrators/Planners
- Show name and one-line description (from YAML frontmatter)
- Output as formatted table or list

**Output Format**:
```
## Specialists (N agents)
| Agent | Description |
|-------|-------------|
| api-keeper | API design and contract specialist |
...

## Grumpy Reviewers (N agents)
...

## Orchestrators (N agents)
...
```

**Target**: 25-30 lines

---

### 2. cmd-explain-agent

**Purpose**: Explain what a specific agent does in detail

**Arguments**: `$ARGUMENTS` - agent name (e.g., `grumpy-code-reviewer`)

**Behavior**:
- Read the specified agent file
- Extract and present: name, description, focus areas, process, output format
- Explain when to use this agent vs alternatives
- If agent not found, list similar agents

**Output Format**:
```
# Agent: [name]
[description]

## When to Use
- ...

## Focus Areas
- ...

## What You Get
- ...
```

**Target**: 25-30 lines

---

### 3. cmd-summon-specialist

**Purpose**: Directly invoke a specialist agent on the current task

**Arguments**: `$ARGUMENTS` - specialist name (e.g., `security-knight`)

**Behavior**:
- Validate agent exists and is a specialist (not grumpy reviewer or orchestrator)
- Load agent prompt and apply to current context
- Execute as that specialist
- Provide specialist-style output

**Validation**:
- Agent must exist
- Agent must be a specialist (not `grumpy-*`, `senior-council`, `scope-weaver`, etc.)
- Clear error if invalid

**Target**: 30-35 lines

---

### 4. cmd-parliament-review

**Purpose**: Run full parliament review with all 9 grumpy reviewers

**Dependencies**: Phase 2 grumpy reviewers (COMPLETE)

**Behavior**:
1. Identify what to review (code, PR, file, design)
2. Summon all 9 grumpy reviewers in sequence:
   - grumpy-code-reviewer
   - grumpy-standards-enforcer
   - grumpy-architecture-skeptic
   - grumpy-maintainability-curmudgeon
   - grumpy-security-nag
   - grumpy-performance-troll
   - grumpy-accessibility-auditor
   - grumpy-documentation-pedant
   - grumpy-testing-tyrant
3. Collect and deduplicate findings
4. Synthesize into actionable review report
5. Provide severity-ranked issue list

**Output Format**:
```
# Parliament Review

## Summary
[High-level verdict]

## Issues by Severity
### Critical
...
### High
...
### Medium
...
### Low
...

## Recommendations
1. ...

## Reviewer Notes
[Notable disagreements or trade-offs]
```

**Target**: 30-35 lines

---

## Command Optimization Specifications

### Existing Commands to Optimize

| Command | Current Lines | Target Lines | Reduction Goal |
|---------|---------------|--------------|----------------|
| summon-grumpy-reviewer.md | 58 | ~28 | ~52% |
| summon-council.md | 89 | ~35 | ~61% |

### Optimization Patterns

Apply same patterns from agent optimization:

1. **Remove verbose preambles** - "Your job is to:" becomes implicit
2. **Use imperative verbs** - "Review" not "You should review"
3. **Collapse lists** - Multi-line explanations become single bullets
4. **Remove template examples** - Keep structure names, drop sample content
5. **Trust Claude's knowledge** - Don't explain "code review" concepts
6. **Consolidate redundant sections** - Merge similar instructions

### summon-grumpy-reviewer.md Optimization Plan

**Current Issues**:
- Lines 13-17: Verbose "First, restate" section (can be 1 line)
- Lines 18-27: Angle list with explanations (implicit in grumpy agents)
- Lines 29-37: Per-angle instructions (redundant with agent behavior)
- Lines 38-55: Output format over-specified (agents already define this)

**Target Structure** (~28 lines):
```
# Grumpy Reviewer

[1-line role]

## Task
- [2-3 bullets on what to do]

## Process
1. State goal and success criteria
2. Review from multiple angles
3. Identify issues with rationale
4. Suggest concrete fixes

## Output
[Reference standard grumpy output format]
```

### summon-council.md Optimization Plan

**Current Issues**:
- Lines 10-37: Full agent roster (should reference, not list)
- Lines 40-44: Verbose goal restatement (can be 1 bullet)
- Lines 45-59: Example angles list (implicit in agents)
- Lines 60-66: Per-angle instructions (redundant)
- Lines 67-77: Grumpy phase over-explained
- Lines 81-86: Output format verbose

**Target Structure** (~35 lines):
```
# Summon the Council

[1-line role as orchestrator]

## Process
1. Clarify goal and success criteria
2. Select relevant specialists
3. Delegate and collect outputs
4. Run grumpy review phase
5. Iterate until grumps accept
6. Synthesize final answer

## Specialists
[Reference agent categories, don't list all]

## Output
- Summary of goal and approach
- Final solution
- Trade-offs considered
```

---

## Design Principles for Commands

1. **30-35 line maximum** - Match optimized agent targets
2. **Single responsibility** - One clear purpose per command
3. **Consistent structure** - Purpose, Process, Output sections
4. **Reference don't repeat** - Point to agents by name
5. **Trust the model** - Don't over-explain Claude concepts
6. **Clear arguments** - Use `$ARGUMENTS` placeholder for inputs
7. **Graceful errors** - Handle missing/invalid inputs

---

## Dependencies

| Item | Dependency | Status |
|------|------------|--------|
| cmd-list-agents | None | Ready |
| cmd-explain-agent | None | Ready |
| cmd-summon-specialist | Specialists exist | Ready (16 specialists) |
| cmd-parliament-review | All grumpy reviewers | Ready (Phase 2 complete) |
| Command optimization | None | Ready |

---

## Acceptance Criteria

### New Commands
- [ ] All 4 commands created and functional
- [ ] Each command <= 35 lines
- [ ] Consistent structure across commands
- [ ] Error handling for invalid inputs
- [ ] README updated with new commands

### Command Optimization
- [ ] summon-grumpy-reviewer.md optimized (~52% reduction)
- [ ] summon-council.md optimized (~61% reduction)
- [ ] Functionality preserved (same behavior, less tokens)
- [ ] Test both commands after optimization

### Documentation
- [ ] Roadmap.md updated with Phase 3 status
- [ ] work_complete.md created after completion

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-optimization loses clarity | Medium | Test each command after optimization |
| Agent list gets stale | Low | cmd-list-agents reads from filesystem |
| Grumpy review takes too long | Medium | Allow partial review (subset of grumps) |

---

## Out of Scope

- New agent creation (Phase 1, 2 complete)
- Agent memory/context (Phase 4)
- Review report export (Phase 4)
- Configurable grumpiness (Phase 4)
