# Project Outline: Parliament of Chaos

## Vision

A Claude Code plugin that provides a council of specialist AI agents collaborating on software engineering tasks, with all work reviewed by a panel of grumpy critics who iterate until quality standards are met. The goal is to give open source developers access to a full team of opinionated experts through a single, portable plugin.

## Problem Statement

- **Who experiences this problem?** Developers using Claude Code who want comprehensive, multi-perspective feedback on their work without manually prompting for different viewpoints.
- **How are they currently solving it?** Writing custom prompts, switching between contexts, or accepting single-perspective responses.
- **What's the cost of not solving it?** Missed edge cases, security vulnerabilities, performance issues, and inconsistent code quality that a diverse "team" of reviewers would catch.

## Goals

| Goal | Metric | Target |
|------|--------|--------|
| Comprehensive reviews | Perspectives covered per review | 6+ (all grumpy reviewers) |
| Easy adoption | Time from install to first use | < 5 minutes |
| Portable across projects | Installation method | Single marketplace install |
| Community contribution | GitHub stars / forks | Establish baseline, grow 20% monthly |

## Non-Goals

- Custom agent creation UI (users edit markdown files directly)
- Non-Claude Code integrations (VS Code extension, JetBrains, etc.)
- Mobile app support
- Paid/premium tiers (fully open source)

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Lead | @jack | Day-to-day ownership, architecture decisions |
| Contributors | Open source community | Implementation, feedback, new agents |
| Users | Claude Code developers | Usage, bug reports, feature requests |

## Constraints

- Must work within Claude Code plugin architecture
- Agents defined as markdown files in `.claude/agents/`
- Commands defined as markdown files in `.claude/commands/`
- No external runtime dependencies (pure Claude Code)

## Success Criteria

- [ ] All v1.1 agents implemented and documented
- [ ] All v1.1 commands functional
- [ ] Plugin installable from Claude Code marketplace
- [ ] README with clear usage examples
- [ ] At least 3 external users have tried it

---

**Related Documents**:
- [Feature Implementation](./feature-implementation.md)
- [Roadmap](./Roadmap.md)
