# Enhanced Features Guide

This guide covers the new advanced features added to Parliament of Chaos.

## Table of Contents

1. [Native Agent Teams Integration](#native-agent-teams-integration)
2. [Persistent Memory System](#persistent-memory-system)
3. [Plugin Marketplace](#plugin-marketplace)
4. [Agent Skill Trees](#agent-skill-trees)
5. [Debate Analytics Dashboard](#debate-analytics-dashboard)
6. [Advanced Governance Models](#advanced-governance-models)
7. [User-Driven Constraints](#user-driven-constraints)
8. [Multi-Session Debate Chaining](#multi-session-debate-chaining)
9. [Self-Improving Agents](#self-improving-agents)

---

## Native Agent Teams Integration

Organize agents into structured debate teams with specific roles.

### Team Roles

- **Advocate**: Present pro arguments and supporting evidence
- **Opponent**: Present counterarguments and challenges
- **Moderator**: Enforce rules and maintain debate structure
- **Synthesis**: Find common ground and synthesize positions

### Usage

```python
from src.deliberation import (
    DebateController, 
    DeliberationConfig,
    create_default_debate_teams
)

# Create team configuration
agents = ["agent1", "agent2", "agent3", "agent4"]
team_config = create_default_debate_teams(agents)

# Configure debate with teams
config = DeliberationConfig(
    mode="team_debate",
    use_persistent_memory=False
)

controller = DebateController(config)
```

### Coordination Modes

- **Sequential**: Teams speak in priority order
- **Parallel**: All teams execute simultaneously
- **Hybrid**: Mix of sequential and parallel

---

## Persistent Memory System

Store and recall debate history across sessions.

### Storage

Debates are automatically stored in `.parliament-memory/` directory with:
- Topic and timestamp
- Outcome and votes
- Key learnings
- Identified patterns

### Usage

```python
from src.deliberation import MemoryManager

memory = MemoryManager()

# Save a debate
memory.save_debate(
    session_id="session-123",
    topic="API Design Standards",
    outcome={"approved": True, "votes": {...}},
    key_learnings=["REST over GraphQL", "Versioning strategy"]
)

# Recall similar debates
similar = memory.recall_similar_debates("API Design", limit=3)

# Get context for new debate
context = memory.get_memory_context("Should we use microservices?")
```

### Benefits

- Avoid repeated debate mistakes
- Learn from past decisions
- Track conceptual evolution
- Build institutional knowledge

---

## Plugin Marketplace

Extend Parliament with community-contributed agents.

### Commands

```bash
# Install a plugin
/plugin-install blockchain-sage

# List installed plugins
/plugin-list

# Use a plugin
/summon-specialist blockchain-sage
```

### Creating Plugins

```python
from src.deliberation import PluginManager

manager = PluginManager()

manager.install_plugin(
    name="ml-optimizer",
    version="1.0.0",
    author="Community",
    description="Machine learning model optimization expert",
    agent_type="specialist",
    skills=["Neural Networks", "Hyperparameter Tuning", "Model Compression"]
)
```

### Plugin Storage

Plugins are stored in `.parliament-plugins/` with a registry index.

---

## Agent Skill Trees

Hierarchical expertise trees for token-efficient specialization.

### Structure

```yaml
ui-ux-guru:
  primary_domain: "UI/UX Design"
  skills:
    Accessibility:
      - "WCAG Compliance"
      - "Screen Reader Support"
      - "Keyboard Navigation"
    Color Psychology:
      - "Color Theory"
      - "Contrast Ratios"
    Usability Testing:
      - "A/B Testing"
      - "User Feedback"
  skill_levels:
    Accessibility: 5
    Color Psychology: 4
    Usability Testing: 5
```

### Usage

```python
from src.deliberation.agents.skill_trees import SkillTreeManager

skill_mgr = SkillTreeManager()

# Get agent's skills
tree = skill_mgr.get_skill_tree("ui-ux-guru")
accessibility_skills = skill_mgr.get_skills_for_domain("ui-ux-guru", "Accessibility")

# Match agents to tasks
matching_agents = skill_mgr.match_agent_to_task(["accessibility", "wcag"])
```

### Benefits

- Load skills on demand
- Reduce token overhead
- Clear expertise hierarchy
- Better agent selection

---

## Debate Analytics Dashboard

Comprehensive metrics and insights on debate performance.

### Command Usage

```bash
# Analyze a specific topic
/debate-analytics API Design Standards

# View recent debates
/debate-analytics
```

### Metrics Tracked

- **Consensus Score**: Overall agreement level (0-1)
- **Agent Influence**: Impact of each agent on outcome
- **Argument Novelty**: New ideas introduced per round
- **Time to Convergence**: Speed of reaching agreement
- **Token Usage**: Resource consumption
- **Voting Patterns**: Breakdown by voting system

### Example Output

```markdown
# Debate Analytics Dashboard

**Topic:** API Design Standards
**Consensus Score:** 87%

## Performance Metrics
| Metric | Value |
|--------|-------|
| Total Tokens | 8,432 |
| Rounds to Convergence | 3 |
| Average Latency | 2.34s |

## Agent Influence Scores
| Agent | Influence |
|-------|-----------|
| api-keeper | 0.892 |
| system-architect | 0.845 |
```

### Programmatic Usage

```python
from src.deliberation import DebateDashboard, AnalyticsEngine

dashboard = DebateDashboard()
analytics = AnalyticsEngine()

# Calculate metrics
consensus = analytics.calculate_consensus_score(votes)
influence = analytics.calculate_agent_influence(positions, votes)
novelty = analytics.calculate_novelty_scores(rounds_data)

# Generate dashboard
markdown = dashboard.generate_dashboard(debate_results, analytics_data)
```

---

## Advanced Governance Models

Multiple voting systems with confidence weighting and coalition formation.

### Voting Systems

#### 1. Majority Vote
Simple majority wins (>50%)

#### 2. Supermajority
Requires 66.7% approval

#### 3. Influence-Weighted
Votes weighted by agent influence scores

#### 4. Quadratic Voting
Square root of confidence to prevent vote concentration

#### 5. Delegated Voting
High-confidence agents (≥0.8) receive 2x weight

#### 6. Coalition Voting
Aligned agents amplify each other

### Usage

```python
from src.deliberation import VotingSystemManager, CoalitionBuilder

voting = VotingSystemManager()
coalition = CoalitionBuilder()

# Calculate outcome with different systems
approved, details = voting.calculate_outcome(
    votes, 
    positions,
    system="influence_weighted"
)

# Form coalitions
coalitions = coalition.form_coalitions(positions)
analysis = coalition.analyze_coalition_strength(coalition_members, positions)
```

### Configuration

```python
config = DeliberationConfig(
    voting_system="coalition",  # or "supermajority", "delegated", etc.
    convergence_threshold=0.85
)
```

---

## User-Driven Constraints

Define debate rules and patterns to avoid.

### Constraint File Format

Create `constraints.yaml`:

```yaml
constraints:
  max_rounds: 5
  disallowed_patterns:
    - "nested callbacks"
    - "global state"
    - "eval\\("
  required_validators:
    - "security_check"
    - "style_compliance"
  custom_rules:
    no_profanity: "!profane_word"
    require_evidence: "evidence|source|citation"
```

### Usage

```python
from src.deliberation import ConstraintLoader, ConstraintValidator

# Load constraints
loader = ConstraintLoader()
constraints = loader.load_from_file("constraints.yaml")

# Validate content
validator = ConstraintValidator(constraints)
is_valid, violations = validator.validate_statement(content)

if not is_valid:
    print("Violations:", violations)
```

### Validation

Agents automatically validate statements against constraints:
- Pattern matching (regex or literal)
- Custom rule evaluation
- Required validator checks
- Round limit enforcement

---

## Multi-Session Debate Chaining

Carry debates across multiple sessions with state persistence.

### Creating Sessions

```python
from src.deliberation.core.session_manager import SessionManager

session_mgr = SessionManager()

# Create new session
session = session_mgr.create_session(
    session_id="session-2",
    previous_sessions=["session-1"]
)

# Update session
session_mgr.update_session(
    context={"key": "value"},
    conflicts=["unresolved issue"],
    summary="Session 2 summary"
)
```

### Session Features

- **Carried Context**: Important context flows between sessions
- **Conflict Tracking**: Unresolved issues persist
- **Session Summaries**: Compressed history of each session
- **Session Chains**: Link related debates

### Use Cases

- Long-running design decisions
- Iterative feature development
- Cross-project consistency
- Policy evolution tracking

---

## Self-Improving Agents

Meta-learning framework for adaptive agent behavior.

### How It Works

1. **Track Performance**: Record debate outcomes and patterns
2. **Identify Patterns**: Distinguish successful vs failed approaches
3. **Suggest Adaptations**: Recommend strategy changes
4. **Apply Learning**: Agents adapt based on history

### Usage

```python
from src.deliberation.core.self_improvement import SelfImprovementEngine

learning = SelfImprovementEngine()

# Record strategy performance
learning.record_strategy_performance(
    strategy_id="consensus-building",
    performance_score=0.85,
    patterns=["early_compromise", "evidence_based"],
    success=True
)

# Get adaptation suggestions
suggestion = learning.suggest_adaptation("consensus-building")
print(suggestion["recommendation"])

# Apply adaptation
learning.adapt_strategy("consensus-building")
```

### Learning Data

Stored in `.parliament-learning/`:
- Strategy performance history
- Successful patterns
- Failed patterns to avoid
- Adaptation count

### Benefits

- Continuously improving debates
- Reduced repeated mistakes
- Better strategy selection
- Evidence-based adaptations

---

## Configuration

Enable features in `DeliberationConfig`:

```python
config = DeliberationConfig(
    mode="consensus",
    max_rounds=5,
    voting_system="influence_weighted",
    use_persistent_memory=True,     # Enable memory
    enable_constraints=True,         # Enable constraint validation
    enable_self_improvement=True     # Enable meta-learning
)
```

## Storage Directories

All feature data is stored locally:

```
.parliament-memory/      # Debate history
.parliament-plugins/     # Community agents
.parliament-sessions/    # Multi-session state
.parliament-learning/    # Meta-learning data
.parliament-skills/      # Agent skill trees
```

Add these to `.gitignore` to keep them local.

---

## Examples

See `examples/` directory for:
- `constraints.yaml`: Constraint configuration example
- `skill-trees.yaml`: Agent skill tree definitions
- `example_usage.py`: Programmatic usage examples

---

## Next Steps

1. Explore the commands: `/debate-analytics`, `/plugin-install`, `/plugin-list`
2. Create your own constraint files
3. Define custom agent skill trees
4. Experiment with different voting systems
5. Track debate evolution with persistent memory

For questions and support, see the main [README.md](../README.md).
