---
description: Unified security check for dependencies, secrets, and vulnerability patterns
effort: medium
---

# Security Scan

Run a unified security check: dependency vulnerability audit, secret/credential detection in source code, and common vulnerability pattern scanning.

## Usage

```
/security-scan [--secrets] [--deps] [--patterns] [--changed]
```

**Examples**:
```
/security-scan                       # Full security scan (all checks)
/security-scan --secrets             # Secret detection only
/security-scan --deps                # Dependency vulnerability audit only
/security-scan --patterns            # Common vulnerability patterns only
/security-scan --changed             # Scan only changed files (secrets + patterns)
```

## Options

- `--secrets` (optional): Run only the secret/credential detection scan
- `--deps` (optional): Run only the dependency vulnerability audit
- `--patterns` (optional): Run only the common vulnerability pattern scan
- `--changed` (optional): Limit file scanning to changed files (applies to secrets and patterns, not deps)

## Process

1. **Secret Detection**
   - Scan source files for hardcoded credentials:
     - API keys (AWS, GCP, Azure, Stripe, GitHub, etc.)
     - Tokens (JWT, OAuth, bearer tokens)
     - Passwords and connection strings
     - Private keys (RSA, SSH, PGP)
     - Environment variable values committed to source
   - Check `.env` files committed to git (should be in `.gitignore`)
   - Flag high-entropy strings in suspicious contexts

2. **Dependency Vulnerability Audit**
   - Run the appropriate audit tool:
     - npm/yarn/pnpm: `npm audit` / `yarn audit` / `pnpm audit`
     - pip: `pip-audit` or `safety check`
     - Go: `govulncheck`
     - Rust: `cargo audit`
     - Ruby: `bundle audit`
     - PHP: `composer audit`
   - Report vulnerabilities by severity (critical, high, medium, low)
   - Show available patched versions where applicable

3. **Common Vulnerability Patterns**
   - Scan code for OWASP Top 10 patterns:
     - SQL injection (string concatenation in queries)
     - XSS (unescaped user input in templates/HTML)
     - Command injection (`exec`, `system`, `eval` with user input)
     - Path traversal (user input in file paths without sanitisation)
     - Insecure deserialization
     - Hardcoded cryptographic keys or weak algorithms
   - Language-aware pattern matching (different patterns for different stacks)

4. **Report Results**
   - Issues grouped by category (secrets, dependencies, patterns)
   - Severity rating for each finding
   - Specific file locations and line numbers
   - Remediation guidance for each issue

## Output

```
# Security Scan

**Scope**: Full project scan

## Secret Detection
- 2 issues found

| Severity | File | Line | Finding |
|----------|------|------|---------|
| CRITICAL | src/config.ts | 12 | AWS access key ID (AKIA...) |
| HIGH | .env.example | 5 | Contains actual database password |

## Dependency Vulnerabilities
- 3 vulnerabilities found (npm audit)

| Severity | Package | Vulnerability | Fix |
|----------|---------|---------------|-----|
| HIGH | lodash@4.17.20 | Prototype pollution (CVE-2021-23337) | Upgrade to 4.17.21 |
| MEDIUM | axios@0.21.1 | SSRF (CVE-2021-3749) | Upgrade to 0.21.2 |
| LOW | minimist@1.2.5 | Prototype pollution | Upgrade to 1.2.6 |

## Vulnerability Patterns
- 1 issue found

| Severity | File | Line | Pattern | Detail |
|----------|------|------|---------|--------|
| HIGH | src/api/users.ts | 34 | SQL injection | String template in database query |

## Summary: 6 issues (2 critical, 2 high, 1 medium, 1 low)
```

## Notes

- Secret detection uses pattern matching and entropy analysis — may produce false positives on test fixtures
- Dependency audit requires the appropriate package manager to be installed
- Pattern scanning is heuristic-based — findings should be verified manually
- Use `--changed` in pre-commit workflows for speed; use full scan periodically
