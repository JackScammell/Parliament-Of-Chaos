# Reference implementation — NOT part of the running plugin

> **⚠️ This directory does not execute.** Nothing in the Parliament of Chaos plugin
> imports, shells out to, or otherwise runs any code in here. The plugin's actual
> behaviour lives entirely in `agents/*.md`, `commands/*.md`, `settings.json`, and
> `src/hooks/*.sh`. Debates run as **LLM-orchestrated prose** (the
> `deliberation-conductor` agent), not as this Python engine.

## What this is

A Python reference implementation of the deliberation engine's concepts —
convergence detection, voting systems, context pruning, token budgeting, and so
on. It was written as a design study: `docs/ARCHITECTURE.md` describes the two
layers as "parallel expressions of the same ideas."

It is kept for reference because the data structures and algorithms document the
intended semantics of the deliberation system more precisely than prose can.

## Known limitations

- **It cannot run a deliberation.** The model-call layer
  (`deliberation/core/model_tier.py` — `ModelCaller.call_model` /
  `call_model_async`) is an unimplemented stub (`raise NotImplementedError`).
  Every agent invocation through `agents/agent_runtime.py` returns
  `success=False`.
- It is not packaged (no `pyproject.toml`) and is not on any import path the
  plugin uses.

## Running the tests

The unit tests exercise the implemented parts (schemas, context manager,
statement pruner, token counter) and all pass:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r reference/requirements.txt pytest
python -m pytest reference/tests/ -q   # from the repository root
```

Dependencies: see `requirements.txt` in this directory. `pytest` is needed to
run the tests. `sentence-transformers` is an **optional** extra used by
`deliberation/core/vector_memory.py`; without it, vector memory falls back to a
keyword-based implementation.

## If you want to make it real

Implement `ModelCaller.call_model[_async]` against the Claude API and the
communication layer in `deliberation/core/communication.py`, then give the
`/debate-*` commands an execution path that invokes it. Until that happens,
treat everything in this directory as documentation, not software.
