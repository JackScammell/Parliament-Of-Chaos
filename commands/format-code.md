---
description: Auto-detect and run the project's code formatter
---

# Format Code

Detect the project's formatter(s) and run them on changed files. Zero-config — works by reading existing project configuration.

## Usage

```
/format-code [--all] [--check] [files...]
```

**Examples**:
```
/format-code                         # Format changed files (git diff)
/format-code --all                   # Format entire project
/format-code --check                 # Check only, don't modify files
/format-code src/utils.ts            # Format specific file(s)
```

## Options

- `--all` (optional): Format the entire project instead of just changed files
- `--check` (optional): Report unformatted files without modifying them
- `files...` (optional): Specific files or directories to format

## Process

1. **Detect Formatter**
   - Check config files: `.prettierrc`, `.prettierrc.json`, `pyproject.toml` (Black/Ruff), `rustfmt.toml`, `.clang-format`, `.editorconfig`
   - Check package manager scripts: `package.json` scripts containing `prettier`, `format`, etc.
   - Check for Go (`gofmt`/`goimports`), Rust (`rustfmt`), Python (`black`, `ruff format`, `autopep8`), PHP (`php-cs-fixer`)
   - If multiple formatters detected (e.g. Prettier + stylelint), run all in correct order

2. **Determine Scope**
   - Default: files changed in git working tree (`git diff --name-only` + `git diff --staged --name-only`)
   - `--all`: all files matching formatter's configured file patterns
   - Explicit files: only the specified paths

3. **Run Formatter**
   - Execute the detected formatter with appropriate flags
   - If `--check`: use check/verify mode and report which files need formatting
   - Otherwise: format files in place

4. **Report Results**
   - Number of files formatted or checked
   - Any files that could not be formatted (parse errors, etc.)
   - If no formatter detected: suggest one based on the project's language

## Output

```
# Format Code

**Formatter**: Prettier 3.2.0 (from .prettierrc.json)
**Scope**: 7 changed files

## Results
- 4 files formatted
- 3 files already formatted
- 0 errors

All files formatted successfully.
```

## Notes

- Respects existing ignore files (`.prettierignore`, `.gitignore`, etc.)
- If no formatter is configured, detects the primary language and offers to set one up
- For monorepos with multiple formatters, runs the correct formatter per file type
