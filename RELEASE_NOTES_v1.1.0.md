# Release Notes for v1.1.0

## Parliament of Chaos v1.1.0

**Release Date:** 2025-12-05

### 🎉 What's New

Parliament of Chaos v1.1.0 brings major enhancements to the multi-agent development experience with **38% more agents**, **71% more commands**, and comprehensive standards compliance.

---

### ✨ Highlights

#### 🤖 8 New Agents (29 Total)

**New Specialist Agents:**
- 🔄 **migration-monk** - Expert in schema migrations and rollback strategies
- 🔍 **dependency-detective** - Uncovers vulnerability chains and license compliance issues
- ♻️ **refactor-ranger** - Identifies code smells and suggests refactoring patterns
- ⚙️ **config-curator** - Manages environment config, secrets, and feature flags
- 📊 **observability-oracle** - Implements logging, metrics, tracing, and alerting

**New Grumpy Reviewers:**
- ♿ **grumpy-accessibility-auditor** - Enforces WCAG compliance and inclusive design
- 📚 **grumpy-documentation-pedant** - Demands documentation completeness
- 🧪 **grumpy-testing-tyrant** - Ensures comprehensive test coverage and quality

#### 🎮 5 New Commands (12 Total)

**Discovery & Information:**
- `/list-agents` - View all agents grouped by category
- `/list-commands` - Display all commands grouped by category  
- `/explain-agent <agent>` - Get detailed info on what an agent does

**Direct Agent Invocation:**
- `/summon-specialist <agent>` - Directly invoke a specialist for your task
- `/parliament-review` - Full code review using all 9 grumpy reviewers

#### 🛡️ Standards Compliance

All 16 specialist agents now include:
- Requirements to consult official documentation
- Framework-specific pattern verification
- Source citation for recommendations

#### ⚖️ Conflict Resolution Protocol

New priority-based conflict resolution when reviewers disagree:
1. Security (highest priority)
2. Correctness
3. Maintainability
4. Performance (lowest priority)

#### 📚 Enhanced Documentation

- **New Hooks Configuration Guide** (`docs/hooks.md`) - Set up notifications and automation
- **Marketplace Configuration** - Ready for Claude Code marketplace
- **Improved Installation Guide** - Better setup instructions
- **Enhanced Usage Guide** - More examples and workflows

---

### 🔧 Improvements

- Optimized `/summon-council` and `/summon-grumpy-reviewer` for better token efficiency
- Revised all agent definitions for clarity and consistency
- Enhanced senior council orchestration logic
- Added roadmap tracking for scoped and completed items
- Improved agent selection process with expanded specialist roles

---

### 📦 Installation

```bash
/install-github-plugin JackScammell/Parliament-Of-Chaos
```

To update from v1.0.0, simply re-run the installation command.

---

### 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Setup and troubleshooting
- **[Usage Guide](docs/usage.md)** - Commands and workflows  
- **[Hooks Configuration](docs/hooks.md)** - Notifications and automation
- **[CHANGELOG](CHANGELOG.md)** - Complete version history

---

### 🔗 Links

- **Repository**: https://github.com/JackScammell/Parliament-Of-Chaos
- **Issues**: https://github.com/JackScammell/Parliament-Of-Chaos/issues
- **Full Changelog**: https://github.com/JackScammell/Parliament-Of-Chaos/compare/V1.0.0...v1.1.0

---

### 🙏 Acknowledgments

Thank you to everyone who has used Parliament of Chaos and provided feedback. This release represents significant enhancements based on real-world usage and community input.

---

**Full Changelog**: See [CHANGELOG.md](CHANGELOG.md) for detailed changes.
