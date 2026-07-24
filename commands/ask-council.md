---
description: Ask the council a question and get a synthesised answer from the appropriate panel of agents
effort: medium
context: fork
background: false
agent: senior-council
---

# Ask the Council

Pose a question to the Parliament. The Senior Council auto-selects 2–5 relevant specialists, consults them in parallel, and returns a single synthesised answer with points of agreement and disagreement surfaced.

This is a **question-answering** command. There is no fix loop, no artifact, no code edits, no voting.

## Usage

```
/ask-council <question>
```

**Examples**:

```
/ask-council What's the safest way to roll a JWT secret without logging users out?

/ask-council Should we use Postgres LISTEN/NOTIFY or a dedicated queue for async jobs?

/ask-council How does our auth flow handle token refresh today?

/ask-council What are the trade-offs between event sourcing and CRUD for an audit-heavy domain?
```

## When NOT to use

| Situation | Use this instead |
|---|---|
| You want a written plan or spec produced | `/summon-council plan <topic>` |
| You want code shipped | `/summon-council implement <topic>` |
| You want to formally decide between options with voting | `/debate-topic <topic>` |
| You want a single-domain expert opinion | `/summon-specialist <agent>` |
| You want code/design critiqued | `/parliament-review` or `/summon-grumpy-reviewer` |
| You want to know what an agent does | `/explain-agent <agent>` |

If the council infers your question is really one of the above, it will redirect you rather than guess.

## Process

### Step 1 — Classify the question

Senior Council reads the question and decides:

- **Q&A** (this command's purpose) — proceed.
- **Artifact request** ("design …", "build …", "plan …") — stop and direct user at `/summon-council [plan|implement]`.
- **Decision request** ("which should we pick", "A or B", "vote on …") — stop and direct user at `/debate-topic`.
- **Critique request** ("review …", "what's wrong with …") — stop and direct user at `/parliament-review`.
- **Single-agent request** ("ask the security knight …") — stop and direct user at `/summon-specialist`.

Never silently default. If ambiguous, ask the user.

### Step 2 — Lightweight inventory (only if question references the codebase)

If the question refers to project-specific code or behaviour ("how does *our* …", "what's *our* approach to …"), dispatch the `Explore` agent for a fast inventory pass — capture the 1–3 most relevant files and a one-line description each. Share with panellists.

If the question is purely conceptual ("what is X", "trade-offs of Y"), skip inventory.

Always state in the output whether inventory was run.

### Step 3 — Select the panel

Pick 2–5 specialists whose domains are most relevant to the question. Selection rules:

- **Default panel size**: 3. Expand to 4–5 only when the question genuinely spans that many domains. Contract to 2 only when no third domain is meaningfully relevant.
- **If only 1 domain is relevant**: stop and recommend `/summon-specialist <agent>` instead. A council of one is not a council.
- **Allowed specialists**: `api-keeper`, `backend-goblin`, `config-curator`, `data-warlock`, `dependency-detective`, `doc-bard`, `migration-monk`, `observability-oracle`, `package-wizard`, `pipeline-engineer`, `refactor-ranger`, `resilience-tamer`, `security-knight`, `system-architect`, `test-prophet`, `ui-ux-guru`.
- **Do not** invoke grumpy reviewers (they are critique-only — see `/parliament-review`).
- **Do not** invoke `project-oracle`, `scope-weaver`, `task-executor`, or `deliberation-conductor` — they have their own driving commands.
- **Security-touching questions** must include `security-knight`.
- **Cross-cutting architecture questions** should include `system-architect`.

State the panel and a one-line justification per agent in the output.

### Step 4 — Parallel consultation

Dispatch all selected specialists in parallel with the same prompt: the user's question, the inventory (if any), and an instruction to answer concisely from their domain lens. Each specialist returns:

- Their position / answer (1–3 paragraphs)
- Confidence (high / medium / low)
- Key caveats or assumptions
- Pointers to specific files or references where useful

This is the parallel-fan-out pattern — no review loop, no rebuttal rounds. One pass.

### Step 5 — Synthesise

Senior Council produces a single cohesive answer:

1. **Lead with the consensus** — what the panel agrees on.
2. **Surface disagreements** — when specialists diverge, attribute each view by name with a one-line summary of *why* they hold it. Do not flatten genuine conflict into false consensus.
3. **Apply conflict priority** when synthesising a recommendation: security > correctness > maintainability > performance > convenience.
4. **End with a recommendation** — the council's overall steer, even when the panel disagrees, with the reasoning that broke the tie.
5. **Suggest a follow-up** — if the answer implies action ("this needs to be designed properly", "this should be debated formally"), point at the right next command.

## Output

```
# Question
<restated user question>

## Panel Consulted
- agent-name — why this agent
- agent-name — why this agent
- ...

## Inventory
<files referenced, or "None — conceptual question.">

## Consensus
<what the panel agrees on, 1–3 paragraphs>

## Diverging Perspectives
<only if there is genuine disagreement>
- agent-name (confidence: H/M/L) — their view + reasoning
- agent-name (confidence: H/M/L) — their view + reasoning

## Recommendation
<the council's overall steer, with the priority logic that broke any tie>

## Suggested Follow-up
<one of: "no action needed", or the most relevant next command>
```

## Notes

- This is a single-pass command. Token cost scales with panel size (2–5 specialists at `effort: medium`) plus one synthesis pass at the council's `effort: high`. Expect roughly 2–3× the cost of `/summon-specialist`, and well under `/summon-council implement` or `/debate-topic`.
- Parallel fan-out to specialists is more reliable on Claude Code v2.1.128+, where a failing sibling tool call no longer cancels its parallel peers.
- The Senior Council's `answer` mode (this command) sits beside its `plan` and `implement` modes (`/summon-council`). It reuses the same auto-selection logic; only the output shape and process loop differ.
- Inventory is intentionally optional and lightweight here. Q&A questions that *don't* reference the codebase do not benefit from a grep pass and should not pay for one.
