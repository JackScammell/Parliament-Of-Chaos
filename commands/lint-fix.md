---
description: Auto-detect and run the project's linter(s) with auto-fix
---

# Lint Fix

Detect the project's linter(s) and run them with auto-fix enabled on changed files. Parse remaining errors and explain how to fix them.

## Usage

```
/lint-fix [--all] [--no-fix] [files...]
```

**Examples**:
```
/lint-fix                            # Lint and fix changed files
/lint-fix --all                      # Lint and fix entire project
/lint-fix --no-fix                   # Report issues without auto-fixing
/lint-fix src/                       # Lint a specific directory
```

## Options

- `--all` (optional): Lint the entire project instead of just changed files
- `--no-fix` (optional): Report lint errors without auto-fixing (read-only mode)
- `files...` (optional): Specific files or directories to lint

## Process

1. **Detect Linters**
   - Check config files: `.eslintrc.*`, `eslint.config.*`, `.pylintrc`, `pyproject.toml` (Ruff/Pylint/Flake8), `.rubocop.yml`, `.golangci.yml`, `clippy` config
   - Check for multiple linters in the same project (ESLint + stylelint + markdownlint, etc.)
   - Read package manager scripts for lint commands
   - Detect language-specific defaults (Go: `golangci-lint`, Rust: `clippy`, etc.)

2. **Determine Scope**
   - Default: files changed in git working tree
   - `--all`: all files in the project
   - Explicit files: only the specified paths

3. **Run Linters**
   - Execute each detected linter with auto-fix flags (e.g. `--fix`, `--fix-unsafe`, `--auto-correct`)
   - If `--no-fix`: run in check/report mode only
   - Collect results from all linters

4. **Report Results**
   - Number of issues found and fixed per linter
   - Remaining unfixable issues with:
     - File path and line number
     - Rule name and description
     - Explanation of the issue
     - Suggested manual fix

## Output

```
# Lint Fix

**Linters detected**: ESLint 9.0 (from eslint.config.js), stylelint 16.0 (from .stylelintrc)
**Scope**: 12 changed files

## ESLint Results
- 8 issues found, 6 auto-fixed
- 2 remaining issues:

| File | Line | Rule | Issue | Fix |
|------|------|------|-------|-----|
| src/api.ts | 42 | @typescript-eslint/no-explicit-any | Explicit `any` type | Define a proper type or use `unknown` |
| src/utils.ts | 17 | no-unused-vars | `oldHelper` is defined but never used | Remove the unused function |

## stylelint Results
- 3 issues found, 3 auto-fixed
- 0 remaining issues

## Summary: 11 issues found, 9 auto-fixed, 2 require manual fix
```

## Notes

- Auto-fix respects each linter's safety levels (won't apply unsafe fixes unless the linter's config allows it)
- Handles multiple linters running on different file types in the same project
- If no linter is configured, detects the primary language and suggests one
