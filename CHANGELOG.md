# Changelog

All notable changes to Parliament of Chaos will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.22.0] - 2026-07-24

Changelog-review adoption for Claude Code v2.1.174–v2.1.218. Leads with one interactive-UX correctness fix; the rest is bounded, additive documentation. No new commands, no new agents, no `settings.json` policy change.

### Fixed — interactive commands silently backgrounding (`context: fork` default flip)

- **All 12 `context: fork` commands** now set `background: false` in their frontmatter: `summon-council`, `parliament-review`, `debate-topic`, `ask-council`, `summon-specialist`, `summon-grumpy-reviewer`, `incident`, `implement-task-list`, `changelog-review`, `onboard-codebase`, `mutation-test`, `update-docs`. As of Claude Code **v2.1.217**, skills / slash commands with `context: fork` run in the **background by default**; without an opt-out, every Parliament orchestration command would silently background and break the round-by-round interactive review UX the plugin is built on. `background: false` restores foreground/interactive execution. The documented opt-out is a per-command frontmatter flag (there is no `settings.json` lever), consistent with the standing no-policy stance. Recorded dissent (maintainability-curmudgeon, refactor-ranger): 12 override lines track an upstream default that may flip again; the per-command flag is the only mechanism Claude Code provides.

### Added — subagent nesting & concurrency baseline (documentation)

- **`.claude/rules/agent-standards.md`** — new blockquote in *Background Execution* documenting the v2.1.198 → v2.1.218 move to background-by-default subagents, the per-session spawn cap (`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`, default 200, v2.1.212), the `context: fork` background flip (v2.1.217), and the v2.1.218 nested-spawn block (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, default disabled) plus concurrency cap (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, default 20). Supersedes the earlier "subagents nest 5 levels deep" characterisation. The nesting block is **inert for Parliament**: `governance.md` already restricts sub-agent spawning to the two top-level orchestrators, which run one level deep, well inside the default caps. No `CLAUDE_CODE_MAX_*` env vars are shipped in `settings.json`.

### Added — `/code-review` disambiguation (documentation)

- **`README.md`** — note in *Commands* distinguishing Parliament's directly-invoked review commands (`/summon-grumpy-reviewer`, `/parliament-review`) from Claude Code's separate built-in `/code-review` (now manual-only and dispatched to a background subagent).

## [1.21.0] - 2026-05-15

Changelog-review adoption for Claude Code v2.1.129–v2.1.142. Leads with one mandatory correctness fix; the remaining items are bounded, additive doc/telemetry changes. No new commands, no new agents, no `settings.json` policy change.

### Fixed — data-loss documentation correction (worktree branching baseline)

- **`.claude/rules/agent-standards.md`** — the "Worktree branching baseline" blockquote previously told contributors to *"treat v2.1.128 as the minimum safe version"* for workflows that spawn `isolation: worktree` specialists from a local feature branch with unpushed commits. **That guidance became unsafe on Claude Code ≥ v2.1.133**, where the worktree base is governed by the `worktree.baseRef` setting whose default is `fresh` (origin-based) — a worktree-isolated specialist spawned from a local feature branch with unpushed work branches from `origin` again and that work is silently not visible in the worktree. The note now states the safe configuration is **Claude Code ≥ v2.1.133 _with_ an explicit `worktree.baseRef: "head"` setting** (the version floor alone is insufficient), and clarifies that Parliament does **not** ship `worktree.baseRef` in `settings.json` (no-policy stance, reaffirmed v1.14.0) — it guides the user to set it, it does not prescribe it.

### Added — bounded telemetry enrichment

- **`src/hooks/_common.sh`**, **`src/hooks/log_event.sh`** — `activity.jsonl` events now carry two optional, additive fields: `effort_level` (read from the hook payload's `effort.level`, Claude Code v2.1.133+) and `agent_id` (present when the hook fires inside a subagent, v2.1.139+). Both are emitted only when their source value is present (`// empty` + conditional `jq` merge — same idiom as the existing `tool_use_id`/`duration_ms` fields); no new `case` branch, no new control flow on the hot path. Consumers MUST tolerate both fields being absent. Backward-compatible: telemetry under older Claude Code is byte-for-byte unchanged.

### Changed — documentation accuracy

- **`commands/parliament-metrics.md`** — `--by-effort` attribution now documents the hook-emitted `effort_level` field as a third additive source (after the OTel `effort` attribute and the status-line `effort.level`), so hook-only events (`SubagentStart`, `PostToolUse`) carry their own effort tier without needing a co-located OTel span.
- **`commands/parliament-loop.md`**, **`commands/parliament-monitor.md`** — document the Claude Code v2.1.140 fix: `/loop` no longer issues a redundant wakeup for a self-notifying background task, so a looped background monitor's cadence is its own completion signal, not `min(interval, self-notify)`. Guidance: size the loop interval as a staleness ceiling, not an exact tick.
- **`commands/cost-report.md`** — Notes block gains a one-line pointer to `claude plugin details` for the plugin's packaged-token projection (Claude Code v2.1.139+). Pointer only; `/cost-report` does not read or integrate that figure.
- **`.project-files/changelog-review/last-reviewed.json`** — advanced to reflect this review (last reviewed `v2.1.142`, `parliament_version` `1.21.0`).
- **`.claude-plugin/plugin.json`**, **`.claude-plugin/marketplace.json`** — version bumped to 1.21.0.

### Notes

- 143 of ~150 upstream changes in v2.1.129–v2.1.142 had no Parliament surface; the deliberation panel (6/6 APPROVE, 3 rounds) explicitly resisted scope creep. Scope is deliberately small.
- Deferred (not blocking this release): hook `args: string[]` exec-form migration (v2.1.139); hook `continueOnBlock` for PostToolUse (v2.1.139, pairs with the queued v1.20.0 PreToolUse git-commit guard); hooks-invoking-MCP-tools note carried over from the 2026-04-29 review.
- Rejected: shipping `worktree.baseRef` in `settings.json` (violates the no-policy stance); `skillOverrides` / `/goal` / `/scroll-speed` / agent-view / fast-mode Opus default (no Parliament surface — Parliament uses `model: inherit`).
- No README/`docs/usage.md` changes: neither file embeds a hardcoded plugin version anchor (version is surfaced via `/version`), and no command/agent count changed.

## [1.20.0] - 2026-05-07

### Added — `/commit-and-push` guided commit helper (developer-executed)

Adds a new advisory command that drafts the commit, runs pre-flight checks, audits push safety, and emits the exact git commands as a copy-paste block. **The command never executes `git commit`, `git push`, `git tag`, or any other state-changing git operation** — those are explicit developer actions, by design.

- **`/commit-and-push`** — read-only inspection of the working tree + staged/unstaged diff, drafted Conventional-Commit-style message (overridable via `--message`/`--scope`/`--type`), pre-flight delegation to `/pre-commit-check` (skippable via `--skip-checks`) and non-skippable secret scan via `/security-scan`, push-safety audit (protected branch detection, upstream divergence, first-push detection), and a "RUN THESE YOURSELF" output block with the copy-paste-ready `git add` / `git commit` / `git push` lines. Force pushes are never rendered. Pushes to `main` / `master` / `release/*` / `production/*` require explicit `--allow-protected`.
- **Triple-statement of the no-mutation rule** — frontmatter blockquote, top-of-process line, and output-block banner all repeat that the command does not execute git mutations. Refusal output examples cover detached-HEAD and mid-merge states.
- **`commands/manifest.yaml`** — registered under `developer-workflow` (`owner: pipeline-engineer`, `effort: medium`, `skill_surface: true`) with a `notes:` field encoding the no-mutating-git-ops constraint.
- **`commands/git-workflow.md`**, **`commands/pre-commit-check.md`** — cross-reference pointers to `/commit-and-push` added.

### Changed

- **`README.md`** — Developer Workflow table gains the `/commit-and-push` row; command count updated 64 → 66 (also resolves the prior 64/65 drift between the two count references).
- **`docs/usage.md`** — Quick-reference Developer-workflow table gains the `/commit-and-push` row; command count updated 65 → 66.
- **`commands/list-commands.md`** — Developer Workflow category updated (12 → 13 commands; `commit-and-push` inserted alphabetically after `pre-commit-check`).
- **`.claude-plugin/plugin.json`**, **`.claude-plugin/marketplace.json`** — version bumped to 1.20.0.

### Notes

- New command, no new agents, no settings.json changes, no hook changes.
- Hard constraint: the user explicitly required that committing and pushing remain developer-executed actions. The command is purely advisory — it draft, audits, and shows the commands; the developer runs them.
- Deliberate non-goals: no auto-staging, no confirmation-gated commit, no `Bash(git commit:*)` invocation. A PreToolUse hook to hard-block `git commit` / `git push` from any agent (belt-and-braces defence layered on top of the textual constraint) is logged as a future improvement in the command's "Future Improvements" section.

## [1.19.0] - 2026-05-07

### Added — `/ask-council` Q&A command

Adds a new entry-point command for **question-answering** against the Parliament. Sits beside `/summon-council` (artifact production) and `/debate-topic` (formal decision-making) and fills the gap for "I just want a synthesised expert answer."

- **`/ask-council <question>`** — auto-selects 2–5 relevant specialists, consults them in parallel, and synthesises a single cohesive answer that surfaces both consensus and disagreement. No fix loop, no artifact, no code edits, no voting. Single-pass.
- **Question classification (Step 1)** — before consulting any panel, the council classifies the question and redirects if it is really an artifact request (`/summon-council`), decision request (`/debate-topic`), critique request (`/parliament-review`), or single-agent request (`/summon-specialist`). Never silently defaults — asks the user when ambiguous. A council of one is not a council: questions whose only relevant domain is a single specialist are redirected.
- **Optional inventory (Step 2)** — runs the `Explore` inventory pass only when the question references project-specific code or behaviour. Purely conceptual questions skip the grep pass to avoid paying for an unhelpful one. Always stated in the output whether inventory was run.
- **Panel selection (Step 3)** — default size 3, expand to 4–5 only when the question genuinely spans that many domains, contract to 2 when no third domain is meaningfully relevant. Security-touching questions must include `security-knight`. Cross-cutting architecture questions should include `system-architect`. Grumpy reviewers, planning agents, and `deliberation-conductor` are excluded — they have their own driving commands.
- **Parallel consultation (Step 4)** — single round, no rebuttals. Each specialist answers from their lens with confidence (H/M/L), caveats, and file pointers where useful.
- **Synthesis (Step 5)** — leads with consensus, surfaces disagreements with attribution (no flattening genuine conflict into false consensus), applies the standard conflict priority (security > correctness > maintainability > performance > convenience) to break ties, and ends with a recommendation plus a suggested follow-up command if the answer implies action.
- **`agents/senior-council.md`** — extended with a third operating mode (`answer`) beside the existing `plan` and `implement` modes. Reuses the council's existing auto-selection logic; only the output shape and process loop differ. The `## Modes`, `## Responsibilities`, and `## Output` sections all updated to partition behaviour by mode.

### Changed

- **`commands/manifest.yaml`** — new `ask-council` entry under the `agent-invocation` category (`effort: medium`, `owner: senior-council`, `skill_surface: true`).
- **`agents/senior-council.md`** — `## Modes` adds the `answer` mode description; `## Responsibilities` partitions Discovery / Agent Selection / Review Management / Conflict Resolution / Synthesis by mode and clarifies that `answer` mode has no review loop and optional inventory; `## Output` now has separate sub-sections for `/summon-council` modes and `/ask-council` mode.
- **`README.md`**, **`docs/usage.md`** — `/ask-council` documented under the Agent Invocation section with usage, when-NOT-to-use guidance, response shape, and worked examples.
- **`.claude-plugin/plugin.json`**, **`.claude-plugin/marketplace.json`** — version bumped to 1.19.0.

### Notes

- New command, no new agents, no settings.json changes, no hook changes.
- Token-cost positioning: `/ask-council` ≈ 2–3× `/summon-specialist` (one synthesis pass at council `effort: high` plus 2–5 specialists at `effort: medium`), well under `/summon-council implement` (full grump iteration loop) and `/debate-topic` (multi-round convergence).
- The "redirect when ambiguous, never silently default" pattern from the v1.18.0 mode-disambiguation work in `/summon-council` is reused here for question-classification — same correctness > convenience priority applied at the entry point.
- Deliberate non-goals: no rebuttal rounds (use `/debate-topic`), no critique loop (use `/parliament-review`), no artifact written to disk (use `/summon-council plan`), no code edits (use `/summon-council implement`).

## [1.18.0] - 2026-05-06

### Added — Two-mode `/summon-council` with mandatory inventory step

Reshapes `/summon-council` into a two-mode orchestrator (`plan` / `implement`) and adds a mandatory codebase inventory step so the council never proposes a helper, module, or service the project already has.

- **`/summon-council plan <topic>`** — produces a written plan artifact at `.project-files/plans/<slug>.md` without editing code. Uses a planning-specialist subset (`system-architect`, `security-knight`, `data-warlock`, `api-keeper`, plus domain agents) and a plan-shaped reviewer subset (`grumpy-architecture-skeptic`, `grumpy-maintainability-curmudgeon`, `grumpy-security-nag`, `grumpy-performance-troll`, with `grumpy-budget-hawk` / `grumpy-privacy-paranoid` / `grumpy-testing-tyrant` added when the topic warrants). Plan artifact structure: Goal, Existing Capabilities Found, Reuse Decision, Options Considered, Recommended Approach, Risks & Trade-offs, Suggested Task Breakdown, Open Questions.
- **`/summon-council implement <topic>`** — preserves the prior full-9-grump iteration to ship working code, now with the inventory pass and extend-don't-create default applied.
- **Mode disambiguation** — when the mode cannot be inferred unambiguously from the topic, the council asks the user before doing any work. Pure review requests (no fix loop) are redirected to `/parliament-review`.
- **Inventory pass (Step 1, both modes)** — before any specialist work, the council dispatches the `Explore` agent to grep for related helpers, utilities, services, modules, and tests. Captures path + one-line summary + caller count for each plausible match. The inventory is shared with every specialist spawned. **Default rule: extend existing capabilities; only create new ones when the specialist provides a concrete reason** (incompatible API, separate concern, etc.). Reuse decision is documented in the output.
- **When-NOT-to-use table** — `/summon-council` documentation now points users at `/plan-project`, `/roadmap-add-item`, `/roadmap-item-scope`, `/implement-task-list`, `/parliament-review`, `/summon-grumpy-reviewer`, and `/summon-specialist` for cases that have purpose-built commands.

### Changed

- **`agents/senior-council.md`** — New `## Modes` section, updated `## Responsibilities` (Discovery step, mode-partitioned Agent Selection and Review Management, plan-artifact spec, synthesis includes inventory summary), updated `## Output` (now 6 fields including Mode and Inventory Summary).
- **`commands/summon-council.md`** — Description updated to "Orchestrate specialists and grumpy reviewers for ad-hoc planning or implementation". New "Mode selection", "When NOT to use", "Step 1 — Inventory", and mode-specific Process subsections. Output section split per mode.
- **`commands/manifest.yaml`** — `summon-council` entry now carries a `notes:` field describing the two-mode behaviour, plan-artifact location, inventory pass, and review-redirect.
- **`.claude-plugin/plugin.json`**, **`.claude-plugin/marketplace.json`** — version bumped to 1.18.0.
- **`README.md`**, **`docs/usage.md`** — `/summon-council` entries updated to describe the two-mode behaviour and inventory pass.

### Notes

- Documentation + behaviour-spec release. No new commands, no new agents, no settings.json changes, no hook changes.
- Inventory pass uses the existing `Explore` agent (read-only, fast, does not pollute the main context window). No new tooling required.
- The `.project-files/plans/` directory is created lazily by `senior-council` on first plan-mode invocation. Plan files use kebab-case slugs derived from the topic.
- Plan-mode reviewer subset is a deliberate subset of the full 9-grump panel — accessibility, code-quality, standards, documentation, and testing reviews are not meaningful before any code exists. They re-enter via `/implement-task-list` or `/summon-council implement` when the plan becomes code.
- Mode-disambiguation behaviour is "ask, never silently default" — this is the correctness > convenience priority applied at the entry point.

## [1.17.0] - 2026-05-05

### Added — Claude Code Feature Adoption v2.1.124–v2.1.128 (Priority 2)

Implements the two Priority 2 items from the 2026-05-05 `/changelog-review` deliberation. Closes the fan-out reliability and `claude project purge` documentation gaps queued from the Priority 1 release earlier today (v1.16.0).

- **Fan-out reliability note (v2.1.128)** — New `## Notes` sections in `commands/parliament-review.md` and `commands/summon-council.md` documenting that parallel fan-out to specialists and reviewers is more reliable on Claude Code v2.1.128+, where a failing sibling tool call no longer cancels its parallel peers. One bullet per file, version-tagged for future correlation.
- **`claude project purge` interaction note (v2.1.126)** — New blockquote callout in the `## Plugin State Storage` section of `.claude/rules/agent-standards.md` documenting that `claude project purge` clears Claude-managed plugin state (`${CLAUDE_PLUGIN_DATA}/chaos-parliament-of-chaos/` — telemetry, disposable) but does not touch `.project-files/` (user-curated planning artifacts, lives in the project tree outside Claude-managed state). Wording explicitly attributes preservation to `purge`'s scope rather than a Parliament-side guarantee — caught by the architecture-skeptic in Round 1 review as an overclaim that would have planted a false sense of security if `purge` scope ever expands.

### Changed

- **`commands/parliament-review.md`** — New `## Notes` section appended.
- **`commands/summon-council.md`** — New `## Notes` section appended.
- **`.claude/rules/agent-standards.md`** — New `claude project purge` interaction blockquote in the Plugin State Storage section.

### Notes

- Documentation-only release. No new commands, agents, hooks, or settings.json changes. Three existing surfaces extended with version-tagged notes.
- Closes the deferred queue from the 2026-05-05 `/changelog-review`. The two deferred-docs items from the 2026-04-29 review (hooks invoking MCP tools, agent-typed hooks bug-fix) remain queued — status unchanged.
- The Item 4 wording is intentionally cautious: "preservation of `.project-files/` is a property of `purge`'s scope, not a Parliament-side guarantee." If a future Claude Code release expands `purge` scope, this callout will need revision — flag for re-check on the next `/changelog-review` cycle.

## [1.16.0] - 2026-05-05

### Added — Claude Code Feature Adoption v2.1.124–v2.1.128 (Priority 1)

Implements the two Priority 1 items from the 2026-05-05 `/changelog-review` deliberation (5/5 APPROVE, fast mode). Closes the trigger-attribution and worktree-isolation-baseline gaps opened by upstream Claude Code v2.1.126 and v2.1.128.

- **`/parliament-metrics --by-trigger` partition (v2.1.126)** — Cost and latency panels can now be split by invocation trigger (`user-slash` / `claude-proactive` / `nested-skill`). Attribution sources, in priority order: `invocation_trigger` attribute on `claude_code.skill_activated` OTel events (authoritative, v2.1.126+); heuristic fallback derived from event ordering on older Claude Code versions (best-effort — explicitly documented as non-authoritative, with named failure modes for interleaved or parallel activations). Rows that resolve to neither source fall under `unknown` and are reported separately so partial historical data does not skew the breakdown. Composable with `--by-effort` — passing both flags produces a two-dimensional split (effort tier × trigger).
- **`agent-standards.md` worktree branching baseline (v2.1.128)** — New blockquote callout in the Isolation section documenting the v2.1.128 silent-data-loss fix: on Claude Code < v2.1.128, `EnterWorktree` branched from the remote tracking head, so unpushed local commits on a feature branch could be silently dropped when an `isolation: worktree` specialist was spawned. v2.1.128 fixes this by branching from local HEAD. Recommends v2.1.128 as the minimum safe version for any workflow that spawns worktree-isolated specialists from a local feature branch with unpushed work — scoped to the actual risk surface, not a blanket upgrade demand.

### Changed

- **`commands/parliament-metrics.md`** — New `--by-trigger` flag, "Trigger attribution (Claude Code v2.1.126+)" section mirroring the existing "Effort attribution" section, updated Usage / Examples / Options / Process step 2 to cover the new flag and its composition with `--by-effort`.
- **`.claude/rules/agent-standards.md`** — New v2.1.128 worktree branching baseline blockquote in the Isolation section, matching the v2.1.101 MCP-inheritance callout style.

### Notes

- Documentation-only release. No new commands, agents, hooks, or settings.json changes. Two existing surfaces extended.
- Priority 2 items from the 2026-05-05 review (one-line reliability note in `parliament-review.md` / `summon-council.md`, and the `claude project purge` interaction note in `agent-standards.md`) are queued for v1.17.0 per the deliberation.
- The `--by-trigger` heuristic fallback for pre-v2.1.126 telemetry is intentionally documented as best-effort with named failure modes rather than presented as authoritative — users who need authoritative trigger attribution must run on Claude Code v2.1.126+ for the windows they care about.

## [1.15.0] - 2026-04-29

### Added — Claude Code Feature Adoption v2.1.113–v2.1.123 (Priority 2)

Implements the two Priority 2 items deferred from the v1.14.0 deliberation (5/5 APPROVE, fast mode). Closes the effort-attribution and orphan-plugin-cleanup gaps that the v1.14.0 release explicitly queued for v1.15.0.

- **`${CLAUDE_EFFORT}` adoption in cost-aware skills (v2.1.120)** — `/cost-report estimate` now resolves the effort baseline through a four-step priority chain: explicit `--effort` flag → target command's `effort:` frontmatter → `${CLAUDE_EFFORT}` env var → `medium` fallback. The chosen tier and its source are surfaced in the estimate output (`**Effort baseline**: high (source: ${CLAUDE_EFFORT})`). Effort multipliers (low 0.55×, medium 1.00×, high 1.55×, xhigh 2.10×) apply to the historical p50/p95 token bounds. Multipliers are overridable via `${CLAUDE_PLUGIN_DATA}/cost-rates.json` under `effort_multipliers`. Removes the need for parallel `--mode` plumbing on cost-projection skills.
- **`/parliament-metrics --by-effort` partition (v2.1.117 + v2.1.119 + v2.1.120)** — Cost and latency panels can now be split by effort tier. Attribution sources, in priority order: OTel `effort` attribute on `cost.usage` / `token.usage` / `api_request` / `api_error` spans (v2.1.117), status-line `effort.level` field (v2.1.119), `${CLAUDE_EFFORT}` env at emit time (v2.1.120). Older events without effort data fall under `unknown` and are reported separately so partial historical data does not skew the breakdown.
- **`claude plugin prune` integration in `/env-doctor` (v2.1.121)** — New `--check-orphans` flag lists auto-installed plugin dependencies that no longer have a dependent (calls `claude plugin list --orphaned`). New `--prune` flag invokes `claude plugin prune` after explicit confirmation. Both flags are no-ops with a one-line note on Claude Code < v2.1.121. `--strict` never auto-invokes pruning. `/plugin-upgrade` post-conditions now suggest running `/env-doctor --check-orphans` after a successful version bump.

### Changed

- **`commands/cost-report.md`** — New "Effort awareness" section, `--effort` flag on `estimate`, multiplier table, updated process and example output.
- **`commands/parliament-metrics.md`** — New `--by-effort` flag, "Effort attribution" section, updated process step 2.
- **`commands/env-doctor.md`** — New `--check-orphans` and `--prune` flags, "Plugin orphans" section under External tools, updated process steps.
- **`commands/plugin-upgrade.md`** — Notes reference the new `/env-doctor --check-orphans` post-upgrade suggestion.
- **`.claude/rules/agent-standards.md`** — New "Reading session effort at runtime (`${CLAUDE_EFFORT}`)" subsection clarifying the relationship between `${CLAUDE_EFFORT}` (per-turn reasoning effort) and the `--mode` flag (deliberation depth) — they are orthogonal and both retained.

### Notes

- No new commands or agents this release. Three existing commands extended with effort-awareness or orphan-plugin handling, one rule file gains a subsection.
- The deferred-docs items from the 2026-04-29 review (hooks invoking MCP tools, agent-typed hooks bug-fix) remain documentation-only and are tracked for inclusion in the next agent-standards refresh — no code change required.
- Multipliers in `/cost-report` are heuristic. Telemetry collected after `--by-effort` ships will refine them; the `effort_multipliers` block in `cost-rates.json` is the override surface.

## [1.14.0] - 2026-04-29

### Added — Claude Code Feature Adoption v2.1.113–v2.1.123 (Priority 1)

Implements the four Priority 1 items from the 2026-04-29 `/changelog-review` deliberation (5/5 APPROVE, fast mode). Closes the four telemetry, permissions, resilience, and release-tagging gaps opened by upstream Claude Code v2.1.113 through v2.1.123.

- **`PostToolUse` / `PostToolUseFailure` telemetry** — `src/hooks/log_event.sh` now handles both events and captures the `duration_ms` field added in Claude Code v2.1.119, plus `tool_use_id` and `tool_name`. Emitted as `tool_use` / `tool_use_failure` event types in `activity.jsonl`. settings.json wires both events through to `log_event.sh`. Schema is additive — older log entries continue to parse.
- **`/parliament-metrics` latency panel — `duration_ms` source** — Now prefers the captured `duration_ms` field over event-pair inference. New `--strict-duration` flag drops inferred rows for windows where the hook was definitely wired. The panel marks the source per-row (`duration_ms` vs `inferred*`) so readers can see fidelity at a glance.
- **Bash permission-rule audit (v2.1.113)** — Verified that Parliament's `settings.json` ships **no** `permissions.allow` or `permissions.deny` rules, so the v2.1.113 narrowing of `Bash(find:*)`, wrapper-bypass closure (`env`/`sudo`/`watch`/`ionice`/`setsid`), and macOS `/private/...` dangerous-removal targets requires no Parliament fix. Documented the verdict and the policy ("plugin only configures hooks; permission rules are user concern") in a new **Permissions** section of `.claude/rules/agent-standards.md`.
- **`/env-doctor` — settings.json malformed-block resilience** — Aligned with Claude Code v2.1.121 (invalid legacy enum) and v2.1.122 (malformed `hooks` block) behaviour: a single broken hook entry now surfaces as a targeted warning naming the event and array index, never as a blanket "settings.json is invalid" fatal. Other hooks continue to be validated.
- **`/plugin-upgrade --tag` — upstream-validated release tags** — New opt-in `--tag` / `--no-tag` switch invokes `claude plugin tag <next-version>` (Claude Code v2.1.118+) after the version-sync phase. The upstream validator confirms the tag matches `.claude-plugin/plugin.json` before writing. Defaults off until proven across a couple of releases. Ignored with a warning on older Claude Code versions.

### Changed

- **`.claude/rules/agent-standards.md`** — New **Permissions** section documenting the Bash permission-rule audit verdict and the no-permission-rules-by-policy stance.
- **`.claude/projects/.../memory/feedback_release_process.md`** (user memory) — Now points at `/plugin-upgrade --tag` as the preferred path.
- **`commands/parliament-metrics.md`** — `--strict-duration` flag and source-attribution column in the latency panel.
- **`commands/env-doctor.md`** — New "settings.json resilience" subsection and example targeted-warning output.
- **`commands/plugin-upgrade.md`** — `--tag` / `--no-tag` documented in usage, options, process step 7, and post-conditions.
- **`docs/DEVELOPMENT.md`** — Plugin-manifest version reference bumped to 1.14.0.

### Notes

- No new commands or agents this release. Five existing surfaces extended, one rule file gains a section, one user-memory feedback file updated.
- Priority 2 (`${CLAUDE_EFFORT}` adoption, `claude plugin prune` integration) and the deferred-docs items remain queued for v1.15.0 per the deliberation.
- Item 2 (Bash audit) is documented as "no change required". The audit itself is the deliverable; the absence of changes is the result.

## [1.13.0] - 2026-04-17

### Added — Tier 4: Ops & Lifecycle (from toolset-gaps-debate.md)

Final tier of the toolset-gaps plan. Tools the three user-memory footguns (release sync, hook location, session crash) and the release / CI / env lifecycle. Completes the 10/10-APPROVE proposal from debate session `fc777472`.

- **`/session-snapshot`** — Checkpoint/resume primitive. `create`, `list`, `resume`, `show`, `prune` sub-commands. Captures conversation transcript, active council/debate state, open task lists, environment, and RNG seed. Atomic writes, schema v1. Primary consumer: `/debate-replay` (Tier 2) — this closes the dependency flagged in v1.11.0.
- **`/docs-audit`** — Symmetric opposite of `/onboard-codebase`. Detects stale references, fabricated claims, drift without breakage, and completeness gaps. Delegates to `doc-bard` for judgement and `grumpy-documentation-pedant` for verdict.
- **`/settings-audit`** — Merged the four original proposals (`/settings-diff`, `/permission-audit`, `/secrets-rotate`, `/feature-flag-list`) into one. Five pillars: permissions, secrets, feature flags, hooks, scope diff. `--fix` proposes diffs without applying.
- **`/env-doctor`** — Runtime environment validator. Checks plugin data directory, hook script locations/permissions/shebangs, external tool availability, and directory-separation conventions. Addresses `feedback_hooks_location.md` by making hook-location drift loud. `--strict` for CI.
- **`/fast-track`** — Replacement for the rejected `/hotfix`. Minimum-review-floor bypass that runs `grumpy-security-nag` and `grumpy-code-reviewer` (plus `grumpy-privacy-paranoid` if personal data detected) and NEVER below. Every use is logged as review debt with a mandatory 7-day follow-up `/parliament-review`. Hard limits on auth/migration changes and large diffs.
- **`/release-notes-draft`** — Drafts CHANGELOG entries from git log and merged PRs since the last tag. Classifies commits via conventional-commit heuristics, deduplicates by PR, cross-checks new commands against `commands/manifest.yaml`. `--apply` inserts at top of CHANGELOG with diff preview.
- **`/ci-watch`** — Polls CI for the current branch/PR. Supports GitHub Actions, GitLab CI, and CircleCI via `gh`/`glab`/API. `--watch` mode polls until terminal. Emits state-change deltas rather than repeated snapshots.
- **`/plugin-upgrade`** — Version-sync helper encoding the `feedback_release_process.md` rule. Bumps `plugin.json`, both slots in `marketplace.json`, and inserts a CHANGELOG stub in one atomic operation. Pre-flight drift check, post-condition verification. `--check` for dry-run.

### Changed

- **`commands/manifest.yaml`** — New `lifecycle` category; 8 new command entries. Tier 4 is the largest of the four tiers.

### Notes — Deferred / Skipped

- **`/i18n-audit`** was originally scheduled for Tier 4 item 4.9 but was shipped in Tier 1 (v1.10.0) alongside the `grumpy-i18n-nitpicker` retention decision. No separate Tier 4 item.
- **`/hotfix`** remains rejected per governance (security > convenience). `/fast-track` is the safety-floor replacement.
- **`/bisect`** and **`/sbom-generate`** remain deferred from the original debate — out of scope for this sweep.

### Toolset-gaps deliberation complete

All four tiers from `toolset-gaps-debate.md` are now shipped. Tier 1 (v1.10.0) was the blocking gate; Tiers 2 (v1.11.0), 3 (v1.12.0), and 4 (v1.13.0) could then land in parallel. Total: 18 new commands plus `commands/manifest.yaml` as the source-of-truth registry. Parliament now has: hygiene tooling, a feedback loop, observability and cost controls, and lifecycle automation for the known footguns.

## [1.12.0] - 2026-04-17

### Added — Tier 3: Observability & Cost (from toolset-gaps-debate.md)

Depends on Tier 1. Turns write-only telemetry into a queryable, budget-aware signal. Closes the observability gap identified by `observability-oracle` and the cost gap flagged by `grumpy-budget-hawk`.

- **`/telemetry-query`** — Ad-hoc read path over `activity.jsonl` (including rotated `.old`) and the plugin data directory. Filters by event, agent, time window, and whitelisted `--where` expressions. Supports `--group-by` aggregations and `--json` output for downstream consumers. Falls back to `.project-files/.telemetry/` on installations without `CLAUDE_PLUGIN_DATA`.
- **`/parliament-metrics`** — Dashboard over telemetry: cost panel (token attribution + spend), latency panel (p50/p95/max per command), SLO panel (background-monitor health), trend panel (rolling deltas). Consumes `/telemetry-query --json` as data source.
- **`/cost-report`** — Dry-run estimates, post-flight retrospectives, and soft-cap budget management. `estimate <command>` walks the target command's Process block to project token usage with historical p50/p95 bounds. Expensive-command registry warns on `/summon-council`, `/parliament-review`, `/debate-topic --mode deep`, `/implement-task-list`, and `/changelog-review --full`. Soft caps only — hard stops were rejected in the debate because they would violate governance (convenience cannot override security or correctness).

### Changed

- **`commands/manifest.yaml`** — New `observability` category; 3 new command entries.

### Notes

- Cost figures require a `${CLAUDE_PLUGIN_DATA}/cost-rates.json` price table; if absent, token usage is shown but USD is rendered as `n/a`.
- `/parliament-webhook` can subscribe to `/parliament-metrics --json` on a schedule for external dashboards.

## [1.11.0] - 2026-04-17

### Added — Tier 2: Learning Loop (from toolset-gaps-debate.md)

Depends on Tier 1. Gives Parliament a feedback loop so past decisions can be revisited, replayed, and measured.

- **`/adr-new`** — Scaffold new Architectural Decision Records under `.project-files/adrs/`. Supports `--from-session` to import context from a prior debate, and `--supersedes` to chain replacements.
- **`/adr-supersede`** — Mark an ADR superseded and forward-link it to its replacement. Never deletes — preserves the historical record.
- **`/decision-review`** — Re-evaluate a prior ADR, debate, or council ruling when context shifts. Produces a verdict of `hold`, `amend`, or `supersede` via a delegated debate.
- **`/debate-replay`** — Deterministic replay of a past debate from a session snapshot. Regression-tests the deliberation engine. `--strict` mode for release gating. Depends on `/session-snapshot` landing in Tier 4.
- **`/agent-usage-stats`** — Per-agent frequency, duration, token cost, and approval-rate statistics aggregated from `activity.jsonl`. Identifies workhorses and retirement candidates.

### Changed

- **`commands/manifest.yaml`** — New `decisions` category; 5 new command entries; driverless-agent tracking extended.

### Notes

- `/debate-replay` will report a clear error about missing snapshot infrastructure until Tier 4 ships. The command is registered now so the surface area is visible, consistent with the "no orphans" rule established in Tier 1.
- ADRs live in `.project-files/adrs/` (user-owned content), not under `${CLAUDE_PLUGIN_DATA}/` (plugin state).

## [1.10.0] - 2026-04-17

### Added — Tier 1: Toolset Hygiene (from toolset-gaps-debate.md)

Tier 1 is the blocking gate from the toolset-gaps deliberation (10/10 APPROVE, round-3 convergence 0.88). Reconciles existing surface before any new feature work lands.

- **`commands/manifest.yaml`** — Declarative registry of every slash command. Tracks name, status (active/deprecated/experimental/orphaned), owner agent, `skill_surface` flag, effort, and category. Source of truth for `/list-commands`, `/version`, and the new `/parliament-doctor`.
- **`/parliament-doctor`** — Reconciles the manifest against `commands/*.md` and the registered skill surface. Reports orphans (file with no manifest entry), ghosts (manifest entry with no file), hidden skills, leaked skills, effort mismatches, and driverless agents. `--strict` mode for release gating; `--fix-manifest` proposes diffs before applying.
- **`/i18n-audit`** — Driver command for `grumpy-i18n-nitpicker` (previously a driverless agent). Scans user-facing strings, verifies framework coverage, checks pluralisation and locale-aware formatting, then delegates to the reviewer for verdict.

### Changed — Orphan Triage (12 commands reconciled)

The following commands existed as markdown files but were not exposed as `/chaos:` skills. Tier 1 triage decided to **expose** all of them (none are retired). They are now registered in `commands/manifest.yaml` with `status: active` and `skill_surface: true`:

- `analyse-queries`, `coverage-audit`, `cut-release`, `generate-tests`, `git-workflow`, `incident`, `infra-review`, `mutation-test`, `retro`, `scaffold`, `test-health`, `track-debt`

### Changed — list-commands

- **`/list-commands`** now reads `commands/manifest.yaml` as the source of truth for command grouping, with a fallback to scanning `commands/*.md` for older installations. Three new categories added: **Hygiene**, **Quality**, **Release**.

### Changed — grumpy-i18n-nitpicker decision

- Retained rather than retired. Tier 1 decision was resolved by adding `/i18n-audit` as its driver command. Manifest records the agent-driver pairing under `agents_requiring_driver` for future `/parliament-doctor` checks.

### Deferred — Tier 2, 3, 4

Subsequent tiers from the toolset-gaps plan land in v1.11.0 (Learning Loop), v1.12.0 (Observability & Cost), and v1.13.0 (Ops & Lifecycle). Tier 1 is the gate — no Tier 2+ work ships until drift is at zero.

## [1.9.0] - 2026-04-17

### Added

#### Claude Code Feature Adoption (v2.1.89–v2.1.112)

##### New Hooks
- **PermissionDenied**: Fires when auto mode denies a Parliament agent's tool call — logs denied tool name and reason for diagnosing silent agent failures in automated workflows. Wired to `notify_teams.sh` for optional team notification.
- **TaskCreated**: Fires when a new task is created — completes the task lifecycle logging alongside the existing `TaskCompleted` hook.

##### Hook Consolidation
- **log_event.sh**: Unified event logging dispatcher replaces four individual scripts (`log_agent_activity.sh`, `handle_post_compact.sh`, `handle_instructions_loaded.sh`, `handle_stop_failure.sh`). Uses a `case` statement to extract event-specific fields — adding a new logged event is now a one-line case addition.
- **Log rotation**: `_common.sh` now rotates `activity.jsonl` to `activity.jsonl.old` when it exceeds 10MB, preventing unbounded log growth.

##### Plugin Manifest
- **`keep-coding-instructions: true`** in `plugin.json` — ensures Parliament's `.claude/rules/*.md` (agent-standards, governance, output-standards) stay resident across context compactions, pairing with the existing `InstructionsLoaded` hook. Prevents reviewers from losing the governance priority hierarchy mid-deliberation.
- **`dependencies: []`** field in `plugin.json` — declares zero external-plugin dependencies. v2.1.110 makes this install-enforced; an explicit empty array signals intent and future-proofs additions.

##### Standards Documentation
- **`xhigh` effort tier** documented in `agent-standards.md` — Opus 4.7's new tier (Claude Code v2.1.111) between `high` and `max` is listed as *Reserved* in the effort-tiers table. No agents adopt it yet; reserved for future deliberation-conductor deep-mode runs pending benchmark evidence.
- **Subagent MCP inheritance** documented in `agent-standards.md` — v2.1.101 made MCP tools flow automatically from parent sessions to spawned subagents. Note added to the Tool Restrictions section so contributors don't re-declare MCP servers per agent.
- **Default `effort: high`** informational note in `agent-standards.md` — Claude Code v2.1.94 raised the global default from `medium` to `high`. Parliament sets `effort` explicitly per agent so behaviour is unchanged, but the note flags the upstream default for new contributors.

### Changed
- **_common.sh**: Added `HOOK_LOG_DIR`, `HOOK_LOG_FILE`, automatic `mkdir -p`, and 10MB log rotation guard.
- **notify_teams.sh**: Added `PermissionDenied` event case, hardened `.env` sourcing with ownership/permission checks, replaced wildcard `*)` fallback with safe `exit 0` to reject unknown events.
- **settings.json**: All logging hooks now point to unified `log_event.sh`; added `PermissionDenied` and `TaskCreated` hook configurations.
- **Hook count**: 9 hook event handlers (up from 7), served by 3 scripts (down from 5).
- **plugin.json / marketplace.json**: Version bumped to 1.9.0 across both files.

### Removed
- `log_agent_activity.sh`, `handle_post_compact.sh`, `handle_instructions_loaded.sh`, `handle_stop_failure.sh` — replaced by `log_event.sh`.

### Deferred (Priority 2 — tracked for v1.10.0)
- `PreCompact` hook `block` decision (v2.1.105) — needs scope-weaver design pass with hard attempt counter to avoid infinite-block footgun.
- Plugin `monitors` manifest key (v2.1.105) — prototype candidate for always-on log tailing / roadmap drift alerts; waiting one release for community examples.
- Skill-tool slash-command references in specialist prompts (v2.1.108) — consistency audit across test-prophet, backend-goblin, pipeline-engineer.

## [1.8.0] - 2026-03-31

### Added

#### New Agents (33 total, up from 30)

##### Grumpy Reviewers (12 total, up from 9)
- **grumpy-privacy-paranoid**: PII exposure, GDPR/CCPA compliance, consent handling, data retention — fills the gap between security (auth/vulns) and privacy (data governance)
- **grumpy-i18n-nitpicker**: Hardcoded strings, missing translations, broken pluralisation, locale-aware formatting — for any project with multi-language support
- **grumpy-budget-hawk**: Cloud cost impact of PRs, over-provisioned resources, unbounded queries, missing auto-scaling bounds — performance-troll covers speed, this covers spend

#### New Commands (46 total, up from 34)

##### Phase 1 — High frequency, high impact (4 new)
- `/cut-release`: Automate version bumping, changelog generation, git tagging, and release notes across all version-bearing files
- `/scaffold`: Generate convention-compliant boilerplate by reading existing project patterns — models, endpoints, services, tests, full features
- `/generate-tests`: Write tests for existing code following project conventions — delegates to test-prophet with worktree isolation
- `/track-debt`: Scan TODO/FIXME/HACK, complexity hotspots, coverage gaps — maintain a living debt ledger with trend tracking

##### Phase 2 — Strong value, moderate effort (4 new)
- `/incident`: Structured incident triage, hotfix coordination, runbook generation, and postmortem templates
- `/analyse-queries`: SQL/ORM analysis for missing indexes, N+1 patterns, full table scans, with specific CREATE INDEX recommendations
- `/git-workflow`: Complex git operations — merge conflict resolution with context, cherry-pick strategy, branch cleanup, bisect-based debugging
- `/coverage-audit`: Risk-prioritised test coverage analysis — classifies uncovered code by risk, chains into `/generate-tests`

##### Phase 3 — Rounding out the team (4 new)
- `/retro`: Structured retrospective from git history — identifies hotspots, revert frequency, churn patterns, produces action items
- `/infra-review`: Dockerfile, Kubernetes manifest, docker-compose, and CI/CD config best-practice audit
- `/mutation-test`: Evaluate test quality by introducing code mutations and checking if tests catch them — runs in worktree isolation
- `/test-health`: Detect flaky tests, stale assertions, non-deterministic patterns, and test coupling issues

### Changed
- **senior-council**: Added Task() references for 3 new grumpy reviewers (privacy-paranoid, i18n-nitpicker, budget-hawk)
- **deliberation-conductor**: Added Task() references for 3 new grumpy reviewers
- **Agent count**: 33 agents (up from 30) — 3 new grumpy reviewers
- **Command count**: 46 commands (up from 34) — 12 new commands across 3 phases
- **Grumpy reviewer count**: 12 (up from 9) — now covers privacy, i18n, and cloud cost

## [1.7.0] - 2026-03-31

### Added

#### Claude Code Feature Adoption (v2.1.45–v2.1.88)

##### initialPrompt for Planning Agents
- **project-oracle**: Auto-starts the project planning interview on spawn
- **scope-weaver**: Auto-starts the roadmap scoping workflow on spawn
- Deliberation-conductor excluded — orchestrators should react to input, not auto-fire

##### Effort Frontmatter on All 34 Commands
- **High effort** (4): summon-council, debate-topic, parliament-review, implement-task-list
- **Medium effort** (17): plan-project, changelog-review, security-scan, summon-specialist, and 13 others
- **Low effort** (13): list-agents, version, readme, format-code, run-tests, and 8 others

##### ${CLAUDE_PLUGIN_DATA} for Plugin State
- All 5 hook scripts now write logs to `${CLAUDE_PLUGIN_DATA}` when available
- Falls back to `.project-files/.telemetry/` (isolated from user planning data)
- Changelog review state migrated to `${CLAUDE_PLUGIN_DATA}/changelog-review/`

#### Shared Hook Helper
- New `src/hooks/_common.sh` — shared payload parsing, path validation, and data directory resolution
- All 5 logging hooks refactored to source this helper (eliminates duplicated boilerplate)

#### Agent Standards Updates
- `initialPrompt` guidelines — only for agents that drive conversation without needing input first
- Command effort tiers with rationale table and specific examples
- Storage contract documented — `CLAUDE_PLUGIN_DATA` for telemetry, `.project-files/` for user data

### Changed
- **Hook scripts**: Refactored from ~30 lines each to ~15 lines by extracting shared `_common.sh`
- **Telemetry isolation**: Fallback path changed from `.project-files/` root to `.project-files/.telemetry/`
- **notify_teams.sh**: Added comment clarifying it does not use `CLAUDE_PLUGIN_DATA` (webhook-only, no logs)
- **README.md**: Updated activity logging path reference
- **.gitignore**: Added `.project-files/.telemetry/`

## [1.6.0] - 2026-03-18

### Breaking Changes

- **Plugin renamed**: `parliament-of-chaos` → `chaos`. All slash commands now use the `chaos:` prefix (e.g. `/chaos:summon-council` instead of `/parliament-of-chaos:summon-council`). Existing users must reinstall:
  ```
  claude plugin marketplace add https://github.com/JackScammell/Parliament-Of-Chaos.git
  claude plugin install chaos@chaos
  ```

### Added

#### New Commands (34 total, up from 31)

##### Discovery Commands (3 new)
- `/version`: Display the current Parliament of Chaos version, plugin name, agent/command counts, and repository link
- `/readme`: Display the full README directly in the session for quick reference
- `/changelog`: Display the full version history and changelog

### Changed
- **Plugin name**: Renamed from `parliament-of-chaos` to `chaos` for shorter slash command prefixes
- **Command count**: 34 commands (up from 31) — added 3 discovery commands
- **Install/update commands**: Now use `chaos@chaos` format
- **All documentation**: Updated to reflect new plugin name and commands

## [1.5.0] - 2026-03-18

### Added

#### New Commands (30 total, up from 21)

##### Developer Workflow Commands (9 new)
- `/pre-commit-check`: Auto-detect CI pipeline, linters, formatters, type checkers, and test suites — run them all locally before committing. Includes secret scanning. Supports `--fix` for auto-remediation and `--skip` to bypass specific steps
- `/format-code`: Detect the project's formatter (Prettier, Black, gofmt, rustfmt, etc.) and run on changed files. Supports `--all`, `--check`, and explicit file targets. Offers setup if no formatter configured
- `/lint-fix`: Detect linter(s) (ESLint, Ruff, RuboCop, golangci-lint, etc.) and run with auto-fix on changed files. Handles multiple linters per project. Parses remaining errors with explanations
- `/run-tests`: Detect test framework and run suite with `--changed` (only tests affected by git changes via import graph analysis), `--coverage` (highlight untested critical paths), and `--explain` (diagnose failures and suggest fixes)
- `/security-scan`: Unified security check — dependency vulnerability audit, secret/credential detection, and OWASP Top 10 pattern scanning. Supports `--secrets`, `--deps`, `--patterns` focused modes
- `/clean-imports`: Remove unused imports, sort/organise imports per project conventions, convert to type imports (TypeScript). Works across JS/TS, Python, Go, Java, Rust
- `/update-dependencies`: Interactive dependency update — show outdated packages, review changelogs for breaking changes, update incrementally with test runs between each, auto-rollback on failure. Supports `--patch`, `--minor`, `--major`, `--security` filters
- `/dead-code-sweep`: Find unreachable code, unused exports, orphaned files, and dead CSS. Report-only by default with confidence levels. `--apply` shows diff preview and asks for confirmation before removing
- `/update-docs`: Detect and update project documentation affected by recent code changes. Analyses git diff, cross-references with docs, generates updates with provenance tracking. Delegates to doc-bard for writing and grumpy-documentation-pedant for validation. Preview-only by default with `--apply` for confirmed writes

### Changed
- **Command count**: 30 commands (up from 21) — added 9 developer workflow commands
- **Command categories**: Added new "Developer Workflow" category to `/list-commands`

## [1.4.0] - 2026-03-18

### Added

#### New Commands (21 total, up from 17)
- `/parliament-optimize`: Advisory audit of all agent definitions — recommends effort/model settings based on role
- `/parliament-webhook`: Configure HTTP webhook notification endpoints for Slack, Discord, Teams, or custom URLs
- `/parliament-loop`: Set up recurring execution of Parliament commands via Claude Code's `/loop` integration
- `/parliament-monitor`: Manage background monitoring agents for continuous code oversight during sessions

#### Agent Frontmatter Enhancements
- **Effort tiers**: All 30 agents now have `effort` frontmatter — orchestrators `high`, specialists `medium`, reviewers `low`. Estimated 40-60% token cost reduction on review tasks
- **maxTurns limits**: All agents now have `maxTurns` — orchestrators 30, planning 20, specialists 15, reviewers 5
- **Memory scopes**: All 16 specialists now have `memory: project` for persistent project knowledge across sessions
- **Worktree isolation**: All 15 implementation specialists now have `isolation: worktree` for parallel work in isolated git branches (security-knight, doc-bard, package-wizard, dependency-detective, observability-oracle added)

#### New Hooks
- **StopFailure**: Fires on API errors (rate limits, auth failures) during Parliament sessions — logs failure and optionally notifies via webhook
- **PostCompact**: Fires after context compaction — checkpoints state for monitoring context usage patterns
- **InstructionsLoaded**: Fires when CLAUDE.md or rules files are loaded/reloaded — detects stale rules in long sessions

#### Agent Standards
- `.claude/rules/agent-standards.md`: Comprehensive frontmatter standards document covering effort tiers, maxTurns guidelines, memory scopes, tool restrictions, isolation patterns, and templates for each agent role

#### Agent Teams Abstraction (Phase 3 Scaffold)
- `CommunicationLayer` abstraction in `src/deliberation/core/communication.py` — unified interface for inter-agent communication
- `TaskCommunication`: Stable implementation using current Task() subagent model
- `AgentTeamsCommunication`: Experimental placeholder for Agent Teams (v2.1.32+), behind `PARLIAMENT_USE_AGENT_TEAMS=1` feature flag
- Go/no-go gate: Agent Teams integration activates only when the feature exits Claude Code's research preview

### Changed
- **notify_teams.sh**: Added support for StopFailure, PostCompact, and InstructionsLoaded hook events
- **settings.json**: Added StopFailure, PostCompact, and InstructionsLoaded hook configurations with dedicated handler scripts
- **Agent count**: 30 agents (unchanged), now with standardised frontmatter across all roles
- **Command count**: 21 commands (up from 17)

## [1.3.0] - 2026-03-18

### Added
- Native Claude Code plugin installation via `claude plugin marketplace add` and `claude plugin install`

### Changed
- **Hook scripts relocated** from `hooks/` to `src/hooks/` so they survive plugin cache (fixes hooks not working for installed users)
- **Install commands updated** across all documentation to use native `claude plugin` CLI commands instead of non-existent `/install-github-plugin`
- **Update commands updated** to use `claude plugin update parliament-of-chaos@parliament-of-chaos`
- **notify_teams.sh**: Fixed JSON injection vulnerability — payload now constructed with `jq` instead of string interpolation
- **system-architect**: Added `Bash` to `disallowedTools` to enforce read-only access consistently with other analysis agents

### Fixed
- Hooks and settings.json were stripped from plugin cache because they lived in `hooks/` (not cached); moved to `src/hooks/` which is cached
- JSON injection risk in Teams webhook notifications via crafted project directory names

## [1.2.0] - 2026-01-15

### Changed
- Version bump for marketplace registration and Phase 3 advanced orchestration features
- No user-facing changes beyond what was included in the 1.1.0 release

## [1.1.0] - 2025-12-05

### Added

#### New Agents (29 total, up from 21)
- **migration-monk**: Schema migrations and rollback strategies
- **dependency-detective**: Vulnerability chains and license compliance
- **refactor-ranger**: Code smells and refactoring patterns
- **config-curator**: Environment config, secrets, and feature flags
- **observability-oracle**: Logging, metrics, tracing, and alerting
- **grumpy-accessibility-auditor**: WCAG compliance and inclusive design
- **grumpy-documentation-pedant**: Documentation completeness
- **grumpy-testing-tyrant**: Test coverage and quality

#### New Commands (12 total)
- `/list-agents`: Display all agents grouped by category
- `/list-commands`: Display all commands grouped by category
- `/explain-agent <agent>`: Detailed explanation of what an agent does and when to use it
- `/summon-specialist <agent>`: Directly invoke a specialist agent on your current task
- `/parliament-review`: Full review using all 9 grumpy reviewers for maximum scrutiny

#### Features
- **Standards Compliance**: All 16 specialist agents now include a "Standards Compliance" section instructing them to consult official documentation, verify recommendations, and cite sources for framework-specific patterns
- **Conflict Resolution Protocol**: Introduced priority-based conflict resolution (security > correctness > maintainability > performance) for when reviewers disagree
- **Marketplace Configuration**: Added `.claude-plugin/marketplace.json` to register the plugin for Claude Code marketplace
- **Hooks Configuration Guide**: New comprehensive guide (`docs/hooks.md`) explaining how to configure and use hooks for notifications and automation
- **Agent Memory Context**: Added roadmap specification for persistent agent memory across sessions
- **Configurable Grumpiness**: Added roadmap specification for adjustable reviewer strictness levels
- **Review Report Export**: Added roadmap specification for exporting review reports to various formats

### Changed
- **Agent Definitions**: Revised all agent role definitions and output structures for clarity, consistency, and conciseness
- **Senior Council**: Updated task analysis to reference project conventions and standards instead of specific files
- **Command Optimization**: Optimized `/summon-council` and `/summon-grumpy-reviewer` commands for brevity and token efficiency
- **Documentation**: Expanded and improved documentation across all guides (installation, usage, hooks, safe progress assurance)
- **Roadmap Structure**: Added scoped and completed status tracking for roadmap items
- **Agent Count**: Updated from 21 to 29 agents throughout documentation

### Improved
- Agent selection logic in senior-council with expanded specialist roles
- Verification steps and cross-referencing across all agent definitions
- Response style consistency across specialist agents
- Installation and usage guides to reflect the expanded multi-agent, multi-command workflow

## [1.0.0] - 2025-12-03

### Added
- Initial release of Parliament of Chaos
- 21 AI agents (11 specialists, 6 grumpy reviewers, 3 planning agents, 1 orchestrator)
- 7 slash commands for project planning and code review
- Complete documentation suite
- MIT License
- Example project files demonstrating the planning workflow

[1.15.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.12.0...v1.13.0
[1.12.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.8.1...v1.9.0
[1.8.1]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.8.0...v1.8.1
[1.8.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/JackScammell/Parliament-Of-Chaos/compare/V1.0.0...v1.1.0
[1.0.0]: https://github.com/JackScammell/Parliament-Of-Chaos/releases/tag/V1.0.0
