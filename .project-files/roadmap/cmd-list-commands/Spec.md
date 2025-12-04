# Spec: cmd-list-commands

## What

A command that displays all Parliament of Chaos slash commands with their descriptions, helping users discover available functionality.

## Why

- Users need to know what commands exist beyond `/list-agents`
- Currently 11 commands with no single place to view them all
- Mirrors the discoverability provided by `/list-agents` for agents

## Requirements

1. Read all `.claude/commands/parliament-of-chaos/*.md` files
2. Extract command name (from filename) and description (first non-heading paragraph or summary)
3. Group commands by category:
   - **Project Planning**: plan-project, project-status, roadmap-add-item, roadmap-item-scope, implement-task-list
   - **Agent Invocation**: summon-council, summon-specialist, summon-grumpy-reviewer, parliament-review
   - **Discovery**: list-agents, explain-agent, list-commands (this one)
4. Display in table format with command name and description
5. List alphabetically within each category

## Technical Approach

Follow the same pattern as `list-agents.md`:
- Simple markdown command file (~25-30 lines)
- Clear process steps
- Example output structure
- No complex logic - Claude handles the reading/parsing

## Dependencies

None - standalone command

## Acceptance Criteria

- [ ] Command file created at `.claude/commands/parliament-of-chaos/list-commands.md`
- [ ] Running `/list-commands` displays all 12 commands (including itself)
- [ ] Commands grouped into 3 categories
- [ ] Each command shows name and brief description
- [ ] Follows optimization patterns (under 35 lines)

## Edge Cases

- New commands added later should be auto-discovered
- Command without clear description: use first sentence of file
- Self-reference: list-commands should include itself in Discovery category
