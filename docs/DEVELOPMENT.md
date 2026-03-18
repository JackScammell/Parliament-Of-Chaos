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
pip install -r requirements.txt

# Install development dependencies (if you create requirements-dev.txt)
# pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
# Run tests to verify everything works
python -m pytest tests/ -v

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
3. **Mark src as Sources Root**: Right-click `src` → Mark Directory as → Sources Root

---

## Project Structure

```
Parliament-Of-Chaos/
├── .claude/                          # Claude Code plugin files
│   ├── agents/parliament-of-chaos/   # Agent definitions (30 agents)
│   └── commands/parliament-of-chaos/ # Command definitions (30 commands)
│
├── src/                              # Python source code
│   └── deliberation/                 # Deliberation system
│       ├── core/                     # Core modules
│       │   ├── context_manager.py   # Context optimization
│       │   ├── state_engine.py      # Debate state management
│       │   ├── token_counter.py     # Token counting and monitoring
│       │   ├── statement_pruner.py  # Statement deduplication/pruning
│       │   └── vector_memory.py     # Semantic memory storage
│       ├── agents/                   # Agent implementations
│       ├── schemas/                  # Pydantic schemas
│       └── __init__.py
│
├── tests/                            # Test files
│   ├── test_schemas.py               # Schema validation tests
│   ├── test_token_counter.py        # Token counting tests
│   ├── test_statement_pruner.py     # Pruning logic tests
│   └── ...
│
├── docs/                             # Documentation
│   ├── installation.md               # Installation guide
│   ├── usage.md                      # Usage guide
│   ├── API_REFERENCE.md             # Python API reference
│   ├── DELIBERATION_SYSTEM.md       # System architecture
│   └── ...
│
├── examples/                         # Example scripts
│   └── token_reduction_example.py   # Token optimization demo
│
├── CONTRIBUTING.md                   # Contribution guidelines
├── CHANGELOG.md                      # Version history
├── README.md                         # Project overview
├── requirements.txt                  # Python dependencies
└── .gitignore                        # Git ignore rules
```

### Key Directories

- **`.claude/`**: Claude Code plugin agent and command definitions (Markdown files)
- **`src/deliberation/`**: Python implementation of the deliberation system
- **`tests/`**: Unit and integration tests
- **`docs/`**: User-facing documentation
- **`examples/`**: Executable example scripts

---

## Running Tests

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_schemas.py -v
```

### Run Specific Test

```bash
python -m pytest tests/test_schemas.py::test_statement_validation -v
```

### Run with Coverage

```bash
# Install coverage tool first
pip install pytest-cov

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html  # On Mac/Linux
# start htmlcov/index.html  # On Windows
```

### Run Tests in Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode (auto-reruns on file changes)
ptw tests/
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
black src/ tests/

# Check formatting without making changes
black src/ tests/ --check
```

### Type Checking

Use **mypy** for static type checking:

```bash
# Install mypy
pip install mypy

# Run type checker
mypy src/

# With more strict options
mypy src/ --strict
```

### Linting

Use **flake8** for code linting:

```bash
# Install flake8
pip install flake8

# Run linter
flake8 src/ tests/

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

2. **Add command definition** following the template in [CONTRIBUTING.md](CONTRIBUTING.md)

3. **Update documentation**:
   - Add to README.md commands table
   - Add to installation.md commands list
   - Add to usage.md with examples

4. **Add tests** if command has Python logic

5. **Create PR** with the new command

### Adding New Python Functionality

1. **Create module file**:
   ```bash
   touch src/deliberation/core/my_module.py
   ```

2. **Write implementation** with type hints and docstrings

3. **Create test file**:
   ```bash
   touch tests/test_my_module.py
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
   pip install -r requirements.txt
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
3. **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`
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
2. **Review examples** in `examples/`
3. **Search GitHub Issues** for similar problems
4. **Create a new issue** with the `question` label
5. **Reach out** to maintainers

---

**Happy coding!** 🚀
