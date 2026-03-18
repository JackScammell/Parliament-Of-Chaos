# GitHub Release Instructions for v1.1.0

This document provides step-by-step instructions for creating the GitHub release for Parliament of Chaos v1.1.0.

## Prerequisites

All preparation work has been completed:
- ✅ Version bumped to 1.1.0 in `.claude-plugin/marketplace.json`
- ✅ CHANGELOG.md created with comprehensive change documentation
- ✅ Release notes prepared in `RELEASE_NOTES_v1.1.0.md`
- ✅ Code review completed (no issues)
- ✅ Security checks passed (no vulnerabilities)
- ✅ All changes committed to the `copilot/create-release-for-new-version` branch

## Steps to Create the Release

### 1. Merge the PR

First, merge the pull request for `copilot/create-release-for-new-version` into the `main` branch:

1. Navigate to: https://github.com/JackScammell/Parliament-Of-Chaos/pulls
2. Open the PR for `copilot/create-release-for-new-version`
3. Review the changes one final time
4. Click "Merge pull request"
5. Confirm the merge

### 2. Create the GitHub Release

Once merged to main, create the release:

1. Go to: https://github.com/JackScammell/Parliament-Of-Chaos/releases/new

2. **Tag version**: Enter `v1.1.0`
   - Make sure to use lowercase 'v' (unlike V1.0.0) for consistency with semver conventions

3. **Target**: Select `main` branch (or the latest commit SHA after merge)

4. **Release title**: Enter `v1.1.0 - Enhanced agent council with new specialists and commands`

5. **Description**: Copy the content from `RELEASE_NOTES_v1.1.0.md`
   - You can view the file here: `/home/runner/work/Parliament-Of-Chaos/Parliament-Of-Chaos/RELEASE_NOTES_v1.1.0.md`
   - Or use the formatted version below

6. **Options**:
   - ☑️ Set as the latest release (checked)
   - ☐ Set as a pre-release (unchecked)

7. Click "Publish release"

### 3. Verify the Release

After publishing:

1. Check that the release appears at: https://github.com/JackScammell/Parliament-Of-Chaos/releases
2. Verify the tag was created: https://github.com/JackScammell/Parliament-Of-Chaos/tags
3. Test installation with: `claude plugin install parliament-of-chaos@parliament-of-chaos`

### 4. Announce (Optional)

Consider announcing the release:
- Update any relevant documentation or wikis
- Share on social media or relevant communities
- Update the Claude Code marketplace listing if applicable

---

## Release Description (Copy-Paste Ready)

```markdown
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
claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
claude plugin install parliament-of-chaos@parliament-of-chaos
```

To update from a previous version, run `claude plugin update parliament-of-chaos@parliament-of-chaos`.

---

### 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Setup and troubleshooting
- **[Usage Guide](docs/usage.md)** - Commands and workflows  
- **[Hooks Configuration](docs/hooks.md)** - Notifications and automation
- **[CHANGELOG](CHANGELOG.md)** - Complete version history

---

### 🙏 Acknowledgments

Thank you to everyone who has used Parliament of Chaos and provided feedback. This release represents significant enhancements based on real-world usage and community input.

---

**Full Changelog**: https://github.com/JackScammell/Parliament-Of-Chaos/compare/V1.0.0...v1.1.0
```

---

## Notes

- The tag format is `v1.1.0` (lowercase 'v') for better semver consistency, even though v1.0.0 used uppercase
- All documentation in the repository already reflects the v1.1.0 changes
- The CHANGELOG.md file follows Keep a Changelog format for future maintainability
- No code changes were made, only version bumps and documentation, so no testing is required beyond installation verification
