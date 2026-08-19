---
description: Detect flaky tests, stale assertions, and non-deterministic test patterns
effort: medium
argument-hint: "[--flaky-check <n>] [--stale] [--coupling]"
---

# Test Health

Analyse the test suite for reliability and quality problems beyond coverage: flaky patterns, stale assertions, test coupling, and non-deterministic behaviour.

## Usage

```
/test-health [--flaky-check <n>] [--stale] [--coupling]
```

**Examples**:
```
/test-health                         # Full health check (static analysis)
/test-health --flaky-check 5         # Run tests 5 times, report inconsistent results
/test-health --stale                 # Find tests asserting against outdated code
/test-health --coupling              # Detect tests that fail in isolation
```

## Options

- `--flaky-check <n>` (optional): Run the test suite N times and report tests with inconsistent results
- `--stale` (optional): Find tests whose assertions reference code structures that no longer exist
- `--coupling` (optional): Detect tests that share mutable state or depend on execution order

## Process

1. **Static Analysis** (always runs)
   - Detect timing-dependent patterns: `setTimeout`, `sleep`, `Date.now()`, `time.time()`
   - Find unseeded random data: `Math.random()`, `random.choice()` without seeds
   - Flag timezone-dependent assertions
   - Identify global state mutations between tests
   - Find hardcoded file paths or ports that may conflict

2. **Stale Test Detection** (if `--stale`)
   - Cross-reference test assertions with current source code
   - Find tests that import or reference deleted functions/classes
   - Detect tests asserting against outdated return shapes or error messages

3. **Coupling Detection** (if `--coupling`)
   - Identify shared mutable state (class variables, global state, database fixtures)
   - Flag tests that modify shared resources without cleanup
   - Detect test ordering dependencies

4. **Flaky Detection** (if `--flaky-check`)
   - Run the full suite N times
   - Track pass/fail per test across runs
   - Report tests with inconsistent results and probable cause

## Output

```markdown
# Test Health Report

**Tests analysed**: 342
**Health score**: 78/100

## Issues Found

### Flaky Risk (Static Analysis)
| Test | Pattern | Risk |
|------|---------|------|
| test_timeout.py:15 | Uses `time.sleep(0.1)` for synchronisation | High |
| test_api.js:42 | Uses `Date.now()` in assertion | Medium |

### Stale Tests
| Test | Issue |
|------|-------|
| test_legacy.py:30 | Imports `OldService` which was deleted in abc123 |

### Coupled Tests
| Tests | Shared State |
|-------|-------------|
| test_user.py:10, test_order.py:25 | Both modify `global_db` without teardown |
```

## Notes

- Static analysis is fast and always runs
- `--flaky-check` is slow (N full test runs) — use selectively
- Pairs with `/run-tests` for execution and `/generate-tests` for fixes
