---
description: Find unreachable code, unused exports, and orphaned files across the project
effort: medium
---

# Dead Code Sweep

Scan for unreachable code, unused exports, unused functions/classes, dead CSS selectors, and orphaned files. Report-only by default — use `--apply` to remove dead code with a diff preview.

## Usage

```
/dead-code-sweep [--apply] [--scope <path>] [--type <type>]
```

**Examples**:
```
/dead-code-sweep                     # Report dead code across the project
/dead-code-sweep --apply             # Remove dead code (with diff preview before applying)
/dead-code-sweep --scope src/utils/  # Scan only a specific directory
/dead-code-sweep --type exports      # Only find unused exports
```

## Options

- `--apply` (optional): Remove detected dead code. Shows a full diff preview and asks for confirmation before applying changes.
- `--scope <path>` (optional): Limit the scan to a specific directory or file
- `--type <type>` (optional): Limit to a specific category — `exports`, `functions`, `imports`, `files`, `css`, `variables`

## Process

1. **Build Dependency Graph**
   - Parse the project's source files to build an import/export graph
   - Identify entry points (main files, route handlers, exports from `index` files, test files)
   - Trace references from entry points through the dependency tree
   - Account for dynamic imports, re-exports, and barrel files

2. **Detect Dead Code**
   - **Unused exports**: Exported symbols that are never imported anywhere
   - **Unused functions/classes**: Defined but never called or referenced (beyond their own file)
   - **Unused variables**: Module-level variables that are assigned but never read
   - **Orphaned files**: Source files not imported by any other file and not an entry point
   - **Dead CSS**: Selectors that don't match any elements in templates/JSX (if applicable)
   - **Unreachable code**: Code after unconditional returns, throws, or in impossible branches

3. **Filter False Positives**
   - Exclude files matching common generated/config patterns (`*.d.ts`, `*.config.*`, migrations, fixtures)
   - Preserve exports marked with `@public` or `@api` JSDoc tags
   - Preserve entry points defined in package.json `exports`, `main`, `bin` fields
   - Preserve symbols used in decorators, reflection, or DI containers where detectable
   - Flag uncertain cases separately from confident detections

4. **Report or Apply**
   - **Report mode** (default): List all detected dead code with file paths, line numbers, and confidence levels
   - **Apply mode**: Show a complete diff of proposed removals, ask for confirmation, then apply changes

## Output

```
# Dead Code Sweep

**Scope**: Full project (247 source files)
**Entry points**: 12 detected (routes, main, tests, package.json exports)

## Findings

### Unused Exports (7 found)
| File | Export | Confidence | Last Modified |
|------|--------|------------|---------------|
| src/utils/format.ts | formatCurrency | High | 2025-11-03 |
| src/utils/format.ts | formatPercentage | High | 2025-11-03 |
| src/helpers/legacy.ts | parseLegacyConfig | High | 2025-08-12 |
| src/types/internal.ts | OldUserSchema | Medium | 2025-09-20 |

### Orphaned Files (2 found)
| File | Size | Last Modified | Confidence |
|------|------|---------------|------------|
| src/utils/deprecated-parser.ts | 142 lines | 2025-07-15 | High |
| src/components/OldModal.tsx | 89 lines | 2025-06-22 | High |

### Unreachable Code (3 found)
| File | Lines | Type | Confidence |
|------|-------|------|------------|
| src/api/handler.ts | 45-52 | Code after unconditional return | High |
| src/auth/check.ts | 78-91 | Impossible branch (condition always false) | Medium |

### Uncertain (review manually)
| File | Symbol | Reason |
|------|--------|--------|
| src/types/internal.ts | OldUserSchema | May be used via runtime reflection |

## Summary: 12 dead code items found (10 high confidence, 2 medium)

Run `/dead-code-sweep --apply` to remove high-confidence items with diff preview.
```

## Notes

- Default mode is read-only — no code is modified unless `--apply` is explicitly used
- `--apply` always shows a diff and asks for confirmation before making changes
- Medium-confidence items are listed in "Uncertain" section and excluded from `--apply` by default
- Dynamic imports, reflection, and decorator patterns may cause false negatives — the scan is conservative
- For best results, ensure the project builds successfully before running the sweep
- Works across JS/TS, Python, Go, Rust, Java, Ruby — adapts analysis to the language's module system
