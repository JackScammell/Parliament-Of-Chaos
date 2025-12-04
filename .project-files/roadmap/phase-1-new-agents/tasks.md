# Tasks: Phase 1 - New Specialist Agents

## Status: Complete

## Overview

Create 5 new token-optimised specialist agents and integrate them with the senior council and documentation.

---

## Tasks

### Agent Creation

- [x] **Create migration-monk.md** (32 lines)
  - Location: `.claude/agents/parliament-of-chaos/migration-monk.md`
  - Color: cyan
  - Follow data-warlock template structure
  - Focus: schema migrations, data transformations, rollback strategies

- [x] **Create dependency-detective.md** (32 lines)
  - Location: `.claude/agents/parliament-of-chaos/dependency-detective.md`
  - Color: yellow
  - Follow data-warlock template structure
  - Focus: vulnerability chains, license compliance, upgrade paths

- [x] **Create refactor-ranger.md** (32 lines)
  - Location: `.claude/agents/parliament-of-chaos/refactor-ranger.md`
  - Color: green
  - Follow data-warlock template structure
  - Focus: code smells, refactoring patterns, incremental improvements

- [x] **Create config-curator.md** (32 lines)
  - Location: `.claude/agents/parliament-of-chaos/config-curator.md`
  - Color: blue
  - Follow data-warlock template structure
  - Focus: environment config, secrets management, feature flags

- [x] **Create observability-oracle.md** (32 lines)
  - Location: `.claude/agents/parliament-of-chaos/observability-oracle.md`
  - Color: magenta
  - Follow data-warlock template structure
  - Focus: logging, metrics, tracing, alerting

### Integration

- [x] **Update senior-council.md specialist list**
  - Add: migration-monk, dependency-detective, refactor-ranger, config-curator, observability-oracle
  - Update the Agent Selection line in Responsibilities section

- [x] **Update README.md**
  - Add 5 new agents to Specialist Agents table
  - Update count from "Specialist Agents (11)" to "Specialist Agents (16)"
  - Update total agent count from "21 Agents" to "26 Agents"

### Verification

- [x] **Verify agent file structure**
  - Each file has valid YAML frontmatter (name, description, model, color)
  - Each file is 32 lines (within 30-35 target)
  - Each file follows Focus Areas / Process / Output pattern

- [ ] **Test agent invocation**
  - Verify `@migration-monk` responds appropriately
  - Verify `@dependency-detective` responds appropriately
  - Verify `@refactor-ranger` responds appropriately
  - Verify `@config-curator` responds appropriately
  - Verify `@observability-oracle` responds appropriately

---

## Notes

- All agents must use `model: inherit` to use the parent conversation's model
- Colors chosen to avoid conflicts with existing agents
- Line count includes YAML frontmatter (8 lines) + content (24 lines)
- Reference template: `data-warlock.md` at 31 lines

## Definition of Done

1. All 5 agent files created and line-count verified ✓
2. senior-council.md updated with new specialists ✓
3. README.md updated with new agents and counts ✓
4. All agents respond when invoked with `@agent-name` (manual test required)
