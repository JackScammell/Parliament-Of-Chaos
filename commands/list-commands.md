---
description: Display all Parliament of Chaos slash commands grouped by category
effort: low
---

# List Commands

Display all Parliament of Chaos slash commands grouped by category.

## Process

1. Read `commands/manifest.yaml` for the authoritative command list, categories, and statuses
2. For each entry with `skill_surface: true`, resolve the description from the command file's frontmatter
3. Group by category using the manifest's `categories` block
4. Render alphabetically within each category
5. If `commands/manifest.yaml` is missing or unreadable, fall back to scanning `commands/*.md`

## Category Reference (from manifest v1)

- **Project Planning**: plan-project, project-status, roadmap-add-item, roadmap-item-scope, implement-task-list
- **Agent Invocation**: ask-council, summon-council, summon-specialist, summon-grumpy-reviewer, parliament-review
- **Deliberation**: debate-topic, debate-analytics
- **Developer Workflow**: pre-commit-check, format-code, lint-fix, run-tests, security-scan, clean-imports, update-dependencies, dead-code-sweep, update-docs, analyse-queries, git-workflow, scaffold
- **Operations**: parliament-optimize, parliament-webhook, parliament-loop, parliament-monitor, changelog-review, incident, infra-review, retro
- **Codebase Analysis**: onboard-codebase
- **Discovery**: list-agents, explain-agent, list-commands, version, readme, changelog
- **Plugins**: plugin-install, plugin-list
- **Hygiene**: parliament-doctor
- **Quality**: coverage-audit, generate-tests, mutation-test, test-health, track-debt, i18n-audit
- **Release**: cut-release

## Output

```
## Project Planning (5)
| Command | Description |

## Agent Invocation (5)
| Command | Description |

## Deliberation (2)
| Command | Description |

## Developer Workflow (12)
| Command | Description |

## Operations (8)
| Command | Description |

## Codebase Analysis (1)
| Command | Description |

## Discovery (6)
| Command | Description |

## Plugins (2)
| Command | Description |

## Hygiene (1)
| Command | Description |

## Quality (6)
| Command | Description |

## Release (1)
| Command | Description |
```

Commands are listed alphabetically within each category. Only commands with `skill_surface: true` in the manifest are displayed. Commands with `status: deprecated` are shown with a `(deprecated)` tag. Commands with `status: experimental` are shown with an `(experimental)` tag.
