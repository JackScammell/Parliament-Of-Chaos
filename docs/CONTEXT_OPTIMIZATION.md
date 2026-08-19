# Context Optimization and Management System

**Version:** 1.0  
**Status:** Implemented  
**Last Updated:** 2025-02-17

---

## Overview

The Context Optimization and Management System is a comprehensive token-efficient context handling solution for Parliament of Chaos. It reduces token usage by 60-70% while preserving reasoning quality, scaling multi-agent debates, and supporting multi-session workflows.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│            Parliament of Chaos                       │
│                                                      │
│  ┌──────────────────┐                               │
│  │ DebateController │                               │
│  └────────┬─────────┘                               │
│           │                                          │
│  ┌────────▼─────────┐       ┌──────────────┐       │
│  │   StateEngine    │◄──────┤ ContextManager│       │
│  └────────┬─────────┘       └──────┬───────┘       │
│           │                        │                │
│  ┌────────▼─────────┐             │                │
│  │  AgentRuntime    │◄────────────┘                │
│  └──────────────────┘                               │
│                                                      │
└──────────────────────────────────────────────────────┘

ContextManager Layers:
┌─────────────────────────────┐
│    ContextManager           │
│  ┌──────────────────────┐  │
│  │  ImmediateContext    │  │ ← Current round only
│  └──────────────────────┘  │
│  ┌──────────────────────┐  │
│  │  HistoricalContext   │  │ ← Compressed summaries
│  └──────────────────────┘  │
│  ┌──────────────────────┐  │
│  │  ReferenceContext    │  │ ← Rules & retrieval
│  └──────────────────────┘  │
└─────────────────────────────┘
```

## Core Components

### 1. ContextManager

**Location:** `reference/deliberation/core/context_manager.py`

The main orchestrator for token-efficient context handling.

**Key Features:**
- Structured JSON-based context representation
- Rolling memory compression
- Bounded token usage (independent of debate length)
- Token usage tracking and metrics

**Usage:**
```python
from src.deliberation.core.context_manager import ContextManager

# Create context manager
manager = ContextManager(max_historical_rounds=3)

# Start a new round
manager.start_new_round(round_number=0)

# Add statements to current round
manager.add_statement(debate_statement)

# Compress round after completion
manager.compress_round(round_summary)

# Build optimized context for an agent
context = manager.build_agent_context(
    agent_id="agent-1",
    agent_position=position,
    topic="Should we implement feature X?"
)

# Get token statistics
stats = manager.get_token_statistics()
```

### 2. ImmediateContext

**Purpose:** Stores current round data with maximum detail.

**Data Structure:**
```json
{
  "round_number": 5,
  "agent_statements": [
    {
      "agent_id": "agent_1",
      "position": "Pro-X",
      "argument": "Main points...",
      "amendment": null,
      "confidence": 0.85
    }
  ],
  "votes": [],
  "amendments": []
}
```

**Token Optimization:**
- Arguments summarized to ~50 words max
- Only essential fields included
- Structured JSON format (not prose)

### 3. HistoricalContext

**Purpose:** Compressed summaries of previous rounds.

**Data Structure:**
```json
{
  "recent_summaries": [
    {
      "round": "3",
      "core_positions": ["Pro-X", "Contra-X"],
      "major_conflicts": ["Budget allocation"],
      "consensus_level": 0.65
    }
  ],
  "aggregated": {
    "all_positions": ["Pro-X", "Contra-X"],
    "unresolved_conflicts": ["Budget allocation", "Timeline"],
    "pending_amendments": ["Amendment-A"],
    "consensus_trend": [0.5, 0.6, 0.65]
  }
}
```

**Token Optimization:**
- Only last N rounds kept (default: 3)
- Aggregated view of all historical data
- No raw transcripts stored

### 4. ReferenceContext

**Purpose:** Optional rules, constraints, and semantic retrieval results.

**Data Structure:**
```json
{
  "rules": ["Rule 1", "Rule 2"],
  "constraints": ["Constraint 1"],
  "relevant_arguments": [
    {"text": "Similar argument", "score": 0.9}
  ]
}
```

**Token Optimization:**
- Limited to top 3 items per category
- Optional (only included when needed)

## Token Reduction Strategies

### 1. Structured JSON Over Free Text

**Before:**
```
The agents discussed various positions including support for feature X 
with the following reasoning: it would improve performance. Agent-2 
disagreed, stating that...
```

**After (JSON):**
```json
{
  "statements": [
    {"agent": "agent-1", "position": "Pro-X", "confidence": 0.8},
    {"agent": "agent-2", "position": "Contra-X", "confidence": 0.7}
  ]
}
```

**Token Savings:** ~60%

### 2. Rolling Summaries

Instead of keeping full transcripts:
- Compress each round into a structured summary
- Discard detailed statements after summarization
- Keep only last N round summaries

**Token Savings:** ~70% after 5+ rounds

### 3. Argument Summarization

Long arguments automatically summarized:
```python
# Original: 200 words
"This is a very long argument with many detailed points about..."

# Summarized: ~50 words
"This is a very long argument with many detailed points..."
```

**Token Savings:** ~40-60% per statement

### 4. Selective Pruning

Low-impact or low-confidence statements can be pruned:
- Confidence < 0.3: Consider for pruning
- Redundant arguments: Deduplicated

### 5. Dynamic Context Building

Agents receive only what they need:
- Their own position
- Immediate context (current round)
- Historical summary (compressed)
- Reference context (optional)

**Token Budget Allocation (for 500 token target):**
- Role/Objective/Topic: ~50 tokens
- Immediate Context: ~200 tokens
- Historical Summary: ~150 tokens
- Agent Position: ~50 tokens
- Reference Context: ~50 tokens (optional)

## Integration Guide

### Enabling Context Optimization

#### In StateEngine:
```python
from src.deliberation.core.state_engine import StateEngine

# Enable context optimization
state_engine = StateEngine(use_context_optimization=True)

# Disable (default for backward compatibility)
state_engine = StateEngine(use_context_optimization=False)
```

#### In DebateController:
```python
from src.deliberation.core.debate_controller import DebateController
from src.deliberation.models.schemas import DeliberationConfig

config = DeliberationConfig(max_rounds=5)
controller = DebateController(config)

# Context optimization is automatically enabled
# via StateEngine(use_context_optimization=True)
```

### Accessing Context Statistics

```python
# From StateEngine
stats = state_engine.get_context_statistics()

# From DebateController results
result = await controller.run_deliberation(topic, agents)
context_stats = result.get("context_optimization")
```

## Multi-Session Support

### SessionManager Integration

**Location:** `reference/deliberation/core/session_manager.py`

The SessionManager now integrates with ContextManager for cross-session persistence.

**Usage:**
```python
from src.deliberation.core.session_manager import SessionManager

# Create session manager with context optimization
manager = SessionManager(use_context_optimization=True)

# Create a new session linked to previous ones
session = manager.create_session(
    session_id="session-2",
    previous_sessions=["session-1"],
    context_manager=context_manager
)

# Context manager state is automatically persisted
manager.update_session(context={}, conflicts=[], summary="...")

# Load previous session context
manager._load_context_manager_state("session-1")
```

### Cross-Session Context

```python
# Get aggregated context from all sessions in chain
cross_session = manager.get_cross_session_context()

# Returns:
{
    "session_count": 3,
    "all_conflicts": ["Conflict-1", "Conflict-2"],
    "all_summaries": {...},
    "context_keys": ["key1", "key2"]
}
```

## Optional: Vector Memory Support

The system includes interfaces for vector memory integration (optional).

### VectorMemoryEntry Schema

```python
from src.deliberation.models.schemas import VectorMemoryEntry

entry = VectorMemoryEntry(
    entry_id="entry-1",
    content="Important argument text",
    metadata={"round": 5, "agent": "agent-1"},
    embedding=[0.1, 0.2, ...],  # Optional
    timestamp="2026-02-17T15:00:00Z"
)
```

### Semantic Retrieval

```python
# Add semantic retrieval results to reference context
results = [
    {"text": "Similar argument", "score": 0.9},
    {"text": "Related point", "score": 0.8}
]

manager.add_semantic_retrieval_result(
    query="budget allocation",
    results=results,
    top_k=3
)
```

## Performance Metrics

### Context Optimization Metrics

The system tracks detailed metrics:

```python
{
    "average_tokens_per_agent": 450,
    "token_reduction_percentage": 65.0,
    "immediate_context_tokens": 200,
    "historical_context_tokens": 150,
    "reference_context_tokens": 50,
    "compression_ratio": 0.35,
    "rounds_tracked": 5
}
```

### Token Statistics

```python
stats = manager.get_token_statistics()

{
    "average_total": 425,
    "max_total": 480,
    "min_total": 380,
    "average_immediate": 200,
    "average_historical": 150,
    "calls_tracked": 15
}
```

## Testing

### Running Tests

```bash
# Run context manager tests
python -m unittest tests.test_context_manager -v

# Run all tests including integration
python -m unittest tests.test_schemas -v
```

### Test Coverage

- ✅ 26 unit tests for ContextManager
- ✅ Integration tests with StateEngine
- ✅ Backward compatibility tests
- ✅ Token reduction validation
- ✅ Multi-round compression tests

## Best Practices

### 1. Always Use Context Optimization for New Debates

```python
# Good
state_engine = StateEngine(use_context_optimization=True)

# Less optimal (legacy compatibility)
state_engine = StateEngine(use_context_optimization=False)
```

### 2. Set Appropriate Historical Window

```python
# For short debates (3-5 rounds)
manager = ContextManager(max_historical_rounds=3)

# For longer debates (10+ rounds)
manager = ContextManager(max_historical_rounds=5)
```

### 3. Track Token Usage

```python
# Track after each agent call
manager.track_token_usage(agent_id)

# Review statistics periodically
stats = manager.get_token_statistics()
if stats["average_total"] > 500:
    print("Warning: Token usage exceeding target")
```

### 4. Use Semantic Retrieval Sparingly

```python
# Only add when truly relevant
if topic_requires_historical_context:
    manager.add_semantic_retrieval_result(query, results, top_k=3)
```

### 5. Persist Context for Multi-Session Debates

```python
# Always link sessions
session = session_manager.create_session(
    session_id="session-2",
    previous_sessions=["session-1"],
    context_manager=context_manager
)
```

## Migration from Legacy System

### Gradual Migration

The system maintains full backward compatibility:

1. **Phase 1:** Keep existing code working (default `use_context_optimization=False`)
2. **Phase 2:** Enable optimization for new debates
3. **Phase 3:** Migrate existing debates as needed

### Example Migration

```python
# Legacy code (still works)
state_engine = StateEngine()
context = state_engine.get_agent_context("agent-1")

# Migrated code (optimized)
state_engine = StateEngine(use_context_optimization=True)
context = state_engine.get_agent_context("agent-1")
```

Both return compatible context structures.

## Troubleshooting

### Issue: Context optimization not working

**Solution:** Ensure `use_context_optimization=True` in StateEngine:
```python
state_engine = StateEngine(use_context_optimization=True)
```

### Issue: Token usage still high

**Solutions:**
1. Reduce `max_historical_rounds` (default: 3)
2. Check if reference context is being overused
3. Verify argument summarization is working

### Issue: Context manager state not persisting

**Solution:** Ensure SessionManager has access to ContextManager:
```python
session_manager.create_session(
    session_id="...",
    context_manager=context_manager
)
```

## Future Enhancements

- [ ] Automatic topic-based vector retrieval
- [ ] Machine learning-based argument compression
- [ ] Adaptive token budgeting based on debate complexity
- [ ] Real-time token usage visualization
- [ ] Integration with external vector databases (Pinecone, Weaviate)

## References

- **Primary Implementation:** `reference/deliberation/core/context_manager.py`
- **Integration Layer:** `reference/deliberation/core/state_engine.py`
- **Session Persistence:** `reference/deliberation/core/session_manager.py`
- **Schema Definitions:** `reference/deliberation/models/schemas.py`
- **Tests:** `reference/tests/test_context_manager.py`

---

**For questions or issues, please refer to the Parliament of Chaos documentation or open an issue on GitHub.**
