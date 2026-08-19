---
description: Detect and update project documentation affected by recent code changes
effort: medium
context: fork
background: false
agent: senior-council
argument-hint: "[--scope branch|commit|staged] [--apply] [--create] [--dry-run]"
---

# Update Docs

After completing work on an issue or feature, detect project documentation that has become stale due to code changes and update it. Conservative by default — previews all changes and requires confirmation before applying.

## Usage

```
/update-docs [--scope branch|commit|staged] [--apply] [--create] [--dry-run]
```

**Examples**:
```
/update-docs                         # Preview doc updates for current branch vs main
/update-docs --apply                 # Preview then apply updates (with confirmation)
/update-docs --scope commit          # Only changes from the most recent commit
/update-docs --scope staged          # Only staged changes (pre-commit use)
/update-docs --create                # Also create new doc sections for undocumented features
/update-docs --dry-run               # Report what is stale without generating updates
```

## Options

- `--scope` (optional): What code changes to analyse
  - `branch` (default): Diff current branch against base branch (main/master)
  - `commit`: Only the most recent commit
  - `staged`: Only staged changes
- `--apply` (optional): Apply the proposed changes after user confirmation. Without this flag, changes are previewed only.
- `--create` (optional): Allow creation of new documentation sections for features that have zero existing docs. Off by default — creating docs is a design decision that should be intentional.
- `--dry-run` (optional): Report which docs are potentially stale and why, without generating any update content. Fastest mode for quick checks.

## Process

### Phase 1: Change Analysis

Delegate to relevant specialists to build a structured change manifest from the git diff:

- **Changed symbols**: Functions, classes, methods that were added, removed, renamed, or had signatures changed
- **Changed config**: New or modified environment variables, settings keys, feature flags
- **Changed CLI surface**: New or modified command arguments, options, usage patterns
- **Changed APIs**: Modified routes, request/response shapes, status codes
- **Renamed/moved files**: Detect via `git diff --diff-filter=R` to catch broken path references

This structured manifest drives the cross-referencing. Raw diffs alone are insufficient — a refactor that renames internals is different from a one-line behaviour change.

### Phase 2: Documentation Discovery

Scan the project for documentation files in priority order:

**Tier 1 — Always scan** (high-value, frequently stale):
- `README.md` and `**/README.md`
- `CHANGELOG.md`
- API reference docs (`docs/api*`, OpenAPI specs)
- Configuration docs (files referencing env vars, settings)
- Inline docstrings/JSDoc on changed functions

**Tier 2 — Scan when relevant** (context-dependent):
- Architecture docs (`docs/architecture*`, `docs/design*`)
- Contributing/development guides (`CONTRIBUTING.md`)
- Agent definitions (`agents/*.md`) — if agent behaviour changed
- Command definitions (`commands/*.md`) — if command behaviour changed
- Rules files (`.claude/rules/*.md`)

**Tier 3 — Flag but never edit**:
- Generated docs (detected by `<!-- AUTO-GENERATED -->` markers, presence of generation scripts in `package.json`/`Makefile`, or conventional paths like `docs/generated/`)
- External docs (wiki pages, Notion links) — flag as potentially stale

For each doc file, build an index of which code symbols, config keys, file paths, and API routes it references.

### Phase 3: Staleness Detection

Cross-reference the change manifest against the documentation index. Assign confidence levels:

| Confidence | Criteria | Action |
|-----------|----------|--------|
| **High** | Symbol renamed/removed and docs reference old name; function signature changed and docstring has old params | Update directly |
| **Medium** | Function body changed meaningfully, docs describe its behaviour; config key semantics changed | Update with review flag |
| **Low** | File in same module changed, docs mention the module generally | Flag for manual review only |

### Phase 4: Update Generation

Delegate writing to **doc-bard** with these constraints:

- **Never fabricate.** Every doc change must be traceable to a specific code change. If the behaviour of a new parameter is unclear from the code, write "TODO: document parameter `x`" rather than guessing.
- **Never edit generated files.** Report the regeneration command instead (e.g. "run `npm run docs:generate`").
- **Never delete documentation sections.** If code was removed, flag the orphaned docs for human review. Removed code might be moving, not disappearing.
- **Preserve formatting.** Match the existing heading style, list format, code fence language, and tone of the document being updated.
- **Cite provenance.** Each change must reference what triggered it (e.g. "`authenticate()` signature changed — added `scope` parameter").

### Phase 5: Validation and Review

Route through **grumpy-documentation-pedant** to validate:

- Updated docs reference symbols/paths that actually exist in the codebase
- No broken links introduced
- Formatting is consistent with the rest of the document
- No hallucinated parameter descriptions or fabricated behaviour claims
- Coverage report is accurate

### Phase 6: Present Results

Show the full report with diffs. If `--apply` was passed, ask for explicit confirmation before writing any files.

## Safety Checks

Before running, the command must verify:

1. **Clean target files.** If any documentation file that would be modified has uncommitted changes, warn the user and skip that file (to avoid clobbering in-progress work).
2. **Scope boundaries.** Only modify files matching the documentation patterns above. Never modify source code files (except inline docstrings on changed functions).
3. **No auto-apply without confirmation.** Even with `--apply`, show the full diff and require explicit "yes" before writing.

## Output

```
# Documentation Update Report

**Scope**: branch `feature/new-auth` vs `main` (14 files changed)
**Documentation scanned**: 32 files
**Potentially stale**: 5
**Updated**: 3 (pending confirmation)
**Flagged for manual review**: 1
**Generated (regenerate manually)**: 1

## Change Summary

| Changed Symbol | Type | Change |
|---------------|------|--------|
| `authenticate()` | function | Signature changed (added `scope` param) |
| `AUTH_PROVIDER` | config | New env var added |
| `SessionToken` | type | Field `expiresAt` renamed to `expiry` |

## Proposed Updates

### 1. docs/API_REFERENCE.md [HIGH confidence]
**Triggered by**: `authenticate()` signature change

```diff
- ### authenticate(username: string, password: string): Promise<Token>
+ ### authenticate(username: string, password: string, scope?: string): Promise<Token>

- Authenticates a user with username and password.
+ Authenticates a user with username and password. Optionally accepts a `scope`
+ parameter to limit the token's permissions.
```

### 2. README.md [HIGH confidence]
**Triggered by**: `AUTH_PROVIDER` env var added

```diff
  | `DATABASE_URL` | PostgreSQL connection string | Required |
+ | `AUTH_PROVIDER` | Authentication provider (local, oauth, saml) | Optional, defaults to `local` |
```

### 3. src/auth/session.ts — docstring [HIGH confidence]
**Triggered by**: `SessionToken.expiresAt` renamed to `expiry`

```diff
- * @property expiresAt - When the session token expires
+ * @property expiry - When the session token expires
```

## Flagged for Manual Review

### 4. docs/architecture/auth-flow.md [LOW confidence]
**Reason**: References authentication flow that changed. The diagram may need updating but the specific changes needed are unclear from the diff alone.

## Generated Docs (regenerate manually)

### 5. docs/generated/openapi.yaml
**Reason**: API routes changed. Regenerate with: `npm run docs:generate`

## Coverage Summary

| Category | Scanned | Updated | Flagged | Skipped |
|----------|---------|---------|---------|---------|
| README files | 3 | 1 | 0 | 0 |
| API docs | 4 | 1 | 0 | 1 (generated) |
| Config docs | 2 | 0 | 0 | 0 |
| Inline docstrings | 14 | 1 | 0 | 0 |
| Architecture docs | 5 | 0 | 1 | 0 |
| Command/agent defs | 4 | 0 | 0 | 0 |

## Not Covered (no documentation exists)
- `AUTH_PROVIDER` env var: No configuration guide found.
  Run with `--create` to generate a new section.
```

## Integration

This command fits naturally into the post-implementation workflow:

1. `/implement-task-list` — build the feature
2. `/update-docs` — update affected documentation
3. `/pre-commit-check` — verify everything passes
4. Commit and push

## Notes

- Delegates writing to doc-bard and validation to grumpy-documentation-pedant
- Preview-only by default — no files are modified without `--apply` and explicit confirmation
- Generated documentation is never edited — only flagged with the regeneration command
- Documentation sections are never deleted — only flagged for human review when source code is removed
- Every proposed change includes provenance (which code change triggered it) so the developer can verify correctness
- For large diffs (100+ files changed), focuses on Tier 1 docs only and suggests narrowing scope
- If no documentation exists at all, recommends `/onboard-codebase` instead
