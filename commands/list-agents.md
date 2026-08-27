---
description: Display all Parliament of Chaos agents grouped by category
effort: low
---

# List Agents

Display all Parliament of Chaos agents grouped by category.

## Process

1. Read all `agents/*.md` files
2. Extract name and description from YAML frontmatter
3. Group by category:
   - **Orchestrators**: senior-council, deliberation-conductor
   - **Planning**: project-oracle, scope-weaver
   - **Utility**: task-executor (its own role in `.claude/rules/agent-standards.md` and `scripts/ci/conformance.py` — not a planning agent)
   - **Specialists**: All non-grumpy, non-planning, non-utility agents
   - **Grumpy Reviewers**: All grumpy-* agents

## Output

```
## Orchestrators (2)
| Agent | Description |

## Planning Agents (2)
| Agent | Description |

## Utility (1)
| Agent | Description |

## Specialists (16)
| Agent | Description |

## Grumpy Reviewers (12)
| Agent | Description |
```

List agents alphabetically within each category. The five subtotals sum to the 33-agent fleet.

## Notes

- Not the same as Claude Code's built-in `/list-agents` (added upstream in v2.1.239, which lists live teammate agents in the session). `/chaos:list-agents` lists the Parliament fleet definitions.
