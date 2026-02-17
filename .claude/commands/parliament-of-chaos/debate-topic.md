# Debate Topic

Run a structured multi-agent deliberation on a specified topic using the Parliament of Chaos deliberation system.

## Agent

**Delegated to: deliberation-conductor**

## Purpose

Conduct formal debate with:
- Parallel agent execution
- Structured JSON outputs
- Convergence detection
- Performance tracking
- Configurable modes and voting systems

## Usage

```
/debate-topic [topic] --mode [fast|adversarial|consensus|deep] --voting [majority|supermajority|quadratic|influence_weighted]
```

**Examples**:
```
/debate-topic Should we adopt microservices architecture?

/debate-topic API versioning strategy --mode adversarial --voting supermajority

/debate-topic Database sharding approach --mode deep --voting influence_weighted
```

## Options

- `--mode` (optional): Deliberation mode
  - `fast`: 3 rounds, quick consensus
  - `adversarial`: 5-7 rounds, maximum challenge
  - `consensus`: 5 rounds, balanced (default)
  - `deep`: 7-10 rounds, thorough exploration

- `--voting` (optional): Voting system
  - `majority`: >50% to pass (default)
  - `supermajority`: ≥66% to pass
  - `quadratic`: Quadratic voting
  - `influence_weighted`: Weighted by agent influence

## Process

1. **Identify Participants**
   - Select relevant Parliament agents for topic
   - Assign roles and alignments

2. **Structured Rounds**
   - Round 1: Opening positions (parallel)
   - Subsequent: Rebuttals based on summaries (parallel)
   - Meta-analysis after each round
   - Early termination if consensus reached

3. **Final Vote**
   - Chair synthesizes proposal
   - All agents vote (parallel)
   - Apply voting system rules

4. **Report**
   - Decision outcome
   - Round summaries
   - Performance metrics
   - Key insights

## Output

Structured markdown report with:
- All round positions
- Meta-analysis scores
- Voting results table
- Performance metrics (tokens, latency, convergence)
- Final recommendation

## Notes

- Uses deliberation system in `src/deliberation/`
- All agent outputs are validated JSON
- Tracks token usage and performance
- Applies rolling memory compression
- Detects and reports convergence

This command provides formal, measurable consensus-building for complex technical decisions.
