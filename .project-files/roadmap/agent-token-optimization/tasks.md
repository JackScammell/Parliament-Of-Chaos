# Tasks: Agent Token Optimization

## Status: Complete

## Tasks

### Preparation
- [x] Document current token counts for all 21 agents (baseline measurement)
- [x] Create before/after test prompts for each agent category

### Tier 1: Compact Agents (17 agents, light optimization)
- [x] Optimize grumpy-code-reviewer
- [x] Optimize grumpy-standards-enforcer
- [x] Optimize grumpy-architecture-skeptic
- [x] Optimize grumpy-maintainability-curmudgeon
- [x] Optimize grumpy-security-nag
- [x] Optimize grumpy-performance-troll
- [x] Optimize data-warlock
- [x] Optimize doc-bard
- [x] Optimize resilience-tamer
- [x] Optimize security-knight
- [x] Optimize pipeline-engineer
- [x] Optimize system-architect
- [x] Optimize test-prophet
- [x] Optimize api-keeper
- [x] Optimize backend-goblin
- [x] Optimize ui-ux-guru
- [x] Optimize package-wizard

### Tier 2: Medium Agent
- [x] Optimize senior-council (target: 67 → ~45 lines) ✓ Achieved 32 lines

### Tier 3: Large Agents (significant reduction)
- [x] Optimize scope-weaver (target: 110 → ~70 lines) ✓ Achieved 57 lines
- [x] Optimize project-oracle (target: 116 → ~75 lines) ✓ Achieved 59 lines
- [x] Optimize task-executor (target: 117 → ~75 lines) ✓ Achieved 68 lines

### Validation
- [x] Test each optimized agent with sample prompts
- [x] Verify senior-council orchestration still works
- [x] Document final token counts (after measurement)
- [x] Create optimization guidelines for future agents

## Notes

**Optimization patterns applied:**
1. Removed "You are..." preambles where obvious from name
2. Used imperative verbs, not passive descriptions
3. Collapsed multi-sentence explanations into bullet points
4. Removed markdown template examples (kept structure, dropped filler)
5. Eliminated phrases like "Your responsibilities include..." - just listed them
6. Trusted Claude to understand context - didn't over-explain

**Preserved:**
- YAML frontmatter structure
- Output format requirements
- Agent personality/tone
- Cross-references to other agents
