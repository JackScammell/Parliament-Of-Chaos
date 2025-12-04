# Roadmap: Parliament of Chaos

## Current Status

**Last Updated**: 2025-12-04

**Current Phase**: v1.1 Development

**Overall Progress**: 17 of 20 items complete

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
| [agent-token-optimization](./roadmap/agent-token-optimization/) | Complete | None |

**Milestone**: All existing agents optimized for minimal context footprint

---

### Phase 1: New Specialist Agents

_Goal: Expand specialist coverage to new domains_

| Item | Status | Dependencies |
|------|--------|--------------|
| [migration-monk](./roadmap/phase-1-new-agents/) | Complete | None |
| [dependency-detective](./roadmap/phase-1-new-agents/) | Complete | None |
| [refactor-ranger](./roadmap/phase-1-new-agents/) | Complete | None |
| [config-curator](./roadmap/phase-1-new-agents/) | Complete | None |
| [observability-oracle](./roadmap/phase-1-new-agents/) | Complete | None |

**Milestone**: All new specialists available for council summons

---

### Phase 2: New Grumpy Reviewers

_Goal: Add specialized review perspectives_

| Item | Status | Dependencies |
|------|--------|--------------|
| [grumpy-accessibility-auditor](./roadmap/phase-2-grumpy-reviewers/) | Complete | None |
| [grumpy-documentation-pedant](./roadmap/phase-2-grumpy-reviewers/) | Complete | None |
| [grumpy-testing-tyrant](./roadmap/phase-2-grumpy-reviewers/) | Complete | None |

**Milestone**: Grumpy council expanded to 9 reviewers

---

### Phase 3: New Commands

_Goal: Improve discoverability and direct agent access_

| Item | Status | Dependencies |
|------|--------|--------------|
| [cmd-list-agents](./roadmap/phase-3-new-commands/) | Complete | None |
| [cmd-explain-agent](./roadmap/phase-3-new-commands/) | Complete | None |
| [cmd-summon-specialist](./roadmap/phase-3-new-commands/) | Complete | None |
| [cmd-parliament-review](./roadmap/phase-3-new-commands/) | Complete | grumpy reviewers |
| [cmd-roadmap-add-item](./roadmap/cmd-roadmap-add-item/) | Complete | None |
| command-optimization | Complete | None |
| [cmd-list-commands](./roadmap/cmd-list-commands/) | Complete | None |

**Milestone**: Users can discover, understand, and directly invoke agents

---

### Phase 4: Quality of Life Features

_Goal: Enhanced workflow and configurability_

| Item | Status | Dependencies |
|------|--------|--------------|
| [review-report-export](./roadmap/review-report-export/) | Scoped | None |
| [configurable-grumpiness](./roadmap/configurable-grumpiness/) | Scoped | None |
| [conflict-resolution](./roadmap/conflict-resolution/) | Complete | senior-council agent |
| [agent-memory-context](./roadmap/agent-memory-context/) | Scoped | None |

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
cmd-list-commands ◄─── (standalone)

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
| 2025-12-04 | Completed conflict-resolution | Priority-based conflict handling for reviewer disagreements |
| 2025-12-04 | Added cmd-list-commands | Command discoverability - lists all 12 commands by category |
| 2025-12-04 | Completed Phase 3 (new commands + optimization) | 4 new commands, 2 optimized (147→54 lines, 63% reduction) |
| 2025-12-04 | Completed agent-token-optimization | Reduced 21 agents by 22.5% lines, 34.5% characters |
| 2025-12-04 | Added Phase 0 with agent-token-optimization | Optimize existing agents before adding new ones |
| 2025-12-04 | Initial v1.1 roadmap created | Project planning session |

---

**Related Documents**:
- [Project Outline](./project-outline.md)
- [Feature Implementation](./feature-implementation.md)
