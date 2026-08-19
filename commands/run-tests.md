---
description: Auto-detect and run the project's test suite with intelligent options
effort: low
argument-hint: "[--changed] [--coverage] [--explain] [--all] [files...]"
---

# Run Tests

Detect the project's test framework and run the test suite. Supports running only tests affected by current changes, coverage reporting, and failure explanation.

## Usage

```
/run-tests [--changed] [--coverage] [--explain] [--all] [files...]
```

**Examples**:
```
/run-tests                           # Run full test suite
/run-tests --changed                 # Only tests affected by current git changes
/run-tests --coverage                # Run with coverage report
/run-tests --explain                 # Parse failures and suggest fixes
/run-tests --changed --explain       # Changed tests with failure explanations
/run-tests src/utils/                # Run tests for specific path
```

## Options

- `--changed` (optional): Only run tests affected by files changed in git. Uses import graph analysis to find related test files.
- `--coverage` (optional): Include coverage report. Highlight untested critical paths.
- `--explain` (optional): For any failures, read the test and source code, explain what went wrong, and suggest a fix.
- `--all` (optional): Explicitly run the full suite (default behaviour, useful to override project-level defaults)
- `files...` (optional): Specific test files or source directories to test

## Process

1. **Detect Test Framework**
   - Check config files: `jest.config.*`, `vitest.config.*`, `pytest.ini`, `pyproject.toml`, `phpunit.xml`, `.rspec`, `Cargo.toml`
   - Check package manager scripts for test commands
   - Detect framework from test file patterns (`*.test.ts`, `*_test.go`, `test_*.py`, `*_spec.rb`)

2. **Determine Scope**
   - Default: full test suite using the project's configured test command
   - `--changed`: analyse `git diff` to find changed source files, then trace the import graph to identify which test files exercise those changes
   - Explicit files: only the specified paths

3. **Run Tests**
   - Execute the detected test runner with appropriate flags
   - If `--coverage`: enable coverage collection (e.g. `--coverage`, `--cov`, `-cover`)
   - Stream output in real-time where possible

4. **Report Results**
   - Test count: passed, failed, skipped
   - If `--coverage`: coverage summary with uncovered critical paths highlighted
   - If `--explain` and failures exist: read failing test + source code and provide diagnosis

## Output

```
# Run Tests

**Framework**: Jest 29.7 (from jest.config.ts)
**Scope**: Changed files (4 test files from 7 changed source files)

## Results
- 47 tests run: 45 passed, 1 failed, 1 skipped
- Duration: 3.2s

## Failures

### src/utils/__tests__/parser.test.ts > parseInput > handles empty strings

**Expected**: `null`
**Received**: `""`

**Explanation**: The `parseInput` function at `src/utils/parser.ts:23` returns an empty string for empty input, but the test expects `null`. The function's early return (`if (!input) return input`) preserves the empty string because `""` is falsy but `!input` returns `true`, so `return input` returns `""` not `null`.

**Suggested fix**: Change line 23 to `if (!input) return null` if the intended behaviour is to normalise all falsy inputs to `null`.

## Coverage (if --coverage)
- Statements: 87.3%
- Branches: 72.1%
- Functions: 91.5%
- Uncovered critical paths:
  - `src/auth/session.ts` lines 45-67 (session refresh logic — 0% branch coverage)
```

## Notes

- `--changed` uses static import analysis — it may miss dynamic imports or runtime-only dependencies
- `--explain` reads source code to provide context-aware diagnosis, not just stack traces
- Coverage thresholds are read from project config if available
- For monorepos, detects and runs the appropriate test runner per package
