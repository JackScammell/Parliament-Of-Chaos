# Agent Teams Evaluation

**Issue**: #52
**Status**: Initial assessment — hands-on testing deferred
**Date**: 2026-02-27

## Overview

Agent Teams is an experimental Claude Code feature (v2.1.32+) that enables true concurrent multi-agent execution. This document evaluates its applicability to Parliament of Chaos.

## Current State

- **Feature flag**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- **Maturity**: Experimental — API may change between releases
- **Hook support**: `TeammateIdle` and `TaskCompleted` events are already wired into our `settings.json` and `notify_teams.sh`

## Alignment with Parliament of Chaos

### What Agent Teams could replace
| Current approach | Agent Teams equivalent |
|---|---|
| Sequential agent simulation in single context | True parallel agent execution |
| `senior-council` dispatching via `Task()` tools | Team coordinator spawning teammates |
| Grumpy reviewers running one-at-a-time | All 9 reviewers running concurrently |
| `deliberation-conductor` simulating rounds | Potential native round orchestration |

### What Agent Teams cannot replace
- **Python deliberation backend** (`src/deliberation/`): Convergence detection, quadratic voting, influence-weighted voting, rolling memory compression — these are custom logic that Agent Teams does not provide natively
- **Structured round-based flow**: Agent Teams provides concurrent execution but not the multi-round deliberation pattern with convergence checks between rounds
- **Analytics and metrics**: The debate analytics pipeline is custom functionality

## Preliminary Architecture Assessment

### Recommended approach: Hybrid
Agent Teams handles the **execution layer** (parallel spawning, result collection), while the Python backend continues to handle the **deliberation logic** (rounds, voting, convergence).

```
User → /summon-council → senior-council (Team Coordinator)
                              │
                              ├── Agent Teams: parallel specialist execution
                              │   (replaces sequential Task() dispatch)
                              │
                              ├── Agent Teams: parallel grumpy review
                              │   (replaces sequential reviewer dispatch)
                              │
                              └── Python backend: round management, voting, convergence
                                  (unchanged — complementary layer)
```

### Key benefit
The primary win is **latency reduction** for review cycles. Running 9 grumpy reviewers in parallel instead of sequentially could reduce review time by ~80%.

## Risks

| Risk | Severity | Notes |
|---|---|---|
| Experimental API instability | High | Must maintain current `Task()` approach as fallback |
| Token cost increase | Medium | Parallel agents each get their own context window |
| Custom agent compatibility | Unknown | Need to verify plugin agents work as teammates |
| Round coordination gap | Medium | Agent Teams lacks native round/convergence support |

## Next Steps

1. **Enable and test**: Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and run a simple council workflow
2. **Verify agent compatibility**: Confirm custom plugin agents can participate as team members
3. **Measure performance**: Compare token usage and latency vs current sequential approach
4. **Prototype hybrid**: Wire Agent Teams execution into `deliberation-conductor` with Python backend for rounds
5. **Decision gate**: Based on findings, either adopt hybrid approach or defer until Agent Teams stabilises

## Recommendation

**Defer adoption until Agent Teams exits experimental status.** The groundwork is already in place:
- `TeammateIdle` and `TaskCompleted` hooks are configured
- `background: true` on grumpy reviewers prepares for concurrent execution
- `isolation: worktree` on specialists prepares for parallel file access

When Agent Teams stabilises, migration should be straightforward given these Phase 3 foundations.
