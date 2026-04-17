---
description: Scaffold a new Architectural Decision Record (ADR) from a title or ongoing discussion
effort: medium
---

# ADR New

Scaffold a new Architectural Decision Record. ADRs are the typed record of why the project made a choice — without them, past decisions are untraceable and `/decision-review` has nothing to re-evaluate.

Parliament ADRs live in `.project-files/adrs/` so they stay with the project and survive plugin updates (per the `.project-files/` vs `${CLAUDE_PLUGIN_DATA}/` separation in `agent-standards.md`).

## Usage

```
/adr-new <title> [--from-session <id>] [--supersedes <adr-number>] [--status proposed|accepted]
```

**Examples**:
```
/adr-new "Adopt YAML manifest for commands"
/adr-new "Switch event log to NDJSON" --from-session fc777472
/adr-new "Retire grumpy-i18n-nitpicker" --supersedes 0007
```

## Options

- `<title>` (required, positional): Short decision title. Converted to a kebab-case slug.
- `--from-session <id>` (optional): Pull context from a past debate or council session. Imports the final vote, trade-offs, and deferred items into the ADR.
- `--supersedes <adr-number>` (optional): Reference an existing ADR that this one replaces. The old ADR is updated via `/adr-supersede`.
- `--status` (optional): `proposed` (default) or `accepted`. `proposed` requires later ratification.

## Process

1. **Pick a number** — next integer, zero-padded to 4 digits, scanning `.project-files/adrs/NNNN-*.md`.
2. **Slugify title** — lowercase, kebab-case, strip punctuation.
3. **Resolve context** — if `--from-session` is supplied, read the session transcript/debate artefact and summarise the deliberation into the *Context* and *Decision* sections. Otherwise use an interactive Q&A to fill them.
4. **Write the ADR** to `.project-files/adrs/NNNN-slug.md` using the template below.
5. **Index** — append an entry to `.project-files/adrs/INDEX.md` (create if missing): number, title, status, date, link.
6. **Supersede link** — if `--supersedes` given, invoke `/adr-supersede <old>` to close the previous ADR.

## ADR Template

```markdown
# NNNN — <Title>

- **Status**: proposed | accepted | deprecated | superseded-by-NNNN
- **Date**: YYYY-MM-DD
- **Deciders**: <agents or humans involved>
- **Relates to session**: <session id, if any>

## Context
Why are we deciding this now? What is the observable problem or opportunity?

## Decision
What did we decide? State it as a single clear sentence followed by supporting detail.

## Consequences
- Positive: ...
- Negative: ...
- Neutral: ...

## Alternatives considered
- Option A — rejected because ...
- Option B — rejected because ...

## Governance priority invoked
Which priority drove the choice? (security > correctness > maintainability > performance > convenience)

## References
- Source debate / council transcript
- Related ADRs
- External documents
```

## Output

```
# ADR Created

- File: .project-files/adrs/0012-adopt-yaml-manifest-for-commands.md
- Number: 0012
- Status: proposed
- Index updated: .project-files/adrs/INDEX.md

Next steps:
- Fill any remaining TODOs in the template
- Run /summon-council for ratification if status is proposed
- Link the ADR from related roadmap items or commits
```

## Notes

- ADRs are user-owned content — they live in `.project-files/adrs/`, not under `${CLAUDE_PLUGIN_DATA}/`.
- The numbering scheme is strictly monotonic — never reuse a retired number.
- Use `/adr-supersede` rather than editing a historical ADR in place.
- `/decision-review` reads these files to re-evaluate past decisions when context shifts.
- The `INDEX.md` file is regenerable from filenames if lost, but hand-maintenance gives a curated description.
