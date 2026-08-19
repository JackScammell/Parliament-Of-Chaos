---
description: Auto-detect and run all CI checks locally before committing
effort: medium
argument-hint: "[--fix] [--skip <step>]"
---

# Pre-Commit Check

Auto-detect the project's CI pipeline, linters, formatters, type checkers, and test suites. Run them all locally in the correct order to guarantee CI will pass before you push.

## Usage

```
/pre-commit-check [--fix] [--skip <step>]
```

**Examples**:
```
/pre-commit-check                    # Run all detected checks
/pre-commit-check --fix              # Auto-fix what can be fixed, then report remaining issues
/pre-commit-check --skip tests       # Skip test execution (e.g. for a docs-only change)
```

## Options

- `--fix` (optional): Automatically fix issues where possible (format code, fix lint errors) before reporting results
- `--skip <step>` (optional): Skip a specific step — `format`, `lint`, `typecheck`, `tests`, `secrets`

## Process

1. **Detect Toolchain**
   - Read CI config files (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.)
   - Read package manager files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, etc.)
   - Identify formatters, linters, type checkers, and test runners from config files and scripts
   - Detect pre-commit hooks (`.pre-commit-config.yaml`, `husky`, `lint-staged`)

2. **Run Checks in Order**
   Execute detected tools in dependency order:
   1. **Secrets scan** — Scan staged files for hardcoded API keys, tokens, passwords, private keys
   2. **Format check** — Run formatter in check mode (e.g. `prettier --check`, `black --check`)
   3. **Lint** — Run linter(s) (e.g. `eslint`, `ruff`, `golangci-lint`)
   4. **Type check** — Run type checker if present (e.g. `tsc --noEmit`, `mypy`, `pyright`)
   5. **Tests** — Run test suite (e.g. `jest`, `pytest`, `go test`)

3. **Report Results**
   - Show pass/fail for each step with summary
   - For failures: show the specific errors and suggest fixes
   - If `--fix` was used: show what was auto-fixed and what remains

## Output

```
# Pre-Commit Check Results

## Detected Toolchain
- Formatter: Prettier (from package.json)
- Linter: ESLint (from .eslintrc.js)
- Type checker: TypeScript (from tsconfig.json)
- Tests: Jest (from jest.config.ts)
- CI: GitHub Actions (from .github/workflows/ci.yml)

## Results

| Step | Status | Details |
|------|--------|---------|
| Secrets | PASS | No secrets detected in staged files |
| Format | FAIL | 3 files need formatting |
| Lint | PASS | No lint errors |
| Type check | PASS | No type errors |
| Tests | PASS | 142 tests passed |

## Issues to Fix
1. **Format**: Run `npx prettier --write src/foo.ts src/bar.ts src/baz.ts`

## Verdict: FIX REQUIRED (1 issue)
```

## Notes

- Runs against staged/changed files by default, not the entire project
- If no CI config is found, falls back to detecting tools from config files and package manager scripts
- Secret scanning checks for common patterns: API keys, AWS credentials, private keys, connection strings, tokens
- Use `--fix` for a one-command "make it all pass" workflow
- Want a guided commit + push workflow on top of these checks? Run `/commit-and-push` — it invokes this command, drafts a Conventional-Commit message, audits push safety, and prints the exact git commands for the developer to run (it never executes `git commit` or `git push` itself).
