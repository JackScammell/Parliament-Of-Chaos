---
description: Drive grumpy-i18n-nitpicker to audit the project for hardcoded strings, missing translations, and locale bugs
effort: medium
argument-hint: "[--scope <path>] [--locale <code>] [--severity <level>] [--since <ref>]"
---

# I18n Audit

Invoke the `grumpy-i18n-nitpicker` reviewer to inspect the project (or a specified scope) for internationalisation problems. This command is the **driver** for the i18n reviewer — without it, the agent has no entry point and is effectively dead weight.

## Usage

```
/i18n-audit [--scope <path>] [--locale <code>] [--severity <level>] [--since <ref>]
```

**Examples**:
```
/i18n-audit                              # Audit the whole project
/i18n-audit --scope src/ui/              # Scan only the UI directory
/i18n-audit --locale en-GB               # Treat en-GB as the source locale
/i18n-audit --severity high              # Only surface High and Critical findings
/i18n-audit --since HEAD~20              # Only files changed since 20 commits ago
```

## Options

- `--scope <path>`: Limit the audit to a directory or file. Defaults to the full project.
- `--locale <code>`: Declare the project's source locale (BCP-47). Defaults to `en`.
- `--severity <level>`: Minimum severity to surface (Low / Medium / High / Critical). Defaults to Low.
- `--since <git-ref>`: Restrict to files changed since the given git ref — useful for PR review. Omit for a full sweep.

## Process

1. **Detect i18n framework** — look for typical signals:
   - JS/TS: `i18next`, `react-intl`, `lingui`, `formatjs`, `vue-i18n`
   - Python: `gettext`, `babel`, `django.utils.translation`
   - Ruby/Rails: `I18n`, `en.yml` files under `config/locales/`
   - Go: `go-i18n`, catalog files
   - Other: generic key-value JSON/YAML locale files
2. **Enumerate candidate strings** — scan source within `--scope` for user-facing literals (React JSX text, `alert()`, template strings in UI components, logged user messages, API error messages).
3. **Check coverage** — for each candidate, determine whether it flows through the i18n framework or is a raw literal.
4. **Check pluralisation & formatting** — look for `+` string concatenation of translated fragments, date/number/currency formatting that bypasses the locale API, and hardcoded singular/plural heuristics.
5. **Invoke grumpy-i18n-nitpicker** via `Task(grumpy-i18n-nitpicker)` with the collected findings. The reviewer applies its critique framework and produces a verdict.
6. **Report** — surface findings in the project's review format (summary, issues with severity, recommendations, verdict).

## Output

```
# I18n Audit

**Scope**: src/ui/
**Locale**: en
**Framework detected**: react-intl
**Files scanned**: 142
**Candidate strings**: 318 (214 through framework, 104 raw literals)

## Verdict
REJECT — 23 High-severity issues must be fixed.

## Issues

### Critical (0)
—

### High (23)
| File | Line | Issue | Suggested fix |
|------|------|-------|---------------|
| src/ui/Header.tsx | 34 | Raw string "Welcome back" | Wrap with <FormattedMessage id="header.welcome" /> |
| src/ui/Cart.tsx   | 88 | Manual pluralisation `${n} item${n===1?'':'s'}` | Use ICU plural: {count, plural, one {# item} other {# items}} |
| ...               | ... | ...   | ... |

### Medium (41)
[collapsed — expand with --severity medium]

### Low (40)
[collapsed]

## Recommendations
1. Introduce a lint rule (`@formatjs/enforce-placeholder-style`) to prevent regression.
2. Pipe date formatting through the existing `formatDate(locale, value)` helper rather than `toLocaleDateString()` directly.
3. Extract hardcoded SVG text to translatable labels.

## Next Steps
- Run `/i18n-audit --severity high` after fixes to confirm the reviewer approves.
- Pair with `/summon-specialist refactor-ranger` to apply mechanical replacements.
```

## Notes

- This command is a Tier 1 hygiene item from the toolset-gaps plan — the reviewer exists but had no driver until v1.10.0.
- Running with `--since` is the recommended pattern inside a pull-request review. Full-project runs are best scheduled via `/parliament-loop`.
- If no i18n framework is detected, the audit falls back to a pure "hardcoded string" scan and flags the absence of a framework as a High issue.
- The reviewer never modifies source — its output is advisory. Use `/summon-specialist` to apply fixes.
