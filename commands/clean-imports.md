---
description: Remove unused imports and organise import ordering across changed files
---

# Clean Imports

Remove unused imports, sort and organise imports according to project conventions, and fix import ordering across changed files. Works across languages.

## Usage

```
/clean-imports [--all] [--check] [files...]
```

**Examples**:
```
/clean-imports                       # Clean imports in changed files
/clean-imports --all                 # Clean imports across the entire project
/clean-imports --check               # Report issues without modifying files
/clean-imports src/components/       # Clean imports in a specific directory
```

## Options

- `--all` (optional): Process the entire project instead of just changed files
- `--check` (optional): Report unused/unordered imports without modifying files
- `files...` (optional): Specific files or directories to process

## Process

1. **Detect Language and Conventions**
   - Identify the project's language(s) from file extensions and config
   - Check for import ordering rules:
     - ESLint `import/order` or `simple-import-sort` config
     - Python `isort` config in `pyproject.toml` or `.isort.cfg`
     - Go `goimports` conventions
     - Java/Kotlin import group ordering
   - If no explicit config, use language-standard conventions

2. **Analyse Imports**
   - Parse each file's import statements
   - Resolve which imports are actually used in the file
   - Identify:
     - Unused imports (imported but never referenced)
     - Duplicate imports (same module imported twice)
     - Side-effect imports that should be preserved (e.g. `import './polyfill'`, `import _ "net/http/pprof"`)
     - Type-only imports that could use `import type` (TypeScript)

3. **Fix Imports**
   - Remove unused imports (preserving side-effect imports)
   - Sort imports according to project conventions or language defaults:
     - **JS/TS**: Built-ins, external packages, internal aliases, relative imports
     - **Python**: stdlib, third-party, local (isort compatible)
     - **Go**: stdlib, external, internal
     - **Java**: java.*, javax.*, third-party, project
   - Convert to `import type` where applicable (TypeScript)
   - Remove duplicate imports, merging named imports where possible

4. **Report Results**
   - Number of files processed
   - Imports removed, reordered, or converted per file
   - Any files skipped (parse errors, generated code, etc.)

## Output

```
# Clean Imports

**Languages**: TypeScript, CSS
**Scope**: 9 changed files
**Convention**: ESLint import/order (from eslint.config.js)

## Results

| File | Removed | Reordered | Type-converted |
|------|---------|-----------|----------------|
| src/api/client.ts | 2 | yes | 1 |
| src/components/Header.tsx | 1 | yes | 0 |
| src/utils/index.ts | 0 | yes | 3 |

## Summary: 3 unused imports removed, 3 type imports converted, 9 files reordered
```

## Notes

- Preserves side-effect imports (`import './styles.css'`, `import 'reflect-metadata'`)
- Respects `eslint-disable` comments on import lines
- For generated files (detected via headers like `// Code generated`), skips processing
- In `--check` mode, exits with a non-zero summary if issues are found (useful for CI)
