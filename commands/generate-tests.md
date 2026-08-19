---
description: Generate tests for existing code following project conventions
effort: medium
argument-hint: "[<path>] [--changed] [--type <unit|integration|e2e>] [--coverage-gaps]"
---

# Generate Tests

Write tests for existing source code. Reads the target code, detects the project's test framework and conventions, and generates comprehensive test files.

## Usage

```
/generate-tests [<path>] [--changed] [--type <unit|integration|e2e>] [--coverage-gaps]
```

**Examples**:
```
/generate-tests src/services/PaymentService.ts    # Tests for a specific file
/generate-tests --changed                          # Tests for all changed files
/generate-tests src/controllers/ --type integration # Integration tests for a directory
/generate-tests --coverage-gaps                     # Fill gaps from coverage report
```

## Options

- `<path>` (optional): File or directory to generate tests for
- `--changed` (optional): Generate tests for files changed since last commit
- `--type` (optional): Test type — `unit` (default), `integration`, or `e2e`
- `--coverage-gaps` (optional): Run coverage first, then generate tests for uncovered critical paths

## Process

1. **Detect Test Framework**
   - Identify: Jest, Vitest, pytest, PHPUnit, Go testing, RSpec, JUnit, etc.
   - Read existing tests for assertion style, mocking patterns, and naming conventions

2. **Analyse Source Code**
   - Identify public API surface, branches, and error paths
   - Map dependencies that need mocking
   - Identify edge cases: null inputs, empty collections, boundary values, error conditions

3. **Generate Tests**
   - Create test file in the correct location following project structure
   - Cover: happy path, edge cases, error handling, boundary conditions
   - Use the project's assertion style and mocking patterns
   - Include descriptive test names that explain intent

4. **Validate**
   - Run generated tests to verify they pass
   - Fix any failing tests
   - Run formatter on generated files

## Output

```
Generated:
  - tests/services/PaymentService.test.ts (12 tests)
    ✓ 4 happy path tests
    ✓ 5 edge case tests
    ✓ 3 error handling tests

All 12 tests passing.
```

## Notes

- Reads existing tests to match your exact conventions — never generates alien-looking tests
- With `--coverage-gaps`, prioritises untested code by risk (auth, payments, data mutation)
- Tests are generated in a worktree to avoid polluting your working directory until approved
