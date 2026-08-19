# Parliament of Chaos — Architecture Overview

New to the repository? This page is the map. Parliament of Chaos is **two loosely-coupled
layers** living in one repository, and understanding that split resolves most of the
"wait, how does this fit together?" questions.

| | **A. The Claude Code plugin (runtime)** | **B. The Python deliberation library** |
|---|---|---|
| **What it is** | The thing that actually runs when you type `/chaos:…` in Claude Code | A standalone, importable Python implementation of the same deliberation concepts |
| **Lives in** | `agents/`, `commands/`, `src/hooks/`, `.claude/rules/`, `.claude-plugin/` | `reference/deliberation/`, with `reference/tests/` and `reference/examples/` |
| **Language** | Markdown (agents + commands) + Bash (hooks) | Python 3.8+ (`pydantic`, `pyyaml`, `tiktoken`) |
| **Executed by** | Claude Code, as LLM-native prompts and Task fan-out | A Python interpreter, via `import` — see [`API_REFERENCE.md`](API_REFERENCE.md) |
| **Docs** | [`usage.md`](usage.md), [`installation.md`](installation.md), [`hooks.md`](hooks.md) | [`API_REFERENCE.md`](API_REFERENCE.md), [`DELIBERATION_SYSTEM.md`](DELIBERATION_SYSTEM.md), [`ENHANCED_FEATURES.md`](ENHANCED_FEATURES.md) |

> **The single most important fact:** the slash commands and agents do **not** call the Python
> code, and the Python code does not drive the plugin. They are **parallel expressions of the
> same ideas** — one as LLM-native orchestration, one as a conventional Python library — that
> share a design vocabulary (deliberation rounds, voting systems, convergence, token reduction)
> but not a runtime call path. Keep this in mind when reading the docs: a page under "Layer B"
> describes real, tested Python that an LLM turn never executes.

---

## Layer A — The Claude Code plugin (what runs in-session)

This is the live product. When you invoke a Parliament command, an LLM — not a Python process —
does the work.

```
.claude-plugin/
  plugin.json          # Plugin manifest — version source of truth (must match marketplace.json + CHANGELOG)
  marketplace.json     # Marketplace metadata
agents/                # 33 agent definitions (Markdown + YAML frontmatter)
  senior-council.md            # Orchestrator — coordinates specialists + reviewers
  deliberation-conductor.md    # Orchestrator — runs structured debates via Task() fan-out
  <16 specialists>             # Domain experts (backend-goblin, data-warlock, …) — implement
  <12 grumpy reviewers>        # Read-only quality gates (grumpy-security-nag, …) — critique only
  <3 planning agents>          # project-oracle, scope-weaver, task-executor
commands/              # 66 slash-command definitions + manifest.yaml (the registry)
  manifest.yaml        # Source-of-truth registry; reconciled by /parliament-doctor
src/hooks/             # Bash hook scripts (log_event.sh, notify_teams.sh, _common.sh, …)
.claude/rules/         # Governance loaded via the InstructionsLoaded hook
  governance.md, agent-standards.md, output-standards.md, fan-out-policy.md
```

**How a command executes.** A command (e.g. `/debate-topic`) names an owner agent in its
frontmatter (`deliberation-conductor`). That agent is an LLM persona whose tools are
`Task(<other-agent>)` calls plus Read/Write/Edit. Orchestrators fan out to specialists and
reviewers as sub-agents; hooks fire on lifecycle events (`SubagentStart`, `TaskCompleted`, …)
and append telemetry to `activity.jsonl`. No step shells out to `reference/deliberation/`.

**Governance is enforced in prose, not code.** The rules in `.claude/rules/` — the conflict-
resolution priority, the read-only reviewer constraint, the council fan-out/liveness floor —
are instructions the orchestrating LLM follows, wired in through the `InstructionsLoaded` hook.
See [`governance.md`](../.claude/rules/governance.md) and
[`fan-out-policy.md`](../.claude/rules/fan-out-policy.md).

## Layer B — The Python deliberation library (`reference/deliberation/`)

A conventional, importable Python package implementing the deliberation engine as code. It has
its own tests and runnable examples and is documented as a library API — it is **not** invoked
by Layer A.

```
reference/deliberation/
  core/          # debate_controller, state_engine, token_counter, statement_pruner,
                 # context_manager, vector_memory, session_manager, metrics, model_tier, …
  memory/        # memory_manager, memory_store — persistent cross-session memory
  plugins/       # plugin_manager, plugin_registry — extension marketplace
  constraints/   # constraint_validator, constraint_loader
  governance/    # voting_systems (majority/supermajority/quadratic/influence), coalition_builder
  analytics/     # analytics_engine, dashboard
  agents/        # agent_runtime, team_coordinator, skill_trees
  models/        # schemas.py — Pydantic models (DebateStatement, Vote, RoundSummary, …)
  utils/         # validation
tests/           # pytest suite (test_token_counter, test_statement_pruner, test_schemas, …)
examples/        # standalone runnable demos (add repo root to sys.path; no CLI entrypoint)
```

**Entry point.** There is no CLI or `setup.py`/`pyproject.toml`; you use it as a library —
`sys.path`-insert the repo root and `import` from `deliberation`, exactly as the files under
`reference/examples/` do. Concepts, schemas, and module APIs are documented in
[`API_REFERENCE.md`](API_REFERENCE.md), [`DELIBERATION_SYSTEM.md`](DELIBERATION_SYSTEM.md),
[`CONTEXT_OPTIMIZATION.md`](CONTEXT_OPTIMIZATION.md), and
[`TOKEN_REDUCTION_GUIDE.md`](TOKEN_REDUCTION_GUIDE.md).

---

## Where things are stored at runtime

| Location | Contents | Owner / lifecycle |
|---|---|---|
| `${CLAUDE_PLUGIN_DATA}/` | Telemetry, `activity.jsonl`, review state | Plugin-owned; survives updates; disposable |
| `.project-files/` | User-facing planning artifacts (outlines, roadmaps, specs, plans) | User-owned; lives with the project |
| `.project-files/.telemetry/` | Hook-data fallback when `CLAUDE_PLUGIN_DATA` is unset | Plugin-owned fallback |

See [`agent-standards.md`](../.claude/rules/agent-standards.md) for the full plugin-state and
frontmatter conventions.

## Historical documents

Point-in-time completion memos and old release notes are kept under
[`docs/archived/`](archived/) with a banner on each. They describe real past work but are **not**
maintained as current documentation — always prefer [`CHANGELOG.md`](../CHANGELOG.md) and the
live pages above.
