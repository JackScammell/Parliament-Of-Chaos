# Roadmap: Parliament of Chaos

## Current Status

**Last Updated**: 2024-12-04

**Current Phase**: v1.1 Development

**Overall Progress**: 1 of 18 items complete

---

## Version Overview

```
v1.0 (MVP)                    v1.1 (Current)                 v1.2 (Future)
|------------------------------|------------------------------|
[Complete]                     [New Agents    ]
                               [New Commands  ]
                               [QoL Features  ]
```

---

## v1.1 Roadmap Items

### Phase 0: Agent Optimization

_Goal: Reduce token/context usage across all existing agents while maintaining quality_

| Item | Status | Dependencies |
|------|--------|--------------|
| [agent-token-optimization](./roadmap/agent-token-optimization/) | Not Started | None |

**Milestone**: All existing agents optimized for minimal context footprint

---

### Phase 1: New Specialist Agents

_Goal: Expand specialist coverage to new domains_

| Item | Status | Dependencies |
|------|--------|--------------|
| [migration-monk](./roadmap/migration-monk/) | Not Started | None |
| [dependency-detective](./roadmap/dependency-detective/) | Not Started | None |
| [refactor-ranger](./roadmap/refactor-ranger/) | Not Started | None |
| [config-curator](./roadmap/config-curator/) | Not Started | None |
| [observability-oracle](./roadmap/observability-oracle/) | Not Started | None |

**Milestone**: All new specialists available for council summons

---

### Phase 2: New Grumpy Reviewers

_Goal: Add specialized review perspectives_

| Item | Status | Dependencies |
|------|--------|--------------|
| [grumpy-accessibility-auditor](./roadmap/grumpy-accessibility-auditor/) | Not Started | None |
| [grumpy-documentation-pedant](./roadmap/grumpy-documentation-pedant/) | Not Started | None |
| [grumpy-testing-tyrant](./roadmap/grumpy-testing-tyrant/) | Not Started | None |

**Milestone**: Grumpy council expanded to 9 reviewers

---

### Phase 3: New Commands

_Goal: Improve discoverability and direct agent access_

| Item | Status | Dependencies |
|------|--------|--------------|
| [cmd-list-agents](./roadmap/cmd-list-agents/) | Not Started | None |
| [cmd-explain-agent](./roadmap/cmd-explain-agent/) | Not Started | None |
| [cmd-summon-specialist](./roadmap/cmd-summon-specialist/) | Not Started | None |
| [cmd-parliament-review](./roadmap/cmd-parliament-review/) | Not Started | grumpy reviewers |
| [cmd-roadmap-add-item](./roadmap/cmd-roadmap-add-item/) | Complete | None |

**Milestone**: Users can discover, understand, and directly invoke agents

---

### Phase 4: Quality of Life Features

_Goal: Enhanced workflow and configurability_

| Item | Status | Dependencies |
|------|--------|--------------|
| [review-report-export](./roadmap/review-report-export/) | Not Started | None |
| [configurable-grumpiness](./roadmap/configurable-grumpiness/) | Not Started | None |
| [conflict-resolution](./roadmap/conflict-resolution/) | Not Started | senior-council agent |
| [agent-memory-context](./roadmap/agent-memory-context/) | Not Started | None |

**Milestone**: Full v1.1 feature set complete

---

## Dependencies Graph

```
migration-monk ─────────────────────┐
dependency-detective ───────────────┤
refactor-ranger ────────────────────┼──► cmd-summon-specialist
config-curator ─────────────────────┤
observability-oracle ───────────────┘

grumpy-accessibility-auditor ───────┐
grumpy-documentation-pedant ────────┼──► cmd-parliament-review
grumpy-testing-tyrant ──────────────┘

cmd-list-agents ◄─── (standalone)
cmd-explain-agent ◄─── (standalone)

review-report-export ◄─── (standalone)
configurable-grumpiness ◄─── (standalone)
conflict-resolution ◄─── senior-council (exists)
agent-memory-context ◄─── (standalone)
```

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Agent prompt quality varies | Medium | Medium | Grumpy reviewers review agent prompts too |
| Feature creep | High | High | Strict adherence to v1.1 scope |
| Plugin marketplace requirements change | Medium | Low | Monitor Claude Code updates |
| Agent conflicts/overlapping concerns | Medium | Medium | Clear domain boundaries in agent descriptions |

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2024-12-04 | Added Phase 0 with agent-token-optimization | Optimize existing agents before adding new ones |
| 2024-12-04 | Initial v1.1 roadmap created | Project planning session |

---

**Related Documents**:
- [Project Outline](./project-outline.md)
- [Feature Implementation](./feature-implementation.md)
