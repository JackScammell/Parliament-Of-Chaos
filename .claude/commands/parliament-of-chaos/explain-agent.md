# Explain Agent

Explain what a specific agent does and when to use it.

**Argument**: Agent name (e.g., `security-knight`)

## Process

1. Read `.claude/agents/parliament-of-chaos/$ARGUMENTS.md`
2. If not found, list available agents
3. Extract: name, description, focus areas, process, output format

## Output

```
# Agent: [name]
[description from frontmatter]

## When to Use
- Scenarios where this agent excels
- vs similar agents (if applicable)

## Focus Areas
- [from agent file]

## What You Get
- Output format and structure
```

## Error Handling

If agent not found:
```
Agent "[name]" not found.

Available agents:
- [list similar or all agents]

Try: /explain-agent [valid-name]
```
