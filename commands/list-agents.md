---
description: Display all Parliament of Chaos agents grouped by category
---

# List Agents

Display all Parliament of Chaos agents grouped by category.

## Process

1. Read all `agents/*.md` files
2. Extract name and description from YAML frontmatter
3. Group by category:
   - **Orchestrators**: senior-council, deliberation-conductor
   - **Planning**: project-oracle, scope-weaver, task-executor
   - **Specialists**: All non-grumpy, non-planning agents
   - **Grumpy Reviewers**: All grumpy-* agents

## Output

```
## Orchestrators (2)
| Agent | Description |

## Planning Agents (3)
| Agent | Description |

## Specialists (16)
| Agent | Description |

## Grumpy Reviewers (9)
| Agent | Description |
```

List agents alphabetically within each category.
