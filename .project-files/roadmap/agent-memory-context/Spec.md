# Specification: agent-memory-context

## Overview

**Item**: agent-memory-context
**Phase**: 4 (Quality of Life Features)
**Dependencies**: None

## Problem Statement

Each agent invocation starts fresh with no memory of previous sessions. This means:
1. Specialists re-discover the same context repeatedly
2. Previous decisions are not referenced
3. Patterns and preferences must be re-explained
4. No continuity across review sessions

## Goals

1. **Context persistence** - agents can reference previous work
2. **Decision memory** - past trade-offs and choices are available
3. **Pattern learning** - project-specific conventions are remembered
4. **Lightweight** - minimal overhead for context loading

## Non-Goals

- Full conversation history storage
- Cross-project memory
- Automatic learning without user input
- Real-time context synchronization

## Technical Approach

### Context Sources

Leverage existing project files as memory:

| Source | Contains |
|--------|----------|
| `.project-files/project-outline.md` | Project goals, constraints, scope |
| `.project-files/roadmap/*/work_complete.md` | Previous decisions and trade-offs |
| `.parliament-of-chaos/reviews/` | Past review outcomes (if scribe enabled) |

### Context Loading

Add context awareness to senior-council orchestration:

```markdown
## Context Loading

Before starting work:
1. Read `.project-files/project-outline.md` for project context
2. Scan `.project-files/roadmap/*/work_complete.md` for previous decisions
3. Reference relevant past work when making new recommendations
```

### Memory Markers

Allow users to flag important decisions for memory:

```
/summon-council
remember: We chose JWT over sessions for mobile support

Design the token refresh mechanism...
```

These markers get appended to a context file:

```
.parliament-of-chaos/
  context.md    # User-flagged decisions and preferences
```

### Context File Format

```markdown
# Parliament Context

## Project Decisions
- 2025-12-04: Chose JWT over sessions for mobile support
- 2025-12-03: Using PostgreSQL, not MySQL

## Coding Preferences
- Prefer composition over inheritance
- Always use strict TypeScript

## Review Preferences
- Security is highest priority
- Performance is secondary to maintainability
```

### Commands to Update

| Command | Change |
|---------|--------|
| `/summon-council` | Load context before orchestration |
| `/implement-task-list` | Reference previous work_complete.md files |
| New: `/remember` | Add decision to context.md |
| New: `/forget` | Remove decision from context.md |

## Acceptance Criteria

- [ ] Agents reference project-outline.md for context
- [ ] Previous work_complete.md files inform current decisions
- [ ] `remember:` parameter stores user decisions
- [ ] `/remember` command adds to context.md
- [ ] `/forget` command removes from context.md
- [ ] Context is loaded at session start
- [ ] Documentation explains memory system

## Risks

| Risk | Mitigation |
|------|------------|
| Context file grows too large | Limit to recent N entries; allow pruning |
| Stale context causes confusion | Include dates; user can /forget outdated items |
| Token overhead from context loading | Keep context file concise; summarise |
| Privacy concerns | Context is local; user controls content |

## Open Questions

1. How much context is too much? Token budget considerations.
2. Should context auto-summarise periodically?
3. Should agents be able to suggest "remember this" for important decisions?
4. Integration with export feature (review-report-export)?
