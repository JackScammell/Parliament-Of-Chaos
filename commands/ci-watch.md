---
description: Poll CI pipelines for the current branch and surface status inside Claude
effort: low
---

# CI Watch

Poll CI status for the current branch/PR and surface it inside the session. Avoids the context-switch of flipping to a browser to check whether the build is green before `/cut-release`.

Supports GitHub Actions, GitLab CI, CircleCI, and generic webhook probes.

## Usage

```
/ci-watch [--ref <git-ref>] [--provider github|gitlab|circle|auto] [--watch] [--interval <duration>] [--timeout <duration>]
```

**Examples**:
```
/ci-watch                                # Snapshot current branch
/ci-watch --ref main                     # Snapshot for main
/ci-watch --watch                        # Poll until a terminal state
/ci-watch --watch --interval 30s --timeout 20m
```

## Options

- `--ref <git-ref>`: Branch, tag, or commit. Defaults to the current HEAD's remote-tracking branch.
- `--provider <name>`: Override auto-detection. Useful when multiple CI systems run on the same repo.
- `--watch`: Poll until all checks reach a terminal state (success / failure / cancelled).
- `--interval <duration>`: Polling cadence. Defaults to `30s`. Clamped to `[15s, 5m]`.
- `--timeout <duration>`: Abort after this long in watch mode. Defaults to `30m`.

## Provider detection

Looks for these signals in priority order:

1. `gh` CLI available and repo has `.github/workflows/` — use GitHub Actions
2. `glab` CLI available and `.gitlab-ci.yml` present — use GitLab CI
3. `.circleci/config.yml` present — use CircleCI (via `curl` against API)
4. Fall back to `--provider` flag; error if none detected

## Process

1. **Detect provider** — via flag or heuristic.
2. **Resolve ref** — defaults to `git rev-parse --abbrev-ref --symbolic-full-name @{u}` or the bare commit SHA.
3. **Fetch checks** — call the provider API (or CLI) for the ref's latest checks.
4. **Render** — one table per workflow/pipeline with per-job status.
5. **Watch mode** — re-fetch at the interval until all checks terminate or timeout elapses. Emit an update only when state changes (no noisy identical frames).
6. **Exit** — code 0 if all checks succeed, 1 if any fail, 2 on timeout in watch mode.

## Output

```
# CI Watch

**Ref**: main @ acc5249
**Provider**: github
**Last updated**: 2026-04-17T14:32:05Z

## Workflows
| Workflow         | Status   | Duration | URL |
|------------------|----------|----------|-----|
| CI / test        | success  | 3m12s    | https://github.com/.../runs/1234 |
| CI / lint        | success  | 42s      | https://github.com/.../runs/1234 |
| Release / tag    | queued   | —        | https://github.com/.../runs/1235 |

## Summary
2 / 3 complete. 1 in progress.
```

Watch-mode delta on state change:

```
[14:33:40Z] CI / release tag → success (1m28s)
[14:33:40Z] All checks terminal — exit 0.
```

## Integration

- Chain before `/cut-release` — `ci-watch --watch` followed by the release command prevents cutting a release against a broken build.
- `/parliament-loop 5m /ci-watch` surfaces persistent red builds in long sessions.
- `/parliament-metrics` can consume `--json` output for a build-health panel once CI ingestion is wired.

## Security

- Uses existing CLI auth (`gh auth status`, `glab auth status`). Does not store or transmit credentials.
- API tokens for non-CLI providers are read from environment variables only (`CIRCLE_TOKEN`, etc.), never from settings files.

## Notes

- Provider API rate limits apply. Default interval of `30s` stays well within GitHub's quota for a single repo.
- If no CI is detected, the command exits with a clear message rather than silently succeeding.
- Watch mode is safe to Ctrl-C; no background process is left behind.
- Pair with `/pre-commit-check` for local-first signal and `/ci-watch` for remote confirmation.
