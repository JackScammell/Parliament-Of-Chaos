# Specification: configurable-grumpiness

## Overview

**Item**: configurable-grumpiness
**Phase**: 4 (Quality of Life Features)
**Dependencies**: None

## Problem Statement

The 9 grumpy reviewers always operate at maximum strictness. This can be:
1. Overwhelming for quick iterations or prototypes
2. Overkill for small changes
3. Frustrating when users want "good enough" not "perfect"

Users need a way to dial down the intensity for appropriate contexts.

## Goals

1. **Adjustable strictness** - let users set review intensity
2. **Per-command control** - apply to individual review sessions
3. **Sensible defaults** - maximum grumpiness remains default
4. **Clear semantics** - users understand what each level means

## Non-Goals

- Per-reviewer configuration (too granular)
- Persistent settings across sessions (Claude Code has no state)
- Disabling specific reviewers entirely

## Technical Approach

### Grumpiness Levels

| Level | Name | Behaviour |
|-------|------|-----------|
| 3 | `strict` (default) | Full scrutiny, all issues reported, blocking on high/critical |
| 2 | `moderate` | Focus on high/critical issues, medium as advisory |
| 1 | `lenient` | Only critical issues block, rest are suggestions |

### Command Syntax

Add optional `grumpiness: <level>` parameter:

```
/parliament-review
grumpiness: moderate

Review this utility function...
```

Or:

```
/summon-council
grumpiness: lenient

Quick prototype for the dashboard widget...
```

### Reviewer Behaviour Changes

| Aspect | Strict (3) | Moderate (2) | Lenient (1) |
|--------|------------|--------------|-------------|
| Critical issues | Block | Block | Block |
| High issues | Block | Block | Advisory |
| Medium issues | Report | Advisory | Skip |
| Low issues | Report | Skip | Skip |
| Nitpicks | Report | Skip | Skip |

### Implementation

Add to each grumpy reviewer prompt:

```markdown
## Grumpiness Level

Adjust output based on grumpiness parameter:
- **strict** (default): Report all issues, block on high+
- **moderate**: Focus on high/critical, medium as advisory
- **lenient**: Only critical blocks, rest are suggestions

If not specified, assume strict.
```

### Commands to Update

| Command | Change |
|---------|--------|
| `/summon-council` | Parse grumpiness parameter, pass to reviewers |
| `/parliament-review` | Parse grumpiness parameter, adjust output |
| `/summon-grumpy-reviewer` | Parse grumpiness parameter |
| All 9 grumpy-*.md agents | Add grumpiness level handling |

## Acceptance Criteria

- [ ] `grumpiness: strict|moderate|lenient` parameter recognised
- [ ] Default behaviour unchanged (strict)
- [ ] Reviewers adjust output based on level
- [ ] Documentation explains each level
- [ ] README updated with grumpiness option

## Risks

| Risk | Mitigation |
|------|------------|
| Users always use lenient, miss issues | Default is strict; lenient requires explicit opt-in |
| Inconsistent interpretation across reviewers | Clear table in each reviewer prompt |
| Token bloat in agent files | Keep instructions terse (~3 lines) |

## Open Questions

1. Should grumpiness affect which reviewers run, or just their strictness?
2. Should there be a project-level default in .claude/settings.json?
3. Is 3 levels enough, or should there be more granularity?
