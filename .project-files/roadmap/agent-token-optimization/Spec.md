# Spec: Agent Token Optimization

## What

Refactor all 21 existing Parliament of Chaos agents to minimize token/context usage while maintaining the same quality of output. This is a prerequisite optimization before adding new agents in subsequent phases.

## Why

- **Cost efficiency**: Fewer tokens = lower API costs per agent invocation
- **Context preservation**: Leaner prompts leave more context window for actual work
- **Performance**: Faster response times with smaller prompts
- **Scalability**: Enables adding more agents without context overflow when using multi-agent workflows (e.g., senior-council orchestration)

## Current State Analysis

| Category | Count | Line Range | Notes |
|----------|-------|------------|-------|
| Compact agents | 14 | 32-37 lines | grumpy-*, specialists |
| Medium agents | 3 | 67-117 lines | senior-council, scope-weaver, project-oracle, task-executor |
| Large agents | 4 | 110-117 lines | Planning/orchestration agents |

**Total**: ~990 lines across 21 agents

## Requirements

- [ ] Reduce average agent prompt size by 30-50% without losing functionality
- [ ] Maintain identical output quality and behavior
- [ ] Preserve the personality/tone of each agent (especially grumpy reviewers)
- [ ] Keep structured output formats intact
- [ ] Ensure all cross-references between agents remain valid
- [ ] Document optimization patterns for future agent development

## Technical Approach

### Optimization Strategies

1. **Remove redundant instructions** - Claude already knows how to do many things
2. **Compress verbose descriptions** - Use terse, imperative language
3. **Eliminate obvious implications** - Don't explain what's self-evident
4. **Consolidate duplicate patterns** - Many agents repeat similar structures
5. **Use bullet points over prose** - More information density
6. **Remove example scaffolding** - Reduce markdown template verbosity in prompts

### Agent Categories for Optimization

**Tier 1 - Compact (minimal changes needed)**:
- grumpy-code-reviewer, grumpy-standards-enforcer, grumpy-architecture-skeptic
- grumpy-maintainability-curmudgeon, grumpy-security-nag, grumpy-performance-troll
- data-warlock, doc-bard, resilience-tamer, security-knight
- pipeline-engineer, system-architect, test-prophet, api-keeper
- backend-goblin, ui-ux-guru, package-wizard

**Tier 2 - Medium (moderate optimization)**:
- senior-council (67 lines)

**Tier 3 - Large (significant optimization opportunity)**:
- scope-weaver (110 lines)
- project-oracle (116 lines)
- task-executor (117 lines)

### Constraints

- YAML frontmatter must remain (name, description, model, color)
- Agent description in frontmatter should stay under 280 characters
- No behavioral changes - same inputs should produce equivalent outputs
- Keep markdown formatting for readability during maintenance

## Success Criteria

- [ ] Total line count reduced from ~990 to ~600-700 lines
- [ ] Each agent tested with representative prompts
- [ ] No regression in output quality (manual review)
- [ ] Optimization patterns documented for future agents

## Dependencies

- **Requires**: None (Phase 0 - first item)
- **Affects**: All 21 agent files in `.claude/agents/parliament-of-chaos/`
- **Blocks**: All subsequent phases depend on optimized agents as baseline

## Risks

| Risk | Mitigation |
|------|------------|
| Over-compression loses nuance | Review each agent's output before/after |
| Breaking orchestration flows | Test senior-council workflow end-to-end |
| Personality loss in grumpy agents | Preserve key tone-setting phrases |
