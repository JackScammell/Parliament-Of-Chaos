---
description: Risk-prioritised test coverage analysis — find the most dangerous untested code
effort: medium
---

# Coverage Audit

Go beyond numeric coverage percentages. Run tests with coverage instrumentation, then classify uncovered code by risk to produce a prioritised list of what needs testing most.

## Usage

```
/coverage-audit [--generate] [--threshold <percent>]
```

**Examples**:
```
/coverage-audit                      # Analyse coverage and prioritise gaps
/coverage-audit --generate           # Analyse gaps then generate tests for top priorities
/coverage-audit --threshold 80       # Flag modules below 80% coverage
```

## Options

- `--generate` (optional): After analysis, auto-generate tests for the highest-risk uncovered code (chains to `/generate-tests`)
- `--threshold` (optional): Minimum coverage percentage to flag modules below (default: no threshold, prioritise by risk)

## Process

1. **Run Coverage**
   - Detect test framework and coverage tool
   - Run tests with coverage instrumentation
   - Parse coverage report (lcov, coverage.py, Istanbul, etc.)

2. **Identify Uncovered Code**
   - Extract all uncovered lines, branches, and functions
   - Map to source files and functions

3. **Classify by Risk**
   - **Critical**: Auth logic, payment processing, data mutation, encryption
   - **High**: API endpoints, database operations, error handlers
   - **Medium**: Business logic, validation, data transformation
   - **Low**: Utility functions, formatters, logging

4. **Prioritise**
   - Rank by: risk category, code complexity, recent change frequency (git log)
   - Produce top-10 "most dangerous untested functions" list

5. **Generate** (if `--generate`)
   - Feed top priorities to `/generate-tests` workflow
   - Generate tests for highest-risk uncovered code first

## Output

```markdown
# Coverage Audit

**Overall**: 72% line coverage, 58% branch coverage

## Top 10 Untested Critical Paths
| # | File | Function | Risk | Lines |
|---|------|----------|------|-------|
| 1 | src/auth/verify.ts | verifyToken() | Critical | 15 uncovered |
| 2 | src/payments/charge.ts | processPayment() | Critical | 23 uncovered |

## Modules Below Threshold
| Module | Coverage | Gap |
|--------|----------|-----|
| src/auth/ | 45% | 35% below threshold |
```

## Notes

- Requires the project to have a test suite with coverage support
- Risk classification uses heuristics based on file paths, function names, and code patterns
- Pairs with `/generate-tests --coverage-gaps` for automated gap filling
