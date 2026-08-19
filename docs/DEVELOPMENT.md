# Development Guide

This guide covers setting up a development environment for Parliament of Chaos and contributing to the project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Debugging](#debugging)
- [Common Development Tasks](#common-development-tasks)
- [Release Process](#release-process)

---

## Prerequisites

### Required Software

- **Python 3.8+** - Core language
- **pip** - Package manager
- **git** - Version control
- **Claude Code CLI** (optional) - For plugin functionality testing

### Recommended Tools

- **pytest** - Testing framework (installed via requirements.txt)
- **black** - Code formatter (optional)
- **mypy** - Type checker (optional)
- **VS Code** or **PyCharm** - IDEs with Python support

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first, then clone your fork
git clone https://github.com/YOUR_USERNAME/Parliament-Of-Chaos.git
cd Parliament-Of-Chaos
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r reference/requirements.txt

# Install development dependencies (if you create requirements-dev.txt)
# pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
# Run tests to verify everything works
python -m pytest reference/tests/ -v

# Should see output like:
# ======================== test session starts ========================
# collected XX items
# tests/test_schemas.py::test_statement_validation PASSED
# ...
# ======================== XX passed in X.XXs =========================
```

---

## Development Environment

### Environment Variables

Create a `.env` file in the project root for local configuration:

```bash
# .env
PYTHONPATH=.
DEBUG=true
TEST_MODE=true
```

Add `.env` to `.gitignore` to avoid committing secrets.

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true
}
```

#### PyCharm

1. **Set Interpreter**: File → Settings → Project → Python Interpreter → Add → Existing Environment → Select `venv/bin/python`
2. **Enable pytest**: Settings → Tools → Python Integrated Tools → Testing → Default test runner: pytest
3. **Mark src as Sources Root**: Right-click the repository root → Mark Directory as → Sources Root (the reference package imports as `reference.deliberation`)

---

## Project Structure

```
Parliament-Of-Chaos/
├── .claude/                          # Project rules only (not plugin sources)
│   └── rules/                        # agent-standards, governance, output-standards
├── .claude-plugin/
│   ├── plugin.json                   # Plugin manifest (version 1.23.0)
│   └── marketplace.json              # Marketplace metadata
├── agents/                           # 33 agent definitions (2 orchestrators, 2 planning, 16 specialists, 12 grumpy reviewers, 1 utility)
├── commands/                         # 66 slash commands across 15 categories
│   ├── manifest.yaml                 # Source-of-truth registry — reconciled by /parliament-doctor
│   └── <66 .md files>
│
├── src/                              # Live plugin sources
│   └── hooks/                        # Hook scripts (_common.sh, log_event.sh, notify_teams.sh, log_debate_completion.sh)
│
├── reference/                        # NON-EXECUTING Python reference implementation (see reference/README.md)
│   ├── deliberation/                 # Deliberation engine design study
│   │   ├── core/                     # context_manager, state_engine, token_counter, statement_pruner, vector_memory, …
│   │   ├── agents/                   # Agent implementations
│   │   └── models/                   # Pydantic schemas
│   ├── tests/                        # Unit tests for the reference code
│   ├── examples/                     # Example scripts
│   └── requirements.txt              # Python dependencies for the reference code
│
├── docs/                             # Documentation
│   ├── installation.md               # Installation guide
│   ├── usage.md                      # Usage guide
│   ├── API_REFERENCE.md             # Python API reference (documents reference/, non-executing)
│   ├── DELIBERATION_SYSTEM.md       # System architecture
│   └── ...
│
├── CONTRIBUTING.md                   # Contribution guidelines
├── CHANGELOG.md                      # Version history
├── README.md                         # Project overview
└── .gitignore                        # Git ignore rules
```

### Key Directories

- **`agents/`**: 33 agent definitions (Markdown with YAML frontmatter)
- **`commands/`**: 66 command definitions plus `manifest.yaml` (the source-of-truth registry)
- **`.claude/rules/`**: Project rules (agent-standards, governance, output-standards) — loaded via the `InstructionsLoaded` hook
- **`.claude-plugin/`**: Plugin manifest and marketplace metadata (version must stay in sync)
- **`src/hooks/`**: Hook scripts (`_common.sh`, `log_event.sh`, `notify_teams.sh`, `log_debate_completion.sh`) — the only executable code the plugin ships
- **`reference/`**: **Non-executing** Python reference implementation of the deliberation system, with its own tests and examples — see `reference/README.md`
- **`docs/`**: User-facing documentation

---

## Running Tests

### Run All Tests

```bash
python -m pytest reference/tests/ -v
```

### Run Specific Test File

```bash
python -m pytest reference/tests/test_schemas.py -v
```

### Run Specific Test

```bash
python -m pytest reference/tests/test_schemas.py::test_statement_validation -v
```

### Run with Coverage

```bash
# Install coverage tool first
pip install pytest-cov

# Run with coverage report
python -m pytest reference/tests/ --cov=reference --cov-report=html

# View report
open htmlcov/index.html  # On Mac/Linux
# start htmlcov/index.html  # On Windows
```

### Run Tests in Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode (auto-reruns on file changes)
ptw reference/tests/
```

### Test Output Interpretation

```bash
# PASSED - Test succeeded ✅
# FAILED - Test failed ❌
# SKIPPED - Test was skipped ⏭️
# ERROR - Test encountered an error 🔥
```

---

## Code Quality

### Code Formatting

Use **black** for consistent code formatting:

```bash
# Install black
pip install black

# Format all Python files
black reference/

# Check formatting without making changes
black reference/ --check
```

### Type Checking

Use **mypy** for static type checking:

```bash
# Install mypy
pip install mypy

# Run type checker
mypy reference/

# With more strict options
mypy reference/ --strict
```

### Linting

Use **flake8** for code linting:

```bash
# Install flake8
pip install flake8

# Run linter
flake8 reference/

# With specific rules
flake8 src/ --max-line-length=100 --ignore=E501
```

### Pre-commit Hooks

Set up pre-commit hooks to run checks automatically:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install

# Now hooks run automatically on git commit
```

---

## Debugging

### Print Debugging

```python
# Add debug prints
print(f"Debug: statement = {statement}")
print(f"Debug: tokens = {counter.count_tokens(text)}")
```

### Python Debugger (pdb)

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use Python 3.7+ built-in
breakpoint()
```

**Common pdb commands**:
- `n` - Next line
- `s` - Step into function
- `c` - Continue execution
- `p variable` - Print variable value
- `l` - List source code
- `q` - Quit debugger

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

Press F5 to start debugging.

---

## Common Development Tasks

### Adding a New Agent

1. **Create agent file**:
   ```bash
   touch agents/my-new-agent.md
   ```

2. **Add agent definition** following the template in [CONTRIBUTING.md](CONTRIBUTING.md)

3. **Update documentation**:
   - Add to README.md agents table
   - Add to installation.md agent list
   - Add to usage.md if applicable

4. **Create PR** with the new agent

### Adding a New Command

1. **Create command file**:
   ```bash
   touch commands/my-new-command.md
   ```

2. **Add command definition** following the template in [CONTRIBUTING.md](../CONTRIBUTING.md), including the `effort:` frontmatter field.

3. **Register in `commands/manifest.yaml`** — add a new entry with `name`, `status: active`, `owner`, `skill_surface`, `effort`, and `category`. Releases are gated on `/parliament-doctor --strict`, which fails if the file and manifest disagree.

4. **Update documentation**:
   - Add to README.md commands table (pick the correct category section)
   - Add to docs/usage.md overview table
   - If introducing a new category, extend `categories:` in the manifest and docs/installation.md category list

5. **Run `/parliament-doctor`** to verify no drift (no orphans, ghosts, hidden skills, or leaked skills).

6. **Add tests** if the command has Python logic.

7. **Create PR** with the new command, manifest entry, and documentation.

### Adding New Python Functionality

1. **Create module file**:
   ```bash
   touch reference/deliberation/core/my_module.py
   ```

2. **Write implementation** with type hints and docstrings

3. **Create test file**:
   ```bash
   touch reference/tests/test_my_module.py
   ```

4. **Write tests** for all functions

5. **Run tests** to ensure they pass

6. **Update API documentation** in `docs/API_REFERENCE.md`

7. **Create PR**

### Updating Dependencies

1. **Add dependency** to `requirements.txt`:
   ```
   new-package>=1.0.0
   ```

2. **Install dependency**:
   ```bash
   pip install -r reference/requirements.txt
   ```

3. **Test thoroughly** to ensure compatibility

4. **Update documentation** if needed

5. **Create PR** with dependency change

---

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Creating a Release

1. **Update CHANGELOG.md**:
   - Move items from [Unreleased] to new version section
   - Add release date
   - Update comparison links

2. **Update version** in `.claude-plugin/marketplace.json`:
   ```json
   {
     "version": "1.1.0"
   }
   ```

3. **Commit changes**:
   ```bash
   git add CHANGELOG.md .claude-plugin/marketplace.json
   git commit -m "Release version 1.1.0"
   ```

4. **Create tag**:
   ```bash
   git tag -a v1.1.0 -m "Version 1.1.0"
   git push origin v1.1.0
   ```

5. **Create GitHub Release**:
   - Go to GitHub Releases
   - Click "Draft a new release"
   - Select the tag
   - Add release notes from CHANGELOG
   - Publish release

6. **Announce release** (optional):
   - Update README.md if needed
   - Notify users of update availability

---

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to .env file
echo "PYTHONPATH=." >> .env
```

### Test Failures

If tests fail unexpectedly:

1. **Run single test** to isolate issue
2. **Check for stale .pyc files**: `find . -name "*.pyc" -delete`
3. **Reinstall dependencies**: `pip install -r reference/requirements.txt --force-reinstall`
4. **Clear pytest cache**: `rm -rf .pytest_cache`

### Git Issues

If you encounter git issues:

```bash
# Sync with upstream
git fetch origin
git rebase origin/main

# Resolve conflicts if any
# Then force push (only on feature branches!)
git push --force-with-lease
```

---

## Additional Resources

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [API_REFERENCE.md](API_REFERENCE.md) - Python API documentation
- [Python Testing with pytest](https://docs.pytest.org/) - Testing framework docs
- [Pydantic Documentation](https://docs.pydantic.dev/) - Schema validation
- [Black Code Formatter](https://black.readthedocs.io/) - Code formatting

---

## Getting Help

If you need help with development:

1. **Check documentation** in `docs/`
2. **Review examples** in `reference/examples/`
3. **Search GitHub Issues** for similar problems
4. **Create a new issue** with the `question` label
5. **Reach out** to maintainers

---

**Happy coding!** 🚀
