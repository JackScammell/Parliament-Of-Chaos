---
description: Mark an existing ADR as superseded and link it to its replacement
effort: low
---

# ADR Supersede

Close an existing Architectural Decision Record by marking it `superseded-by-NNNN` and linking to its replacement. This preserves the historical record — we never delete ADRs, we retire them.

## Usage

```
/adr-supersede <old-adr-number> [--by <new-adr-number>] [--reason <text>]
```

**Examples**:
```
/adr-supersede 0007 --by 0012
/adr-supersede 0003 --by 0014 --reason "Manifest replaces hardcoded list"
```

## Options

- `<old-adr-number>` (required): 4-digit ADR number to supersede.
- `--by <new-adr-number>` (optional): The replacement ADR. If omitted, the old ADR is marked `deprecated` without a forward link.
- `--reason <text>` (optional): One-line rationale appended to the old ADR's status section.

## Process

1. **Locate the file** — find `.project-files/adrs/NNNN-*.md` matching the supplied old number. Fail loudly if missing.
2. **Rewrite the status header** — change `Status:` to `superseded-by-NNNN` (or `deprecated` if no `--by`). Add a line `Superseded on: YYYY-MM-DD`. Append `Reason:` if supplied.
3. **Add forward link** — append a short `## Superseded by` section linking to the new ADR file.
4. **Update the replacement** — if `--by` given, ensure the new ADR's frontmatter includes `Supersedes: NNNN` pointing back. If missing, add it.
5. **Refresh the index** — update `.project-files/adrs/INDEX.md` so the row for the old ADR shows its new status and link.

## Output

```
# ADR Superseded

- Old: .project-files/adrs/0007-foo.md (status → superseded-by-0012)
- New: .project-files/adrs/0012-bar.md (Supersedes: 0007)
- Index: updated

The old ADR is preserved; only its status header and forward link were modified.
```

## Notes

- This command never deletes content. It only rewrites the status header, adds a forward link, and updates the index.
- If the target ADR is already marked superseded, the command exits with a warning and no changes.
- `/decision-review` uses the supersession chain to avoid re-evaluating decisions that are already retired.
- For mass rewrites, invoke `/adr-supersede` once per ADR — there is no bulk mode by design. Deliberate churn is the point.
