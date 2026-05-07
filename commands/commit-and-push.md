---
description: Guided commit + push helper that drafts the commit message and prints the exact git commands for the developer to run — never executes them
effort: medium
---

# Commit and Push

Pre-flight a commit and push: audit working tree, run the project's standard
checks, draft a Conventional-Commit message, audit push safety, and emit the
exact git commands as a copy-paste block for the developer to run themselves.

> **This command will NOT run `git commit`, `git push`, `git tag`,
> `git reset --hard`, `git rebase`, or any other state-changing git command.**
> Commit and push are explicit developer actions. Parliament prepares the
> ingredients; the developer is the one who pulls the trigger.

## Usage

```
/commit-and-push [--message <subject>] [--scope <area>] [--type <conv-type>]
                 [--skip-checks] [--allow-protected] [--first-push]
```

**Examples**:
```
/commit-and-push                                  # Full pre-flight + drafted message
/commit-and-push --type fix --scope hooks         # Force conventional-commit type/scope
/commit-and-push --message "Tighten env-doctor"   # Use this subject; draft the body
/commit-and-push --skip-checks                    # Skip /pre-commit-check (still runs secret scan)
/commit-and-push --first-push                     # Print `git push -u origin <branch>` form
/commit-and-push --allow-protected                # Permit drafting a push to main/master (still does not run it)
```

## Options

- `--message <subject>` (optional): Override the drafted commit subject. Body is still drafted from the diff.
- `--scope <area>` (optional): Conventional-commit scope (`feat(hooks): …`).
- `--type <conv-type>` (optional): Conventional-commit type — `feat`, `fix`, `docs`, `refactor`, `chore`, `perf`, `test`, `build`, `ci`. Inferred from diff if omitted.
- `--skip-checks` (optional): Skip the full `/pre-commit-check` pass. **A secret scan is still performed** — that one is non-negotiable.
- `--allow-protected` (optional): Permit drafting a push command targeting `main` / `master` / a branch matching `release/*` or `production/*`. Without this flag, the command refuses to render the push line for protected branches and tells the developer to use a feature branch or `--allow-protected` deliberately.
- `--first-push` (optional): Render `git push -u origin <branch>` instead of plain `git push`.

## Process

The command MUST NOT invoke any of the following from its own tool calls,
under any circumstances: `git commit`, `git push`, `git push --force`,
`git tag`, `git reset --hard`, `git rebase`, `git rebase --continue`,
`git cherry-pick`, `git revert`, `git filter-branch`, `git update-ref`,
`git stash drop`, `git clean -f`, `git remote add`, `git remote remove`.
All such operations are emitted as text for the developer to execute.

1. **Detect git state** (read-only)
   - `git rev-parse --is-inside-work-tree` — confirm we're in a repo.
   - `git symbolic-ref --short HEAD` — current branch (or detect detached HEAD).
   - `git status --porcelain=v1` — modified, staged, untracked.
   - `git rev-list --left-right --count @{u}...HEAD` — ahead/behind upstream (if upstream exists).
   - `git diff --stat` and `git diff --cached --stat` — change summary.
   - Detect: empty commit (no staged + no unstaged changes), detached HEAD,
     untracked files, ignored-but-staged files, large blobs (>1MB), files
     whose names match secret patterns (`.env`, `.env.*`, `*.pem`, `id_rsa`,
     `*.key`, `credentials.json`, `service-account*.json`).

2. **Refuse early on hard stops**
   - Detached HEAD: refuse, suggest creating a branch first.
   - Empty working tree: refuse with a message saying there is nothing to commit.
   - Merge / rebase in progress (`.git/MERGE_HEAD`, `.git/rebase-merge/`):
     refuse and point at `/git-workflow resolve-conflicts`.

3. **Run pre-flight checks**
   - Default: invoke `/pre-commit-check` and capture pass/fail per step.
   - With `--skip-checks`: invoke `/security-scan --secrets-only` (or the
     project's secret-scan equivalent) instead. Never skip secret scanning.
   - If any check fails: stop here. Print the failures, tell the developer
     to fix and re-run `/commit-and-push`.

4. **Draft the commit message**
   - **Type**: from `--type`, else inferred — new files / new public API → `feat`,
     bug-shaped diffs (`fix`, `bug`, error-handling churn) → `fix`,
     `*.md` only → `docs`, test-only → `test`, dependency bumps → `chore(deps)`.
   - **Scope**: from `--scope`, else inferred from the most-touched top-level
     directory (`hooks`, `commands`, `agents`, `src/deliberation`, …).
   - **Subject**: from `--message`, else a one-line summary derived from the
     diff. Imperative mood, no trailing period, ≤72 chars.
   - **Body**: 2–5 lines summarising *why*, drawn from the diff. Lists files
     touched only when the change is small enough to enumerate.
   - **Footer** (only when relevant): `BREAKING CHANGE: …` if the diff
     removes a public surface, `Refs: <issue>` if the branch name encodes one.
   - Match the style of the last 5 commits on the branch (sentence case vs.
     conventional, body presence, line length).

5. **Audit push safety** (no mutation)
   - Branch is `main` / `master` / matches `release/*` / `production/*` →
     refuse to render the push line unless `--allow-protected` is set.
   - No upstream configured → render `git push -u origin <branch>` and note
     that this will create the upstream.
   - Behind upstream → recommend a `git pull --rebase` step *before* the push,
     printed as text for the developer to run, not executed.
   - Force-push pattern (rewriting already-pushed commits) → never render
     `git push --force`. Explain why and suggest a fresh branch.
   - Untracked secret-pattern files → render an explicit warning above the
     copy-paste block.

6. **Emit the developer-only command block**
   - One fenced `bash` block, clearly preceded by a banner.
   - The banner reads: *"Parliament will NOT run the following. Read the
     diff, read the message, then run these yourself:"*
   - The block ends with a single suggested follow-up (`/ci-watch`).

## Output

```markdown
# Commit and Push — Pre-flight

**Branch**: feat/hooks-cleanup → origin/feat/hooks-cleanup (ahead 3, behind 0)
**Working tree**: 4 staged, 2 unstaged, 0 untracked
**Hard stops**: none

## Change Summary
- src/hooks/log_event.sh        | 18 ++++++--
- src/hooks/_common.sh          |  6 ++++
- commands/env-doctor.md        | 12 +++---

## Pre-flight Checks
| Step       | Status | Detail                                  |
|------------|--------|-----------------------------------------|
| Secrets    | PASS   | No secrets detected in staged files     |
| Format     | PASS   | shfmt clean                             |
| Lint       | PASS   | shellcheck clean                        |
| Type check | N/A    | No type checker configured              |
| Tests      | PASS   | 47 passed                               |

## Drafted Commit Message
```
fix(hooks): tighten log_event.sh argument validation

Reject empty event names and unrecognised hook types early, and emit a
single-line warning to stderr instead of a full stack trace. Matches the
defensive style already used in _common.sh and silences noisy CI logs.

Refs: feedback_hooks_location
```

## Push Audit
- Target: `origin/feat/hooks-cleanup` (upstream exists)
- Protected branch: no
- Force-push required: no
- Rebase recommended: no
- Secret-name files in diff: none

---

## RUN THESE YOURSELF

> Parliament will NOT run the following. Read the diff, read the message,
> then run these yourself:

```bash
git add src/hooks/log_event.sh src/hooks/_common.sh commands/env-doctor.md

git commit -m "fix(hooks): tighten log_event.sh argument validation" -m "
Reject empty event names and unrecognised hook types early, and emit a
single-line warning to stderr instead of a full stack trace. Matches the
defensive style already used in _common.sh and silences noisy CI logs.

Refs: feedback_hooks_location
"

git push
```

## Next
- After pushing, run `/ci-watch` to follow the pipeline.
- If you want to amend the message, edit the `git commit` line above before pasting.
```

## Refusal Output Examples

When the command refuses to render commands:

```markdown
# Commit and Push — Refused

**Reason**: HEAD is detached at `a1b2c3d`. Commits made here are easy to lose.

## Suggested fix
1. Create a branch first:
   ```bash
   git switch -c <branch-name>
   ```
2. Re-run `/commit-and-push`.
```

```markdown
# Commit and Push — Refused

**Reason**: A merge is in progress (`.git/MERGE_HEAD` exists).

## Suggested fix
- Run `/git-workflow resolve-conflicts` to walk through the remaining conflicts.
- After all conflicts are resolved and staged, re-run `/commit-and-push`.
```

## Notes

- **Read-only by design.** The command never executes mutating git operations.
  It runs read-only git plumbing (`status`, `rev-parse`, `diff --stat`,
  `rev-list --count`, `symbolic-ref`) and the project's existing pre-flight
  checks. That's it.
- **Secret scan is mandatory.** `--skip-checks` skips lint/format/typecheck/tests
  but never the secret scan. A commit that leaks credentials is the one error
  this command exists to prevent.
- **Protected branches require explicit opt-in.** A push to `main` / `master` /
  `release/*` / `production/*` is refused without `--allow-protected`. Even
  with the flag, the command still does not run the push — it just renders
  the command line.
- **Force pushes are never rendered.** If the command detects that a push
  would require `--force` or `--force-with-lease`, it explains why and
  recommends a fresh branch. The developer can still run a force push by
  hand if they really want to; this command will not generate it.
- **Companion commands**:
  - `/pre-commit-check` — the verification step, invoked upstream.
  - `/security-scan` — secret scan when checks are skipped.
  - `/git-workflow` — merge conflicts, cherry-pick, branch cleanup, bisect.
  - `/ci-watch` — recommended next step after the developer pushes.
- **Owner**: `pipeline-engineer`. **Category**: `developer-workflow`.
  **Effort**: `medium`.

## Future Improvements (deferred)

- Optional PreToolUse hook that hard-blocks `git commit` / `git push` from
  any agent context, as a belt-and-braces defence layered on top of this
  command's textual constraint.
- Optional PR description draft for `--first-push` (or split out as `/pr-draft`).
- Submodule-aware diff summary.
