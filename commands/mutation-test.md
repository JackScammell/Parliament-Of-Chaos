---
description: Evaluate test quality by introducing code mutations and checking if tests catch them
effort: high
context: fork
background: false
---

# Mutation Test

Evaluate whether your tests actually catch bugs. Introduces small, systematic mutations into source code and checks if the test suite detects them. Surviving mutations reveal weak or missing assertions.

## Usage

```
/mutation-test [<path>] [--changed] [--limit <n>]
```

**Examples**:
```
/mutation-test src/services/auth.ts       # Mutate a specific file
/mutation-test --changed                   # Mutate only recently changed files
/mutation-test src/utils/ --limit 10       # Limit to 10 mutations per file
```

## Options

- `<path>` (optional): File or directory to target
- `--changed` (optional): Only mutate files changed since last commit
- `--limit` (optional): Maximum mutations per file (default: 20)

## Process

1. **Select Targets**
   - If `--changed`, use git diff to find modified files
   - Otherwise, use provided path or scan src/ for source files
   - Skip test files, config files, and generated code

2. **Generate Mutations**
   - Negate conditionals (`if (x > 0)` → `if (x <= 0)`)
   - Swap operators (`+` → `-`, `&&` → `||`, `==` → `!=`)
   - Remove return statements (return void instead)
   - Change boundary values (`>` → `>=`, `< n` → `< n+1`)
   - Remove method calls (especially side effects)
   - Swap true/false literals

3. **Execute Per Mutation**
   - Apply one mutation at a time (in worktree isolation)
   - Run the relevant test suite
   - Record: mutation killed (test failed) or survived (tests still pass)
   - Restore original code

4. **Report Results**
   - Mutation score: killed / total mutations
   - List surviving mutants with location and type
   - Prioritise by risk: mutations in auth/payment/data code ranked higher

## Output

```markdown
# Mutation Test Report

**Files tested**: 3
**Mutations generated**: 45
**Mutations killed**: 38 (84%)
**Mutations survived**: 7 (16%)

## Surviving Mutants (ranked by risk)
| # | File | Line | Mutation | Risk |
|---|------|------|----------|------|
| 1 | auth.ts:42 | Negated `isExpired` check | Critical |
| 2 | payment.ts:78 | Removed `validateAmount()` call | Critical |
| 3 | utils.ts:15 | Swapped `>` to `>=` | Low |

## Recommendation
Tests miss critical auth and payment edge cases. Run `/generate-tests auth.ts payment.ts` to fill gaps.
```

## Notes

- Runs in a worktree fork — never mutates your working directory
- Slow by nature (one test run per mutation) — use `--limit` and `--changed` for practical runtimes
- A mutation score below 70% suggests significant test quality gaps
- Pairs with `/generate-tests` to fix surviving mutants
