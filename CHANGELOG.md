# Changelog

All notable changes to Parliament of Chaos will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation review and updates
- CONTRIBUTING.md with comprehensive contribution guidelines
- CHANGELOG.md for tracking project changes
- API_REFERENCE.md for Python library usage
- DEVELOPMENT.md for development setup

### Fixed
- Corrected agent count in documentation (30 agents total)
- Corrected command count in documentation (16 commands total)
- Fixed duplicate "Discovery Commands" section in installation.md
- Updated dates from 2026 to 2025 in implementation documents
- Added missing deliberation-conductor agent to installation.md
- Added missing Analytics & Plugin Commands section

### Changed
- Improved documentation consistency across all files
- Enhanced README.md documentation table with better descriptions

## [1.0.0] - 2025-02-17

### Added
- **Core Parliament System**
  - 30 specialized agents (16 specialists, 9 grumpy reviewers, 3 planners, 2 orchestrators)
  - 16 slash commands for orchestration, review, planning, and analytics
  - Senior Council orchestration for multi-agent collaboration
  - Grumpy reviewer panel for critical code review

- **Specialist Agents**
  - system-architect: High-level design and architecture
  - backend-goblin: Backend performance and caching
  - security-knight: Security analysis and hardening
  - data-warlock: Database design and migrations
  - api-keeper: API design and versioning
  - test-prophet: Testing strategies and TDD
  - ui-ux-guru: UI/UX and accessibility
  - pipeline-engineer: CI/CD and deployment
  - doc-bard: Documentation and comments
  - package-wizard: Dependency management
  - resilience-tamer: Error handling and resilience
  - migration-monk: Schema migrations
  - dependency-detective: Vulnerability scanning
  - refactor-ranger: Code smell detection
  - config-curator: Configuration management
  - observability-oracle: Logging and monitoring

- **Grumpy Reviewers**
  - grumpy-code-reviewer: Overall code quality
  - grumpy-standards-enforcer: Coding standards
  - grumpy-architecture-skeptic: Architecture decisions
  - grumpy-maintainability-curmudgeon: Maintainability concerns
  - grumpy-security-nag: Security vulnerabilities
  - grumpy-performance-troll: Performance issues
  - grumpy-accessibility-auditor: WCAG compliance
  - grumpy-documentation-pedant: Documentation completeness
  - grumpy-testing-tyrant: Test coverage and quality

- **Planning Agents**
  - project-oracle: Interactive project planning
  - scope-weaver: Roadmap item scoping
  - task-executor: Task tracking and execution

- **Orchestrators**
  - senior-council: Multi-agent coordination
  - deliberation-conductor: Structured debate orchestration

- **Commands**
  - `/summon-council`: Full multi-agent orchestration
  - `/summon-grumpy-reviewer`: Quick code review
  - `/summon-specialist`: Invoke specific specialist
  - `/parliament-review`: Full 9-reviewer audit
  - `/debate-topic`: Structured multi-agent deliberation
  - `/list-agents`: Display all agents
  - `/list-commands`: Display all commands
  - `/explain-agent`: Detailed agent information
  - `/plan-project`: Interactive project planning
  - `/project-status`: Project progress dashboard
  - `/roadmap-add-item`: Add roadmap items
  - `/roadmap-item-scope`: Break down roadmap items
  - `/implement-task-list`: Execute tasks with oversight
  - `/debate-analytics`: Generate analytics dashboard
  - `/plugin-install`: Install community plugins
  - `/plugin-list`: List installed plugins

- **Deliberation System**
  - Structured multi-agent debate framework
  - Parallel execution with asyncio
  - Convergence detection and early termination
  - Multiple deliberation modes (fast, adversarial, consensus, deep)
  - Multiple voting systems (majority, supermajority, quadratic, influence-weighted)
  - Structured JSON output schemas
  - Rolling memory compression
  - Performance metrics tracking

- **Context Optimization** (70% Token Reduction)
  - Accurate token counting with tiktoken
  - Session token monitoring with automatic compression
  - Token budget enforcement per agent
  - Statement deduplication with Jaccard similarity
  - Dynamic context pruning for low-confidence statements
  - Bounded memory with O(1) growth
  - Multi-session support with vector memory
  - Semantic retrieval for relevant arguments

- **Safe Progress Assurance**
  - Pre-flight safety checks before implementation
  - Dependency graph construction and validation
  - Conflict detection for files, interfaces, schemas, events
  - Regression test mapping
  - Work completion records with contracts
  - Breaking change detection

- **Project Planning Workflow**
  - Interactive project scoping with Project Oracle
  - Phased roadmap generation
  - Task decomposition and specification
  - Progress tracking and status dashboard
  - Safe implementation with council oversight

- **Hooks System**
  - Configurable event hooks for notifications
  - Teams webhook integration example
  - Custom hook script support
  - Pre/post tool execution hooks

- **Documentation**
  - Comprehensive installation guide
  - Detailed usage guide with examples
  - Update guide with FAQ
  - Hooks configuration guide
  - Safe progress assurance documentation
  - Context optimization guide
  - Token reduction guide
  - Deliberation system documentation
  - Example project files

### Technical Details
- Python 3.8+ support
- Pydantic v2 for schema validation
- PyYAML for configuration
- tiktoken for accurate token counting
- asyncio for parallel execution
- Claude Code plugin architecture

## Project Status

### ✅ Implemented Features
- Core multi-agent system
- All 30 agents
- All 16 commands
- Deliberation system with convergence detection
- Context optimization (70% token reduction)
- Safe progress assurance
- Project planning workflow
- Hooks system
- Comprehensive documentation

### 🚧 Future Enhancements
- Enhanced plugin marketplace
- Coalition formation mechanics
- Constitutional mutation system
- Real-time monitoring dashboard
- Multi-debate benchmarking suite
- Advanced quadratic voting implementation
- Skill tree system for agents
- Cross-session learning and pattern recognition

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

[Unreleased]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/JackScammell/Parliament-Of-Chaos/releases/tag/v1.0.0
