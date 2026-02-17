# Contributing to Parliament of Chaos

Thank you for your interest in contributing to Parliament of Chaos! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Pull Request Process](#pull-request-process)
- [Creating New Agents](#creating-new-agents)
- [Creating New Commands](#creating-new-commands)
- [Community Guidelines](#community-guidelines)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Claude Code CLI (for plugin functionality)
- Basic understanding of multi-agent systems

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Parliament-Of-Chaos.git
   cd Parliament-Of-Chaos
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

Run the test suite to ensure everything is working:

```bash
python -m pytest tests/ -v
```

### Project Structure

```
Parliament-Of-Chaos/
├── .claude/
│   ├── agents/parliament-of-chaos/    # Agent definitions (.md files)
│   └── commands/parliament-of-chaos/  # Command definitions (.md files)
├── src/
│   └── deliberation/                  # Python deliberation system
│       ├── core/                      # Core modules
│       ├── agents/                    # Agent implementations
│       └── schemas/                   # Data schemas
├── tests/                             # Test files
├── docs/                              # Documentation
└── examples/                          # Example scripts
```

---

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports** - Report issues you've encountered
2. **Feature Requests** - Suggest new features or improvements
3. **Code Contributions** - Submit bug fixes or new features
4. **Documentation** - Improve or add documentation
5. **New Agents** - Create new specialist or grumpy reviewer agents
6. **New Commands** - Add new slash commands
7. **Examples** - Provide usage examples

### Reporting Bugs

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, Claude Code version
- **Logs**: Relevant error messages or logs

### Suggesting Features

When suggesting features, please include:

- **Use Case**: Why this feature would be useful
- **Description**: Detailed description of the feature
- **Examples**: How the feature would be used
- **Alternatives**: Other solutions you've considered

---

## Code Style Guidelines

### Python Code

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

Example:
```python
def process_statement(agent_id: str, statement: str, confidence: float) -> DebateStatement:
    """
    Process an agent statement and return a structured DebateStatement.
    
    Args:
        agent_id: Unique identifier for the agent
        statement: The agent's statement text
        confidence: Confidence score between 0.0 and 1.0
        
    Returns:
        A DebateStatement object with validated fields
    """
    # Implementation here
    pass
```

### Agent Definition Files (.md)

Agent files in `.claude/agents/parliament-of-chaos/` should follow this structure:

```markdown
---
name: agent-name
description: Brief one-line description
category: specialist|grumpy-reviewer|planner|orchestrator
expertise: [domain1, domain2]
---

# Agent Name

## Role
Detailed description of the agent's role and responsibilities.

## Expertise
- Specific area 1
- Specific area 2

## When to Use
- Scenario 1
- Scenario 2

## Output Format
What kind of output this agent provides.
```

### Command Definition Files (.md)

Command files in `.claude/commands/parliament-of-chaos/` should follow this structure:

```markdown
---
name: command-name
description: Brief one-line description
category: council|discovery|planning|analytics
---

# /command-name

## Purpose
What this command does and when to use it.

## Usage
```
/command-name [arguments]
```

## Arguments
- `arg1`: Description
- `arg2`: Description (optional)

## Examples
```
/command-name example-value
```

## Output
Description of what the command returns.
```

---

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Test both success and failure cases
- Mock external dependencies

Example:
```python
def test_statement_validation_with_valid_input():
    """Test that valid statements pass validation."""
    statement = DebateStatement(
        agent_id="test-agent",
        position="support",
        argument="Valid argument",
        confidence=0.8
    )
    assert statement.agent_id == "test-agent"
    assert statement.confidence == 0.8
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_schemas.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

---

## Documentation Guidelines

### Documentation Standards

- Use clear, concise language
- Include code examples where applicable
- Keep documentation up to date with code changes
- Use proper Markdown formatting
- Add links to related documentation

### Updating Documentation

When making changes that affect documentation:

1. Update relevant documentation files in `docs/`
2. Update README.md if necessary
3. Update inline code comments and docstrings
4. Add examples to `examples/` if appropriate

---

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest main:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run tests** to ensure everything passes:
   ```bash
   python -m pytest tests/ -v
   ```

3. **Update documentation** if needed

4. **Commit your changes** with clear messages:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Description of changes
   - Related issues
   - Testing performed
   - Documentation updates

4. **Respond to feedback** from reviewers

### PR Review Process

- PRs require at least one approval
- All tests must pass
- Code must follow style guidelines
- Documentation must be updated
- No merge conflicts

---

## Creating New Agents

### Agent Types

1. **Specialist Agents**: Domain experts (e.g., backend, security, testing)
2. **Grumpy Reviewers**: Critical reviewers focused on quality
3. **Planning Agents**: Project planning and scoping
4. **Orchestrators**: Coordinate other agents

### Steps to Create a New Agent

1. **Define the agent's role** and expertise area
2. **Create agent file** in `.claude/agents/parliament-of-chaos/`
3. **Follow the agent template** (see Code Style Guidelines)
4. **Update README.md** to include the new agent
5. **Add tests** if the agent has Python implementation
6. **Submit PR** with agent definition and documentation

---

## Creating New Commands

### Command Categories

1. **Council Commands**: Multi-agent orchestration
2. **Discovery Commands**: Exploration and information
3. **Planning Commands**: Project planning and management
4. **Analytics Commands**: Metrics and insights

### Steps to Create a New Command

1. **Define the command's purpose** and use cases
2. **Create command file** in `.claude/commands/parliament-of-chaos/`
3. **Follow the command template** (see Code Style Guidelines)
4. **Update documentation**:
   - Add to README.md commands table
   - Add to installation.md
   - Add to usage.md with examples
5. **Add tests** for command logic
6. **Submit PR** with command definition and documentation

---

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Assume good intentions

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **Pull Requests**: Code contributions
- **Discussions**: Questions, ideas, and general discussion

### Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Mentioned in release notes
- Credited in documentation (when appropriate)

---

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search GitHub Issues
3. Create a new discussion
4. Reach out to maintainers

---

## License

By contributing to Parliament of Chaos, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Parliament of Chaos!** 🎉
