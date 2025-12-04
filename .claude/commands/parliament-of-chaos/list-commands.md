# List Commands

Display all Parliament of Chaos slash commands grouped by category.

## Process

1. Read all `.claude/commands/parliament-of-chaos/*.md` files
2. Extract command name (filename) and description (first paragraph after title)
3. Group by category:
   - **Project Planning**: plan-project, project-status, roadmap-add-item, roadmap-item-scope, implement-task-list
   - **Agent Invocation**: summon-council, summon-specialist, summon-grumpy-reviewer, parliament-review
   - **Discovery**: list-agents, explain-agent, list-commands

## Output

```
## Project Planning (5)
| Command | Description |

## Agent Invocation (4)
| Command | Description |

## Discovery (3)
| Command | Description |
```

List commands alphabetically within each category.
