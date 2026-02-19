# Parliament of Chaos - Deliberation System

A high-performance multi-agent deliberation system with structured debate, parallel execution, and convergence detection.

## Features

### ✅ Implemented

- **Structured Output** - All agents output strict JSON matching predefined schemas (DebateStatement, Vote, RoundSummary)
- **Model Tiering** - Separate model tiers for chair/agent/summariser/validator roles
- **Parallel Execution** - All independent agent calls run concurrently using asyncio
- **Structured State Engine** - Debate state stored as structured data, not raw transcripts
- **Rolling Memory Compression** - Round summaries generated and raw transcripts discarded
- **Deliberation Modes** - Runtime-configurable modes (fast, adversarial, consensus, deep_deliberation)
- **Meta-Agent Observer** - Monitors convergence and novelty, recommends early termination
- **Validation Layer** - Enforces JSON structure with retry logic
- **Influence & Alignment Tracking** - Tracks agent alignments and influence scores
- **Performance Metrics** - Comprehensive tracking of tokens, latency, convergence, redundancy
- **Prompt Standardization** - All prompts follow ROLE/OBJECTIVE/CONSTRAINTS/OUTPUT FORMAT pattern
- **Voting Systems** - Support for majority, supermajority, quadratic, and influence-weighted voting

## Architecture

```
DebateController
├── AgentRuntime (parallel execution)
├── StateEngine (structured memory)
├── MetaObserver (convergence detection)
├── Validator (schema enforcement)
├── Summariser (memory compression)
└── MetricsCollector (performance tracking)
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
import asyncio
from src.deliberation import DebateController, DeliberationConfig

# Configure deliberation
config = DeliberationConfig(
    mode="consensus",
    max_rounds=5,
    max_tokens_per_agent=300,
    temperature=0.7,
    voting_system="majority"
)

# Initialize controller
controller = DebateController(config)

# Run deliberation
topic = "Should AI systems be required to explain their decisions?"
agents = ["agent1", "agent2", "agent3"]

results = await controller.run_deliberation(topic, agents)
```

### Deliberation Modes

- **fast** - Quick consensus-seeking with minimal rounds
- **adversarial** - Devil's advocate mode with maximum challenge
- **consensus** - Balanced approach seeking common ground
- **deep_deliberation** - Thorough exploration with extended rounds

### Voting Systems

- **majority** - Simple majority (>50%)
- **supermajority** - 2/3 threshold
- **quadratic** - Quadratic voting mechanism
- **influence_weighted** - Votes weighted by agent influence scores

## Schemas

### DebateStatement
```json
{
  "agent_id": "string",
  "position": "string",
  "argument": "string",
  "amendment": "string | null",
  "references": ["string"],
  "confidence": 0.0-1.0
}
```

### Vote
```json
{
  "agent_id": "string",
  "vote": "approve | reject | abstain",
  "reasoning": "string",
  "confidence": 0.0-1.0
}
```

### RoundSummary
```json
{
  "core_positions": ["string"],
  "major_conflicts": ["string"],
  "amendments": ["string"],
  "consensus_level": 0.0-1.0
}
```

## Performance Metrics

The system tracks:
- Total tokens used
- Tokens per round
- Average latency
- Rounds to convergence
- Position entropy
- Argument redundancy score

## Testing

```bash
python3 tests/test_schemas.py
```

## Integration Notes

### API Integration Required

The `ModelCaller` class provides the interface for calling LLM APIs. To integrate:

1. Implement `call_model()` and `call_model_async()` methods
2. Add your API client (Anthropic, OpenAI, etc.)
3. Configure authentication

Example stub:
```python
async def call_model_async(self, role: ModelRole, prompt: str, **kwargs) -> str:
    model_config = self.registry.get_model(role)
    # TODO: Add your API integration here
    # response = await client.messages.create(...)
    # return response.content
    raise NotImplementedError()
```

### Claude Code Plugin Integration

To integrate with the Parliament of Chaos Claude Code plugin:

1. Create a `deliberation-conductor` agent in `.claude/agents/`
2. Add a `/debate-topic` command in `.claude/commands/`
3. The agent orchestrates the deliberation system
4. Results are formatted as markdown reports

## Success Criteria

- ✅ No agent emits unstructured prose (all JSON)
- ✅ All independent calls are parallelized
- ⏳ Token usage reduced ≥40% (requires API integration to measure)
- ✅ Convergence measurable (MetaObserver implemented)
- ✅ Modes configurable without code rewrite
- ✅ Debate runtime stable under scale (async architecture)

## Future Enhancements

- Coalition formation mechanics
- Constitutional mutation system
- Enhanced quadratic voting implementation
- Real-time monitoring dashboard
- Multi-debate benchmarking suite

## License

MIT
