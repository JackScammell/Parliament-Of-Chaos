
<img width="1024" height="1024" alt="logo" src="https://github.com/user-attachments/assets/1db1114d-505f-4cf9-807d-6b6054286e41" />

# THE PARLIAMENT OF CHAOS
A Claude Code plugin that summons a council of opinionated AI specialists to review, design, and refine your code through structured debate and iteration.

## What is Parliament of Chaos?

Parliament of Chaos transforms Claude Code into a multi-agent development team. Instead of a single AI assistant, you get access to:

- **Specialist Agents** - Domain experts in backend, security, architecture, testing, and more
- **Grumpy Reviewers** - Deliberately critical reviewers who find flaws others miss
- **A Senior Council** - An orchestrator that coordinates specialists and iterates until quality standards are met

The result: thoroughly reviewed, battle-tested solutions that have survived scrutiny from multiple perspectives.

## Installation

### Step 1: Add the Plugin Source

```
/plugin marketplace add owner/parliament-of-chaos
```

### Step 2: Install the Plugin

```
/plugin install parliament-of-chaos@parliament-of-chaos
```

Once installed, the commands and agents become available in all your Claude Code sessions.

## Quick Start

### Summon the Full Council

For complex tasks requiring multiple perspectives:

```
/summon-council
```

Then describe your task. The council will:
1. Analyse your request and identify relevant domains
2. Dispatch appropriate specialist agents
3. Run outputs through grumpy reviewers
4. Iterate until all reviewers approve

### Summon a Grumpy Reviewer

For quick, ruthless code review:

```
/summon-grumpy-reviewer
```

Paste your code or describe what needs review. You will receive structured feedback on correctness, readability, structure, and maintainability.

## Available Agents

### Specialist Agents

| Agent | Domain |
|-------|--------|
| backend-goblin | Backend performance and optimisation |
| system-architect | System design and architecture |
| security-knight | Security assessment and hardening |
| data-warlock | Database design and query optimisation |
| api-keeper | API design and contracts |
| test-prophet | Testing strategy and coverage |
| ui-ux-guru | UI/UX and accessibility |
| pipeline-engineer | CI/CD and DevOps |
| doc-bard | Documentation |
| package-wizard | Dependencies and versioning |
| resilience-tamer | Error handling and failure modes |

### Grumpy Reviewers

| Agent | Focus |
|-------|-------|
| grumpy-code-reviewer | General code quality |
| grumpy-standards-enforcer | Standards compliance |
| grumpy-architecture-skeptic | Architecture decisions |
| grumpy-maintainability-curmudgeon | Long-term maintainability |
| grumpy-security-nag | Security nitpicks |
| grumpy-performance-troll | Performance nitpicks |

## Documentation

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)

## How It Works

Parliament of Chaos uses Claude Code's plugin system to inject specialised agent personas and slash commands into your sessions. When you invoke `/summon-council`, the Senior Council orchestrator:

1. **Analyses** your request to identify which domains are relevant
2. **Selects** appropriate specialist agents for the task
3. **Delegates** work to each specialist in parallel
4. **Reviews** all outputs through the panel of grumpy reviewers
5. **Iterates** on feedback, routing fixes back to specialists
6. **Synthesises** the final solution once all reviewers approve

This creates a rigorous, multi-pass review process that catches issues a single reviewer would miss.

## License

MIT
