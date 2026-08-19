#!/usr/bin/env python3
"""Parliament of Chaos — repo conformance gate (v1.26.0 "The Gate").

Validates the repository's own invariants against its authoritative rule
sources and exits non-zero with a per-violation report when the repo has
drifted. Deterministic: filesystem reads only, no network, sorted output.

Rule sources (read the docs, not this script, to amend policy):
  .claude/rules/agent-standards.md   — fleet frontmatter tables (the tables in
                                        this script's constants are derived
                                        from it; update both together)
  .claude/rules/fan-out-policy.md    — single source for the circuit-breaker
                                        threshold and the v2.1.128 fan-out
                                        version floor (check 6)
  commands/manifest.yaml             — its own header documents the per-entry
                                        contract reconciled by check 3
  RELEASE_INSTRUCTIONS.md            — the three-way version-sync rule
                                        enforced by check 4

Checks (see --list-checks):
  1. agent-frontmatter     — 33-agent fleet standards (roles, effort, maxTurns,
                             memory, model pins, disallowedTools, background)
  2. fanout-contract       — the 29 fan-out-capable agents carry the
                             "Fan-Out Contract (fan-out-policy B5 + B6)" section
                             (folded into check 1's file pass)
  3. manifest              — commands/manifest.yaml <-> commands/*.md
                             reconciliation (ghosts, missing, effort, owner)
  4. version-sync          — plugin.json / marketplace.json / CHANGELOG agree
  5. hooks                 — hooks/hooks.json shape, script existence and exec
                             bits, and the v1.25.1 duplicate-registration guard
  6. single-source         — circuit-breaker threshold and version floor only
                             stated in fan-out-policy.md (or cited from it)

Exit code: 1 if any ERROR (or any WARN with --strict), else 0.
Output: one line per violation, "SEVERITY path: message", then a summary.

Dependencies: Python 3 stdlib + PyYAML only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "ERROR conformance: PyYAML is required (pip install pyyaml)\n"
    )
    sys.exit(2)

# --------------------------------------------------------------------------
# Fleet expectations — derived from .claude/rules/agent-standards.md.
# If a table below disagrees with that file, the file wins: fix this script.
# --------------------------------------------------------------------------

ORCHESTRATORS = {"senior-council", "deliberation-conductor"}
PLANNING = {"project-oracle", "scope-weaver"}
TASK_EXECUTOR = {"task-executor"}
# Grumpy reviewers are identified by the `grumpy-` filename prefix; every
# remaining agent is a specialist. Expected fleet shape:
EXPECTED_COUNTS = {
    "orchestrator": 2,
    "specialist": 16,
    "reviewer": 12,
    "planning": 2,
    "task-executor": 1,
}
EXPECTED_TOTAL = 33

# agent-standards.md "Model Selection": the five ADVISORY reviewers are pinned
# to sonnet (measured cost deviation); everything else — including the floor
# reviewers grumpy-security-nag / grumpy-code-reviewer — must stay `inherit`.
SONNET_ADVISORY = {
    "grumpy-performance-troll",
    "grumpy-accessibility-auditor",
    "grumpy-documentation-pedant",
    "grumpy-i18n-nitpicker",
    "grumpy-budget-hawk",
}

REQUIRED_FM_FIELDS = (
    "name", "description", "model", "color", "permissionMode",
    "effort", "maxTurns",
)

EFFORT_BY_ROLE = {
    "orchestrator": "high",
    "reviewer": "low",
    "specialist": "medium",
    "planning": "medium",
    "task-executor": "medium",
}
MAXTURNS_BY_ROLE = {
    "orchestrator": 30,
    "planning": 20,
    "task-executor": 20,
    "specialist": 15,
    "reviewer": 5,
}
MEMORY_BY_ROLE = {  # reviewers accumulate cross-project review taste
    "orchestrator": "project",
    "planning": "project",
    "task-executor": "project",
    "specialist": "project",
    "reviewer": "user",
}

# governance.md: reviewers never modify code and never spawn agents;
# system-architect is advisory (designs, does not implement).
READONLY_DISALLOWED = {
    "Edit", "Write", "NotebookEdit", "Bash", "Task", "Agent", "SendMessage",
}
# Non-orchestrators that may implement still must not spawn sub-agents.
NO_SPAWN_DISALLOWED = {"Task", "Agent", "SendMessage"}
READONLY_SPECIALISTS = {"system-architect"}

# Check 2: exact section-heading marker required in every fan-out-capable
# agent (16 specialists + 12 reviewers + task-executor = 29). Orchestrators
# and planning agents are never fanned out and are exempt.
FANOUT_CONTRACT_MARKER = "Fan-Out Contract (fan-out-policy B5 + B6)"

# Check 6: strings whose single source is .claude/rules/fan-out-policy.md.
#   - breaker threshold: "≥ 2 of its last 3 dispatches"
#   - parallel fan-out version floor: v2.1.128
# CHANGELOG.md is allowed as a historical record. Any other file may only
# carry the string alongside an explicit citation of "fan-out-policy"
# (attribution, not restatement); an uncited restatement is single-source
# drift and is reported as WARN.
SINGLE_SOURCE = Path(".claude/rules/fan-out-policy.md")
HISTORICAL_OK = {Path("CHANGELOG.md")}
LINT_PATTERNS = {
    "circuit-breaker threshold": re.compile(r"2 of its last 3"),
    "v2.1.128 fan-out version floor": re.compile(r"2\.1\.128"),
}
LINT_CITATION = re.compile(r"fan-out-policy")
LINT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".sh", ".py"}
# .project-files/ is user-owned planning history (agent-standards.md "Plugin
# State Storage"), not plugin-shipped source — the lint does not police it.
LINT_EXCLUDE_DIRS = {".git", "node_modules", "worktrees", ".telemetry", ".project-files"}

# Check 5: every hook command must take exactly this shape.
HOOK_CMD_RE = re.compile(
    r'^"\$\{CLAUDE_PLUGIN_ROOT\}"/src/hooks/([A-Za-z0-9_.-]+)$'
)

SEMVER_HEADING_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.M)


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

class Report:
    """Collects violations; keeps output deterministic (insertion order is
    the check order; each check emits in sorted-path order)."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []  # (severity, path, msg)

    def error(self, path: object, msg: str) -> None:
        self.rows.append(("ERROR", str(path), msg))

    def warn(self, path: object, msg: str) -> None:
        self.rows.append(("WARN", str(path), msg))

    def count(self, severity: str) -> int:
        return sum(1 for s, _, _ in self.rows if s == severity)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def read_frontmatter(path: Path) -> dict:
    """Parse the YAML frontmatter block of a markdown file.

    Raises ValueError if the file has no leading `---` fence pair or the
    block is not valid YAML / not a mapping.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("no YAML frontmatter block")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("unterminated YAML frontmatter block")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a YAML mapping")
    return data


def agent_role(name: str) -> str:
    if name in ORCHESTRATORS:
        return "orchestrator"
    if name in PLANNING:
        return "planning"
    if name in TASK_EXECUTOR:
        return "task-executor"
    if name.startswith("grumpy-"):
        return "reviewer"
    return "specialist"


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------
# Check 1 + 2 — agent frontmatter standards and the fan-out contract
# --------------------------------------------------------------------------

def check_agents(root: Path, rep: Report) -> None:
    agents_dir = root / "agents"
    files = sorted(agents_dir.glob("*.md"))
    if not files:
        rep.error("agents/", "no agent files found")
        return

    counts: dict[str, int] = {k: 0 for k in EXPECTED_COUNTS}
    for path in files:
        p = rel(root, path)
        stem = path.stem
        role = agent_role(stem)
        counts[role] += 1

        try:
            fm = read_frontmatter(path)
        except (ValueError, yaml.YAMLError) as exc:
            rep.error(p, f"frontmatter does not parse: {exc}")
            continue

        # Required fields (agent-standards.md "Required Fields").
        missing = [f for f in REQUIRED_FM_FIELDS if f not in fm]
        if missing:
            rep.error(p, f"missing required frontmatter fields: {', '.join(missing)}")
        if fm.get("name") != stem:
            rep.error(p, f"frontmatter name {fm.get('name')!r} != filename stem {stem!r}")

        # Effort tier by role.
        want = EFFORT_BY_ROLE[role]
        if "effort" in fm and fm["effort"] != want:
            rep.error(p, f"{role} must have effort: {want}, found {fm['effort']!r}")

        # maxTurns by role.
        want_turns = MAXTURNS_BY_ROLE[role]
        if "maxTurns" in fm and fm["maxTurns"] != want_turns:
            rep.error(p, f"{role} must have maxTurns: {want_turns}, found {fm['maxTurns']!r}")

        # Memory scope by role.
        want_mem = MEMORY_BY_ROLE[role]
        if fm.get("memory") != want_mem:
            rep.error(p, f"{role} must have memory: {want_mem}, found {fm.get('memory')!r}")

        # Model pins: exactly the five advisory reviewers are sonnet; the
        # floor reviewers and everyone else must stay on inherit.
        want_model = "sonnet" if stem in SONNET_ADVISORY else "inherit"
        if "model" in fm and fm["model"] != want_model:
            rep.error(
                p,
                f"model must be {want_model!r} "
                f"({'advisory-tier cost pin' if stem in SONNET_ADVISORY else 'fleet default / floor'}), "
                f"found {fm['model']!r}",
            )

        # disallowedTools by role (governance.md delegation + read-only rules).
        dt = set(fm.get("disallowedTools") or [])
        if role == "orchestrator":
            # Orchestrators spawn sub-agents: Task must NOT be disallowed.
            if "Task" in dt:
                rep.error(p, "orchestrator must not disallow Task (it spawns sub-agents)")
        elif role == "reviewer" or stem in READONLY_SPECIALISTS:
            lacking = sorted(READONLY_DISALLOWED - dt)
            if lacking:
                rep.error(
                    p,
                    "read-only agent must disallow "
                    f"{{{', '.join(sorted(READONLY_DISALLOWED))}}}; missing: {', '.join(lacking)}",
                )
        else:
            lacking = sorted(NO_SPAWN_DISALLOWED - dt)
            if lacking:
                rep.error(
                    p,
                    "non-orchestrator must disallow "
                    f"{{{', '.join(sorted(NO_SPAWN_DISALLOWED))}}}; missing: {', '.join(lacking)}",
                )

        # background: true on all 12 reviewers, and only on them.
        bg = fm.get("background", False)
        if role == "reviewer" and bg is not True:
            rep.error(p, "reviewer must set background: true")
        if role != "reviewer" and bg:
            rep.error(p, f"{role} must not set background: true (reviewers only)")

        # Check 2 — Fan-Out Contract section on fan-out-capable agents.
        if role in ("specialist", "reviewer", "task-executor"):
            if FANOUT_CONTRACT_MARKER not in path.read_text(encoding="utf-8"):
                rep.error(p, f'fan-out-capable agent missing section "{FANOUT_CONTRACT_MARKER}"')

    # Fleet shape: 2 orchestrators + 16 specialists + 12 reviewers
    # + 2 planning + 1 task-executor = 33.
    for role_name in sorted(EXPECTED_COUNTS):
        if counts[role_name] != EXPECTED_COUNTS[role_name]:
            rep.error(
                "agents/",
                f"expected {EXPECTED_COUNTS[role_name]} {role_name} agents, found {counts[role_name]}",
            )
    if len(files) != EXPECTED_TOTAL:
        rep.error("agents/", f"expected {EXPECTED_TOTAL} agent files, found {len(files)}")


# --------------------------------------------------------------------------
# Check 3 — manifest reconciliation (parliament-doctor's deterministic core)
# --------------------------------------------------------------------------

def check_manifest(root: Path, rep: Report) -> None:
    manifest_path = root / "commands" / "manifest.yaml"
    mp = rel(root, manifest_path)
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        rep.error(mp, f"manifest does not parse: {exc}")
        return
    entries = (manifest or {}).get("commands")
    if not isinstance(entries, list):
        rep.error(mp, "manifest has no top-level 'commands' list")
        return

    cmd_files = {
        f.stem: f for f in sorted((root / "commands").glob("*.md"))
    }
    seen: dict[str, dict] = {}
    for entry in entries:
        name = entry.get("name") if isinstance(entry, dict) else None
        if not name:
            rep.error(mp, f"manifest entry without a name: {entry!r}")
            continue
        if name in seen:
            rep.error(mp, f"duplicate manifest entry: {name}")
            continue
        seen[name] = entry

    # Ghosts (file, no entry) and missing (entry, no file) — manifest header
    # terminology.
    for name in sorted(set(cmd_files) - set(seen)):
        rep.error(mp, f"ghost command: commands/{name}.md exists but has no manifest entry")
    for name in sorted(set(seen) - set(cmd_files)):
        rep.error(mp, f"missing command: manifest lists {name!r} but commands/{name}.md does not exist")

    for name in sorted(set(seen) & set(cmd_files)):
        entry = seen[name]
        cp = rel(root, cmd_files[name])

        # Per-entry effort must match the command file's frontmatter effort.
        try:
            fm = read_frontmatter(cmd_files[name])
        except (ValueError, yaml.YAMLError) as exc:
            rep.error(cp, f"command frontmatter does not parse: {exc}")
            continue
        if entry.get("effort") != fm.get("effort"):
            rep.error(
                cp,
                f"effort drift: manifest says {entry.get('effort')!r}, "
                f"frontmatter says {fm.get('effort')!r}",
            )

        # Owner must resolve to an agent definition.
        owner = entry.get("owner")
        if not owner:
            rep.error(mp, f"entry {name!r} has no owner")
        elif not (root / "agents" / f"{owner}.md").is_file():
            rep.error(mp, f"entry {name!r} owner {owner!r} does not resolve to agents/{owner}.md")


# --------------------------------------------------------------------------
# Check 4 — version sync (RELEASE_INSTRUCTIONS.md pre-release rule)
# --------------------------------------------------------------------------

def check_version_sync(root: Path, rep: Report) -> None:
    plugin_path = root / ".claude-plugin" / "plugin.json"
    market_path = root / ".claude-plugin" / "marketplace.json"
    changelog_path = root / "CHANGELOG.md"

    versions: dict[str, str | None] = {}
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        versions[f"{rel(root, plugin_path)} version"] = plugin.get("version")
    except (OSError, json.JSONDecodeError) as exc:
        rep.error(rel(root, plugin_path), f"unreadable: {exc}")
        return
    try:
        market = json.loads(market_path.read_text(encoding="utf-8"))
        versions[f"{rel(root, market_path)} metadata.version"] = (
            market.get("metadata") or {}
        ).get("version")
        plugins = market.get("plugins") or [{}]
        versions[f"{rel(root, market_path)} plugins[0].version"] = plugins[0].get("version")
    except (OSError, json.JSONDecodeError) as exc:
        rep.error(rel(root, market_path), f"unreadable: {exc}")
        return

    changelog = changelog_path.read_text(encoding="utf-8")
    m = SEMVER_HEADING_RE.search(changelog)
    top = m.group(1) if m else None
    versions[f"{rel(root, changelog_path)} top '## [X.Y.Z]' heading"] = top

    distinct = {v for v in versions.values()}
    if None in distinct or len(distinct) != 1:
        detail = "; ".join(f"{k} = {v!r}" for k, v in sorted(versions.items()))
        rep.error(".claude-plugin/", f"version strings out of sync: {detail}")
        return

    # The released version must also have its compare link at the bottom.
    link_re = re.compile(rf"^\[{re.escape(top)}\]:\s+\S+", re.M)
    if not link_re.search(changelog):
        rep.error(rel(root, changelog_path), f"no '[{top}]:' compare link found for the top release")


# --------------------------------------------------------------------------
# Check 5 — hook configuration (incl. the v1.25.1 duplicate-registration guard)
# --------------------------------------------------------------------------

def check_hooks(root: Path, rep: Report) -> None:
    hooks_path = root / "hooks" / "hooks.json"
    hp = rel(root, hooks_path)
    try:
        cfg = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        rep.error(hp, f"unreadable or invalid JSON: {exc}")
        return

    if set(cfg) != {"hooks"}:
        rep.error(hp, f"top-level keys must be exactly {{'hooks'}}, found {sorted(cfg)}")
    events = cfg.get("hooks")
    if not isinstance(events, dict) or not events:
        rep.error(hp, "'hooks' must be a non-empty object of event -> matcher list")
        return

    # Events are validated generically — no hard-coded event-name map or count,
    # so newly added events (e.g. the SessionStart -> log_event.sh heartbeat)
    # pass so long as their commands take the canonical shape below.
    reported_unexec: set[Path] = set()
    for event in sorted(events):
        matchers = events[event]
        if not isinstance(matchers, list):
            rep.error(hp, f"event {event!r}: expected a list of matcher objects")
            continue
        for matcher in matchers:
            if not isinstance(matcher, dict):
                # Fail closed with a clean report, not an AttributeError
                # (security review: rough edge on non-dict matchers).
                rep.error(hp, f"event {event!r}: matcher entries must be objects, found {type(matcher).__name__}")
                continue
            for hook in matcher.get("hooks", []):
                if not isinstance(hook, dict):
                    rep.error(hp, f"event {event!r}: hook entries must be objects, found {type(hook).__name__}")
                    continue
                if hook.get("type") != "command":
                    rep.error(hp, f"event {event!r}: hook type must be 'command', found {hook.get('type')!r}")
                    continue
                cmd = hook.get("command", "")
                m = HOOK_CMD_RE.match(cmd)
                if not m:
                    rep.error(
                        hp,
                        f"event {event!r}: command must be "
                        f'"${{CLAUDE_PLUGIN_ROOT}}"/src/hooks/<script>, found {cmd!r} '
                        "(hooks must live in src/hooks/ to survive the plugin cache)",
                    )
                    continue
                script = root / "src" / "hooks" / m.group(1)
                if not script.is_file():
                    rep.error(hp, f"event {event!r}: referenced script src/hooks/{m.group(1)} does not exist")
                elif not os.access(script, os.X_OK) and script not in reported_unexec:
                    reported_unexec.add(script)  # report once, not per reference
                    rep.error(rel(root, script), "referenced hook script is not executable (chmod +x)")

    # v1.25.1 regression guard: Claude Code auto-loads hooks/hooks.json, so a
    # plugin.json "hooks" field is a duplicate registration that breaks
    # plugin loading entirely ("Duplicate hooks file detected").
    plugin_path = root / ".claude-plugin" / "plugin.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        if "hooks" in plugin:
            rep.error(
                rel(root, plugin_path),
                "must not declare a 'hooks' field — hooks/hooks.json is auto-loaded "
                "and double registration breaks plugin load (v1.25.1 regression)",
            )
    except (OSError, json.JSONDecodeError):
        pass  # already reported by check 4

    # No-policy stance: Parliament ships no settings file at the repo root.
    if (root / "settings.json").exists():
        rep.error("settings.json", "root settings.json must not exist (no-policy stance; hooks ship via hooks/hooks.json)")


# --------------------------------------------------------------------------
# Check 6 — single-source lint for fan-out-policy.md owned facts
# --------------------------------------------------------------------------

def check_single_source(root: Path, rep: Report) -> None:
    self_path = Path(__file__).resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in LINT_SUFFIXES:
            continue
        relpath = Path(rel(root, path))
        # Exclusions are judged on repo-relative parts so an absolute root
        # that itself lives under e.g. a "worktrees" dir is not skipped.
        if any(part in LINT_EXCLUDE_DIRS for part in relpath.parts):
            continue
        if relpath == SINGLE_SOURCE or relpath in HISTORICAL_OK:
            continue
        if path.resolve() == self_path or relpath == Path("scripts/ci/conformance.py"):
            continue  # this linter names its own patterns
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # NOTE: citation granularity is per-FILE, not per-line — one
        # "fan-out-policy" mention anywhere in a file exempts every marker in
        # it. Coarse but acceptable for a WARN-tier drift lint (two reviewers
        # judged and accepted this); do not assume per-occurrence checking.
        cites_source = bool(LINT_CITATION.search(text))
        for label, pattern in sorted(LINT_PATTERNS.items()):
            if not pattern.search(text):
                continue
            if cites_source:
                # Attribution, not restatement — e.g. /parliament-metrics and
                # /env-doctor quote the value while pointing at the policy.
                continue
            rep.warn(
                relpath,
                f"restates the {label} without citing fan-out-policy.md "
                f"(single source: {SINGLE_SOURCE})",
            )


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

CHECKS = [
    ("agent-frontmatter", "agents/*.md fleet standards (incl. fan-out contract)", check_agents),
    ("manifest", "commands/manifest.yaml <-> commands/*.md reconciliation", check_manifest),
    ("version-sync", "plugin.json / marketplace.json / CHANGELOG.md version agreement", check_version_sync),
    ("hooks", "hooks/hooks.json shape, scripts, duplicate-registration guard", check_hooks),
    ("single-source", "fan-out-policy.md owned facts are not restated elsewhere", check_single_source),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Parliament of Chaos conformance gate")
    parser.add_argument("--list-checks", action="store_true", help="list check names and exit")
    parser.add_argument("--strict", action="store_true", help="treat WARN as failing")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repo root (default: two levels above this script)",
    )
    args = parser.parse_args()

    if args.list_checks:
        for name, desc, _ in CHECKS:
            print(f"{name:20s} {desc}")
        return 0

    root = args.root.resolve()
    rep = Report()
    for _, _, fn in CHECKS:
        fn(root, rep)

    for severity, path, msg in rep.rows:
        print(f"{severity} {path}: {msg}")

    errors, warns = rep.count("ERROR"), rep.count("WARN")
    print(f"conformance: {errors} error(s), {warns} warning(s)")
    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
