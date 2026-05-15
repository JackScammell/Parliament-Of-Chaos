# Commit and Push Command

## Goal

Provide a guided `/commit-and-push` slash command that prepares a clean, well-formed
commit and a safe push, but **never executes** `git commit` or `git push` itself.
The command produces the exact, copy-paste-ready git commands that the developer
runs by hand. The hard constraint — Parliament must not perform the commit or
push on the user's behalf — is the central design rule.

The command must add value beyond raw `git status` / `git diff` by:
- Auditing the working tree (modified, staged, untracked, ignored) and surfacing risk.
- Running the project's existing pre-flight checks (`/pre-commit-check`, secret scan).
- Drafting a Conventional-Commit-shaped message from the diff, with rationale.
- Inspecting branch and remote state (ahead/behind, force-push risk, protected branches).
- Emitting a clearly-labelled "Run these commands yourself" block.

## Existing Capabilities Found

- `/git-workflow` — `commands/git-workflow.md`. Covers conflicts, cherry-pick,
  branch-cleanup, bisect. No commit/push surface. **2 callers** (manifest, list).
- `/pre-commit-check` — `commands/pre-commit-check.md`. Auto-detects and runs
  lint/format/typecheck/tests/secrets. Read-only verification. Will be invoked
  upstream of the new command.
- `/security-scan` — `commands/security-scan.md`. Secret + dependency scan.
  Read-only. Used as a fallback if `/pre-commit-check` is skipped.
- `/cut-release` — `commands/cut-release.md`. Bumps version, generates changelog,
  tags. Already has the principle of "suggest `git push`, do not execute it"
  (see step 6 of its Process section). Establishes precedent for this design.
- `/plugin-upgrade` — `commands/plugin-upgrade.md`. Stages files for the caller
  to commit; emits a next-step prompt with `git commit -am` and `git push`
  wording. Same precedent.
- `/release-notes-draft` — `commands/release-notes-draft.md`. `--apply` is the
  only mutating flag and requires explicit confirmation with diff preview.
  Same defensive posture.
- `/ci-watch` — `commands/ci-watch.md`. Post-push observability. Recommended
  as the natural follow-up after a developer-executed push.
- `pipeline-engineer` agent — `agents/pipeline-engineer.md`. Owner of all
  CI/CD-adjacent commands. Natural owner for `/commit-and-push`.

No command currently covers the "compose a commit message + verify push safety
+ surface the exact git commands for the developer to run" workflow. The
extend-don't-create rule is honoured by reusing `/pre-commit-check` and
`/security-scan` as upstream dependencies rather than duplicating their logic.

## Reuse Decision

**CREATE `/commit-and-push`** — distinct concern (guided pre-commit + commit-
message draft + push-safety audit) with no existing analogue. The command will:

- **Reuse** `/pre-commit-check` for verification (do not re-implement detection).
- **Reuse** `/security-scan` as a secondary check when `/pre-commit-check` is skipped.
- **Reference** `/git-workflow resolve-conflicts` if conflicts are detected.
- **Reference** `/ci-watch` as the suggested follow-up after the developer pushes.
- **Live in** `commands/commit-and-push.md`, owned by `pipeline-engineer`,
  category `developer-workflow`, effort `medium`.

The command is **never** allowed to call `git commit`, `git push`, `git tag`,
`git reset --hard`, or any other state-changing git command. This is enforced
in the command spec itself and re-stated in three places (frontmatter note,
top of process, output footer).

## Options Considered

### Option A — Pure advisory command (selected)
- Read-only inspection, runs `/pre-commit-check`, drafts message, prints
  copy-paste commands.
- Zero risk of accidental commit/push by the assistant.
- Developer pays the cost of one extra paste step.
- Mirrors the precedent set by `/cut-release` and `/plugin-upgrade`.

### Option B — Stage-only command
- Command runs `git add` for the developer, but stops there.
- Adds value (one less manual step) but introduces mutation.
- Contradicts the user's explicit constraint *"this has to be explicitly
  done by a developer"* — staging is part of the commit workflow and the
  user wants no automated movement of files toward a commit.
- Rejected.

### Option C — Confirmation-gated commit
- Command renders a plan, asks the user to confirm with a typed token, then
  runs the commit and push.
- Even with confirmation, the assistant is still the actor. The user's
  request is unambiguous: the **developer** must execute the operations.
- Rejected.

### Option D — Hook-driven enforcement
- Add a PreToolUse hook that blocks any `git commit` / `git push` invoked
  from the assistant side.
- Useful as a *belt-and-braces* defence, but orthogonal to providing the
  command. Logged as a Suggested Future Improvement, not part of this plan.

## Recommended Approach

Implement Option A. The command:

1. **Detects state** — branch, remote tracking, ahead/behind, dirty paths,
   untracked files, ignored-but-staged files, large binaries (>1MB), files
   matching common secret patterns by name (`.env`, `*.pem`, `id_rsa`).
2. **Runs pre-flight** — invokes `/pre-commit-check` (or `/security-scan` if
   `--skip-checks` is set, to keep at least the secret scan). If checks fail,
   the command stops and tells the developer to fix and re-run.
3. **Drafts a commit message** — Conventional Commits format. Subject
   summarising the diff, body explaining the why, optional footer for
   `BREAKING CHANGE:` or `Refs:`. Pulls hints from `git diff` and recent
   commit-message style on the branch.
4. **Audits push target** — flags pushes to `main`/`master`/protected
   branches, force-push patterns, mismatched upstream, detached HEAD.
   Refuses to draft a push command if branch state is dangerous; instead
   recommends `/git-workflow` or manual remediation.
5. **Emits a "RUN THESE YOURSELF" block** — a single fenced shell block
   containing the exact `git add`, `git commit -m`, `git push` (or
   `git push -u origin <branch>` for first push) commands. The block is
   labelled prominently, and the command's output ends with a banner
   stating that Parliament will not run them.

Output never streams a tool call that would execute these git mutations.
The agent driving the command (`pipeline-engineer`) is read-only on git
state — the command spec lists `git commit`, `git push`, `git tag`,
`git reset --hard`, `git rebase`, `git push --force` as explicitly
disallowed Bash invocations within the command's process section.

## Risks & Trade-offs

- **Risk: assistant ignores the constraint.** Mitigated by triple-statement
  (frontmatter note, process step, output banner) and a Suggested Future
  Improvement to add a PreToolUse hook (Option D) that hard-blocks
  `git commit`/`git push` from the assistant context.
- **Risk: commit-message draft is wrong / generic.** Mitigated by showing
  the draft in a clearly-marked editable block; the developer is expected
  to review and tweak before pasting.
- **Risk: developer pastes blindly.** Out of scope — Parliament cannot
  protect against a developer who runs commands without reading them.
  Output banner reminds the user to read the message and diff first.
- **Trade-off: extra friction vs. safety.** The user has explicitly chosen
  safety (developer in the loop). This is the right call for a plugin
  whose audience is its own author plus open-source contributors.
- **Trade-off: no commit-and-push automation for trivial changes.** Users
  who want one-shot automation can write their own shell alias outside
  Parliament. The plugin will not provide it.

## Suggested Task Breakdown

1. **Create `commands/commit-and-push.md`** — full spec with frontmatter
   (`description`, `effort: medium`), Usage, Options, Process, Output
   template, Notes, and a prominent "What this command will NOT do" section.
2. **Register in `commands/manifest.yaml`** — add entry under
   `developer-workflow` with `owner: pipeline-engineer`, `effort: medium`,
   `skill_surface: true`, `status: active`, and a `notes:` field stating
   the no-mutating-git-ops constraint.
3. **CHANGELOG entry** — append to the in-progress release section
   (or the next pending entry) noting the addition under `### Added`.
4. **Cross-references** — add a one-line "see also" pointer in
   `commands/git-workflow.md` and `commands/pre-commit-check.md` so
   developers discover the new command from adjacent surfaces.
5. **Sanity check** — run `/parliament-doctor` mentally (manifest entry
   present, file present, no skill registry drift).

## Open Questions

- Should the command also draft a **PR description** when pushing a feature
  branch for the first time? Deferred — out of scope for v1; can be added
  later or via a separate `/pr-draft` command.
- Should the command refuse on dirty submodules? Deferred — surface a
  warning, do not block.
- Should the command integrate with `/ci-watch` to print a one-liner that
  starts watching after the developer pushes? Yes, include as the final
  "Next" suggestion in the output template.
