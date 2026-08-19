# Parliament of Chaos - API Reference

> **⚠️ Reference-only code.** This documents the Python library under `reference/`, which is a
> **non-executing design study** — nothing in the running plugin invokes it, and its model-call
> layer is an unimplemented stub. See [`reference/README.md`](../reference/README.md) and
> [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) before relying on anything here.

This document provides detailed API reference for using Parliament of Chaos as a Python library.

## Table of Contents

- [Installation](#installation)
- [Core Modules](#core-modules)
- [Deliberation System](#deliberation-system)
- [Schemas](#schemas)
- [Context Management](#context-management)
- [Examples](#examples)

---

## Installation

### As a Python Package

```bash
# Clone the repository
git clone https://github.com/JackScammell/Parliament-Of-Chaos.git
cd Parliament-Of-Chaos

# Install dependencies
pip install -r reference/requirements.txt

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Requirements

```
pydantic>=2.0.0
pyyaml>=6.0.0
tiktoken>=0.5.0
```

---

## Core Modules

### Deliberation Controller

The main entry point for running multi-agent deliberations.

```python
from src.deliberation import DebateController, DeliberationConfig
```

#### `DebateController`

**Purpose**: Orchestrates multi-agent debates with structured output and convergence detection.

**Constructor**:
```python
DebateController(config: DeliberationConfig)
```

**Methods**:

##### `run_deliberation()`

Run a complete deliberation session.

```python
async def run_deliberation(
    self,
    topic: str,
    agents: List[str],
    constraints: Optional[Dict[str, Any]] = None
) -> DebateResults
```

**Parameters**:
- `topic` (str): The debate topic or question
- `agents` (List[str]): List of agent identifiers to participate
- `constraints` (Optional[Dict]): Optional constraints and rules

**Returns**: `DebateResults` object with conclusions, metrics, and history

**Example**:
```python
import asyncio
from src.deliberation import DebateController, DeliberationConfig

config = DeliberationConfig(
    mode="consensus",
    max_rounds=5,
    max_tokens_per_agent=300
)

controller = DebateController(config)

results = await controller.run_deliberation(
    topic="Should we use microservices or monolith?",
    agents=["system-architect", "backend-goblin", "security-knight"]
)

print(f"Consensus reached: {results.consensus_reached}")
print(f"Conclusion: {results.conclusion}")
```

---

### Configuration

#### `DeliberationConfig`

Configuration for deliberation behavior.

```python
from src.deliberation import DeliberationConfig

config = DeliberationConfig(
    mode="consensus",              # Deliberation mode
    max_rounds=5,                  # Maximum debate rounds
    max_tokens_per_agent=300,      # Token limit per agent per round
    temperature=0.7,               # LLM temperature
    voting_system="majority",      # Voting system to use
    enable_early_termination=True, # Allow early convergence
    convergence_threshold=0.85,    # Convergence detection threshold
    use_context_optimization=True  # Enable token optimization
)
```

**Modes**:
- `fast`: Quick consensus with minimal rounds
- `adversarial`: Devil's advocate with maximum challenge
- `consensus`: Balanced approach seeking agreement
- `deep_deliberation`: Thorough exploration with extended rounds

**Voting Systems**:
- `majority`: Simple majority (>50%)
- `supermajority`: 2/3 threshold
- `quadratic`: Quadratic voting mechanism
- `influence_weighted`: Votes weighted by agent influence

---

## Deliberation System

### State Engine

Manages debate state with structured memory.

```python
from src.deliberation.core.state_engine import StateEngine

engine = StateEngine(use_context_optimization=True)
```

#### Methods

##### `add_statement()`

Add an agent statement to the current round.

```python
def add_statement(self, statement: DebateStatement) -> None
```

##### `complete_round()`

Complete the current round and compress history.

```python
def complete_round(self) -> RoundSummary
```

##### `get_context()`

Get context for a specific agent.

```python
def get_context(
    self,
    agent_id: str,
    include_history: bool = True
) -> AgentContext
```

---

### Context Manager

Manages layered context with token optimization.

```python
from src.deliberation.core.context_manager import ContextManager

manager = ContextManager(
    max_historical_rounds=3,
    enable_deduplication=True,
    enable_pruning=True
)
```

#### Methods

##### `build_agent_context()`

Build optimized context for an agent.

```python
def build_agent_context(
    self,
    agent_id: str,
    current_statements: List[DebateStatement],
    historical_summaries: List[RoundSummary],
    rules: Optional[str] = None
) -> str
```

##### `compress_round()`

Compress a round's statements into a summary.

```python
def compress_round(
    self,
    statements: List[DebateStatement]
) -> RoundSummary
```

---

### Token Optimization

#### TokenCounter

Accurate token counting with tiktoken.

```python
from src.deliberation.core.token_counter import TokenCounter

counter = TokenCounter()
tokens = counter.count_tokens("Your text here")
```

#### SessionTokenMonitor

Monitor and manage token usage.

```python
from src.deliberation.core.token_counter import SessionTokenMonitor

monitor = SessionTokenMonitor(
    max_tokens=10000,
    compression_threshold=0.8
)

# Track usage
monitor.track_round(round_number=1, tokens=500)
monitor.track_agent(agent_id="architect", tokens=200)

# Check if compression needed
if monitor.should_compress():
    # Trigger compression
    pass

# Get statistics
stats = monitor.get_statistics()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Budget utilization: {stats['budget_utilization']:.1%}")
```

#### TokenBudgetEnforcer

Enforce per-agent token budgets.

```python
from src.deliberation.core.token_counter import TokenBudgetEnforcer

enforcer = TokenBudgetEnforcer(budget_per_agent=500)

# Check if agent is within budget
agent_context = "..."
if enforcer.check_budget("agent_id", agent_context):
    # Proceed with agent call
    pass
else:
    # Compress context
    compressed = enforcer.compress_to_budget("agent_id", agent_context)
```

---

## Schemas

### DebateStatement

Structured agent statement.

```python
from src.deliberation.schemas import DebateStatement

statement = DebateStatement(
    agent_id="system-architect",
    position="support",
    argument="Microservices provide better scalability and fault isolation.",
    amendment=None,
    references=["previous-statement-id"],
    confidence=0.8
)
```

**Fields**:
- `agent_id` (str): Agent identifier
- `position` (str): Position taken ("support", "oppose", "neutral")
- `argument` (str): Main argument text
- `amendment` (str | None): Proposed amendment to previous statement
- `references` (List[str]): References to previous statements
- `confidence` (float): Confidence score (0.0-1.0)

---

### Vote

Agent vote on a proposal.

```python
from src.deliberation.schemas import Vote

vote = Vote(
    agent_id="security-knight",
    vote="approve",
    reasoning="Security concerns are adequately addressed.",
    confidence=0.9
)
```

**Fields**:
- `agent_id` (str): Agent identifier
- `vote` (str): Vote choice ("approve", "reject", "abstain")
- `reasoning` (str): Explanation for the vote
- `confidence` (float): Confidence in the vote (0.0-1.0)

---

### RoundSummary

Compressed summary of a debate round.

```python
from src.deliberation.schemas import RoundSummary

summary = RoundSummary(
    core_positions=["Microservices improve scalability", "Monolith reduces complexity"],
    major_conflicts=["Debate between operational complexity vs deployment simplicity"],
    amendments=["Add API gateway for service coordination"],
    consensus_level=0.65
)
```

**Fields**:
- `core_positions` (List[str]): Key positions from the round
- `major_conflicts` (List[str]): Main points of disagreement
- `amendments` (List[str]): Proposed changes or additions
- `consensus_level` (float): Consensus score (0.0-1.0)

---

## Context Management

### Statement Deduplication

Remove duplicate or highly similar statements.

```python
from src.deliberation.core.statement_pruner import StatementDeduplicator

deduplicator = StatementDeduplicator(similarity_threshold=0.8)

# Check if statement is duplicate
is_duplicate = deduplicator.is_duplicate(
    agent_id="agent1",
    argument="This is my argument"
)

if not is_duplicate:
    # Add new statement
    deduplicator.add_statement("agent1", "This is my argument")
```

---

### Context Pruning

Remove low-quality statements to reduce token usage.

```python
from src.deliberation.core.statement_pruner import ContextPruner

pruner = ContextPruner(
    min_confidence=0.5,
    min_influence=0.7
)

# Prune statements
pruned_statements = pruner.prune(
    statements=all_statements,
    agent_influence_scores={"agent1": 0.8, "agent2": 0.6}
)

# Get pruning statistics
stats = pruner.get_statistics()
print(f"Removed: {stats['removed_count']} statements")
print(f"Kept: {stats['kept_count']} statements")
```

---

### Vector Memory

Store and retrieve statements semantically.

```python
from src.deliberation.core.vector_memory import VectorMemoryStore

# Initialize with optional embeddings
memory = VectorMemoryStore(use_embeddings=True)

# Store statements
for statement in statements:
    memory.add_statement(statement)

# Retrieve relevant statements
relevant = memory.retrieve_relevant(
    query="What was said about scalability?",
    top_k=5
)
```

---

## Examples

### Basic Deliberation

```python
import asyncio
from src.deliberation import DebateController, DeliberationConfig

async def run_basic_debate():
    config = DeliberationConfig(
        mode="consensus",
        max_rounds=3,
        max_tokens_per_agent=200
    )
    
    controller = DebateController(config)
    
    results = await controller.run_deliberation(
        topic="Should we migrate to TypeScript?",
        agents=["system-architect", "refactor-ranger", "test-prophet"]
    )
    
    print(f"Rounds completed: {results.rounds_completed}")
    print(f"Consensus: {results.conclusion}")
    print(f"Token usage: {results.metrics['total_tokens']}")

asyncio.run(run_basic_debate())
```

### Token-Optimized Deliberation

```python
import asyncio
from src.deliberation import DebateController, DeliberationConfig

async def run_optimized_debate():
    config = DeliberationConfig(
        mode="deep_deliberation",
        max_rounds=10,
        max_tokens_per_agent=300,
        use_context_optimization=True,
        convergence_threshold=0.9
    )
    
    controller = DebateController(config)
    
    results = await controller.run_deliberation(
        topic="Design a rate limiting system",
        agents=[
            "system-architect",
            "backend-goblin",
            "security-knight",
            "resilience-tamer"
        ]
    )
    
    print(f"Token savings: {results.metrics['token_reduction_percentage']:.1%}")
    print(f"Converged in {results.rounds_completed} rounds")

asyncio.run(run_optimized_debate())
```

### Custom Voting System

```python
import asyncio
from src.deliberation import DebateController, DeliberationConfig

async def run_weighted_voting_debate():
    config = DeliberationConfig(
        mode="adversarial",
        max_rounds=5,
        voting_system="influence_weighted",
        temperature=0.8
    )
    
    controller = DebateController(config)
    
    results = await controller.run_deliberation(
        topic="Security vs usability trade-offs in authentication",
        agents=[
            "security-knight",      # High influence on security
            "ui-ux-guru",          # High influence on usability  
            "backend-goblin"       # Medium influence overall
        ]
    )
    
    print(f"Final decision: {results.conclusion}")
    print(f"Vote breakdown: {results.vote_breakdown}")

asyncio.run(run_weighted_voting_debate())
```

---

## Integration with Claude Code Plugin

The Python library is designed to be used by the Claude Code plugin agents. Agent definitions in `.claude/agents/` can invoke the deliberation system:

```markdown
---
name: deliberation-conductor
description: Orchestrates structured multi-agent debates
---

# Deliberation Conductor

This agent uses the Parliament of Chaos deliberation system to run structured debates.

When invoked, it:
1. Configures the deliberation based on the topic
2. Selects appropriate agents to participate
3. Runs the debate using `DebateController`
4. Formats results as a markdown report
```

---

## Advanced Topics

### Custom Agent Implementation

To implement a custom agent:

1. Create an agent definition in `agents/`
2. Define the agent's expertise and role
3. Integrate with the deliberation system via `DebateController`

### Performance Tuning

Optimize deliberation performance:

- Adjust `max_tokens_per_agent` based on complexity
- Use `fast` mode for quick decisions
- Enable `use_context_optimization` for long debates
- Set appropriate `convergence_threshold` for early termination

### Error Handling

Handle common errors:

```python
from src.deliberation import DebateController, DeliberationConfig
from src.deliberation.exceptions import ConvergenceError, TokenLimitError

try:
    controller = DebateController(config)
    results = await controller.run_deliberation(topic, agents)
except ConvergenceError:
    # Failed to reach consensus
    print("Debate did not converge")
except TokenLimitError:
    # Exceeded token budget
    print("Token limit exceeded, enable optimization")
```

---

## API Stability

- **Stable**: Core schemas (DebateStatement, Vote, RoundSummary)
- **Stable**: DeliberationConfig interface
- **Stable**: DebateController.run_deliberation()
- **Beta**: Context optimization components
- **Experimental**: Vector memory integration

---

## Further Reading

- [Usage Guide](docs/usage.md) - Command usage examples
- [Deliberation System](docs/DELIBERATION_SYSTEM.md) - Architecture details
- [Context Optimization](docs/CONTEXT_OPTIMIZATION.md) - Token reduction system
- [Token Reduction Guide](docs/TOKEN_REDUCTION_GUIDE.md) - Optimization features

---

## Support

For questions or issues with the Python API:
- Check the [examples/](examples/) directory
- Review existing [GitHub Issues](https://github.com/JackScammell/Parliament-Of-Chaos/issues)
- Create a new issue with the `api` label
