---
description: Review Claude Code changelog and propose new features for Parliament of Chaos
context: fork
agent: deliberation-conductor
---

# Changelog Review

Fetch the latest Claude Code changelog, identify relevant new features, and run a structured deliberation to propose implementation plans for Parliament of Chaos.

## Usage

```
/changelog-review [--mode fast|consensus|deep] [--focus <area>]
```

**Examples**:
```
/changelog-review
/changelog-review --mode deep
/changelog-review --focus hooks
/changelog-review --focus agents
```

## Options

- `--mode` (optional): Deliberation mode for evaluating features
  - `fast`: Quick 3-round assessment (default)
  - `consensus`: Balanced 5-round evaluation
  - `deep`: Thorough 7-10 round analysis

- `--focus` (optional): Filter to a specific area
  - `hooks`: New hook events and capabilities
  - `agents`: Agent system changes (frontmatter, teams, isolation)
  - `plugins`: Plugin system enhancements
  - `commands`: New CLI commands and features
  - `performance`: Performance and token optimisations
  - `all`: Everything (default)

## Process

1. **Fetch Changelog**
   - Fetch https://code.claude.com/docs/en/changelog using WebFetch
   - Extract all entries with dates and feature descriptions
   - Focus on features relevant to plugin/agent systems

2. **Categorise Features**
   Group new capabilities into:
   - **Agent & Team Features**: frontmatter, memory, isolation, teams
   - **Plugin System**: persistent state, settings, variables
   - **Hook System**: new events, HTTP hooks, hook context
   - **Commands & UX**: new slash commands, effort levels
   - **Performance & Config**: model overrides, memory, token optimisation

3. **Compare Against Current State**
   - Read current `CHANGELOG.md` to identify what Parliament already implements
   - Read `.claude/rules/agent-standards.md` for current agent standards
   - Read `settings.json` for current hook configuration
   - Identify gaps between Claude Code capabilities and Parliament features

4. **Deliberation**
   Run a structured debate with relevant Parliament agents:
   - **system-architect**: Evaluate architectural impact
   - **config-curator**: Evaluate configuration implications
   - **pipeline-engineer**: Evaluate deployment/CI implications
   - **refactor-ranger**: Evaluate code quality opportunities
   - **grumpy-architecture-skeptic**: Challenge proposals
   - **grumpy-maintainability-curmudgeon**: Challenge complexity

5. **Produce Implementation Plan**
   Generate a phased proposal with:
   - Feature rankings by impact/effort ratio
   - Specific agent/command/hook changes needed
   - Dependencies and implementation order
   - Features to avoid and why

## Output

```markdown
# Claude Code Changelog Review

**Reviewed**: [date range of changelog entries]
**Current Parliament Version**: [version from plugin.json]
**New Features Found**: N relevant / M total

## Feature Categories

### Already Implemented
- [features Parliament already leverages]

### Recommended for Next Release
| Priority | Feature | Impact | Effort | Phase |
|----------|---------|--------|--------|-------|
| 1 | ... | High | Low | 1 |

### Deferred / Not Applicable
- [features not relevant to Parliament]

## Deliberation Summary
[condensed debate results with agent positions and vote]

## Proposed Roadmap
### Phase 1: [theme]
- [specific changes]

### Phase 2: [theme]
- [specific changes]

## Next Steps
- Run `/roadmap-add-item` for approved items
- Run `/roadmap-item-scope` to detail specifications
```

## Integration

This command is designed to be run regularly (monthly or after major Claude Code releases) to keep Parliament of Chaos aligned with the latest platform capabilities. It:

1. Automates the manual process of reading release notes
2. Cross-references against current implementation
3. Uses the Parliament's own deliberation system to evaluate proposals
4. Produces actionable roadmap items ready for `/roadmap-add-item`

## Notes

- Requires internet access to fetch the changelog via WebFetch
- The deliberation uses `--mode fast` by default to keep reviews quick
- For major Claude Code releases, use `--mode deep` for thorough evaluation
- Results can be piped into `/roadmap-add-item` for immediate planning
- Run `/parliament-loop 1w /changelog-review --mode fast` for weekly automated checks
