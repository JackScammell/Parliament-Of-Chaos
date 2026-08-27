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
  0. bom                   — no byte-order mark on any shipped asset (UTF-8
                             anywhere in the file, UTF-16/32 at byte 0). Runs
                             FIRST, by design: a BOM already fails the
                             parse-load-bearing checks below, but with a
                             diagnostic that points at the wrong thing, and it
                             passes SILENTLY on the raw-text assets nobody parses
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
  6. single-source-literals— circuit-breaker threshold and version floor only
                             stated in fan-out-policy.md (or cited from it).
                             A TWO-LITERAL spot-check, not prose-duplication
                             detection — see LINT_PATTERNS
  7. reviewer-verdicts     — every grumpy reviewer names the three-token verdict
                             vocabulary in its own verdict instruction, and
                             instructs no binary approve/reject
  8. probe-corpus          — the detectors behind checks 0 and 7 are replayed
                             against the committed probe corpus in
                             scripts/ci/fixtures/ (also available standalone as
                             --self-test). A detector with no committed negative
                             fixtures is a regression anecdote, not a test

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
# SCOPE, stated plainly so nobody over-reads a green check 6: this is a
# TWO-LITERAL SPOT-CHECK on two chosen facts, NOT general prose-duplication
# detection. A passing check 6 says only "these two literals are not restated
# uncited"; it says nothing about whether any other content is duplicated
# across the repo. Adding a third owned fact means adding a third pattern here.
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

# Check 0: assets that must never carry a byte-order mark.
UTF8_BOM = b"\xef\xbb\xbf"
# UTF-16/32 BOMs break the harness identically to a UTF-8 one (the file simply
# does not decode as UTF-8), so they get the same detect-and-refuse posture.
# Longest signature FIRST: a UTF-32LE BOM (FF FE 00 00) starts with the
# UTF-16LE one (FF FE), so a shortest-first scan would mislabel it. Needs a
# 4-byte read, hence the whole-file read below rather than a 3-byte head.
BOM_SIGNATURES = (
    (b"\x00\x00\xfe\xff", "UTF-32BE"),
    (b"\xff\xfe\x00\x00", "UTF-32LE"),
    (b"\xfe\xff", "UTF-16BE"),
    (b"\xff\xfe", "UTF-16LE"),
)
BOM_LABEL_BYTES = {label: sig for sig, label in BOM_SIGNATURES}
BOM_SCAN_GLOBS = (
    "agents/**/*.md",
    "commands/**/*.md",
    "commands/manifest.yaml",
    ".claude/rules/**/*.md",
    ".claude-plugin/*.json",
    "hooks/hooks.json",
    "CHANGELOG.md",
    "README.md",
    "RELEASE_INSTRUCTIONS.md",
    # The gate's own machinery is a shipped asset class too. The realistic
    # regression here is a literal BOM pasted MID-FILE — into one of this
    # module's own error-message string literals, which describe BOM bytes —
    # so the scan below reads the whole file, not just byte 0. A byte-0-only
    # check would have passed that regression silently.
    "scripts/ci/**/*.py",
    "scripts/ci/**/*.sh",
    "scripts/ci/fixtures/*.txt",
    "src/hooks/**/*.sh",
    ".github/workflows/*.yml",
)

# Check 7: the B6 verdict vocabulary (output-standards.md, fan-out-policy.md B6).
# Scoped to agents/grumpy-*.md ON PURPOSE. A repo-wide scan false-positives on
# CHANGELOG.md (historical prose quoting the old wording) and on
# commands/debate-analytics.md ("approve/reject/abstain" vote-tally counts,
# which are a report field, not a reviewer's verdict instruction). The invariant
# belongs to reviewer agent definitions, so the check lives there too.
VERDICT_TOKENS = ("APPROVE", "REJECT", "NO-FINDINGS")
NO_FINDINGS_TOKEN = "NO-FINDINGS"

# The exact heading that opens the shared Fan-Out Contract boilerplate. Check 7
# assertion (a) scans the region BEFORE it — see check_reviewer_verdicts.
FANOUT_HEADING_RE = re.compile(r"^##\s+Fan-Out Contract\b", re.M)

# Word families. `(?i:...)` is scoped ON PURPOSE: the lookaheads that exempt
# the exact uppercase tokens MUST stay case-sensitive, or they would exempt
# "approve" along with "APPROVE" and the whole check would collapse.
_APPROVE = r"(?i:approv(?:e|es|ed|ing|al|als))"
# Affirmative synonyms OUTSIDE the approve-family. Class 1 of the original
# defect was literal synonym substitution, so the next synonym is the most
# likely regression, not the least.
_AFFIRM_SYN = (
    r"(?i:sign(?:s|ed)?[\s\-]?offs?|bless(?:es|ed|ings?)?"
    r"|endorse(?:s|d|ment|ments)?|green[\s\-]?light(?:s|ed)?)"
)
_AFFIRM_ANY = r"(?:" + _APPROVE + r"|" + _AFFIRM_SYN + r")"
# Adverse family. `block` and `condemn` are here — PAIR POSITION ONLY — and
# deliberately absent from the blanket backstop below: the shared Fan-Out
# Contract prose legitimately contains "a member blocked waiting on input",
# "non-blocking" and "B6 condemns a member that reviewed and then gave no
# verdict". In pair position they cannot collide with that prose; as blanket
# terms they would fail all twelve reviewers.
_ADVERSE = (
    r"(?i:reject(?:s|ed|ing|ion|ions)?|object(?:s|ed|ing|ion|ions)?"
    r"|declin(?:e|es|ed)|denial|den(?:y|ies|ied)|refus(?:e|es|ed|al)"
    r"|veto(?:e?s|ed)?|disapprov(?:e|es|ed|al|als)|condemn(?:s|ed|ing)?"
    r"|block(?:s|ed|ing)?|nack(?:s|ed)?|bounce(?:s|d)?|send(?:s)? it back)"
)
# Connector joining the two halves of a binary pair. Commas are DELIBERATELY
# excluded: the conformant three-token list "APPROVE, REJECT, or NO-FINDINGS"
# would otherwise read as a pair and fail every reviewer in the fleet.
#
# Semicolons/dashes/"vs" are NOT added either, and the reason is adjacency, not
# oversight: `_OR` only matches between two ADJACENT halves, and the historical
# semicolon defect ("Approve if maintainable; reject with guidance") has three
# words between them, so a `;` alternative would not have caught it. That
# defect is caught on CASING by NON_TOKEN_VERDICT_RE instead — which is why the
# frontmatter carve-out below had to be narrowed rather than papered over with
# more connectors.
_OR = r"[\s`'*_]*(?:or|/)[\s`'*_]*"
_NOT_TOKEN_APPROVE = r"(?!APPROVE(?![A-Za-z]))"
# Negation openers for the negative-gating shape (evasion class 3).
_NEG = r"(?i:\b(?:no|not|never|without|withhold(?:s|ing)?)\b)"

# The policy was widened FIRST, in output-standards.md ("Review Output Format"
# item 4), and this pattern mirrors it — never the other way round. Evidence
# that the previous four-literal pattern was insufficient: of 24 defective
# verdict lines across the 12 reviewers, TEN hid from it, in three classes —
#   1. synonym substitution  "Verdict: approve or object"
#   2. nominalisation        "Approval or rejection with reasons"
#   3. negative gating       "No approval until all issues addressed"
# Class 3 was the dangerous one: it concealed the defect in grumpy-security-nag
# and grumpy-privacy-paranoid (both floor) plus grumpy-standards-enforcer and
# grumpy-budget-hawk, and the narrow pattern declared all four clean.
#
# Class 3 carries the uppercase-token exemption because the CONFORMANT fix
# keeps the gating shape and fixes the vocabulary: "Never APPROVE until all
# issues addressed; REJECT while any remain; NO-FINDINGS only when the review
# surfaced none" offers all three tokens and is correct.
BINARY_VERDICT_RE = re.compile(
    # class 1 + 2 — synonym and nominalised pairs, in either order
    r"(?<![A-Za-z])" + _AFFIRM_ANY + _OR + _ADVERSE + r"(?![A-Za-z])"
    + r"|(?<![A-Za-z])" + _ADVERSE + _OR + _AFFIRM_ANY + r"(?![A-Za-z])"
    # class 3 — negative gating that never offers NO-FINDINGS
    + r"|" + _NEG + r"\s+(?:[\w-]+\s+){0,2}"
    + _NOT_TOKEN_APPROVE + _AFFIRM_ANY + r"(?![A-Za-z])"
    + r"|(?<![A-Za-z])" + _NOT_TOKEN_APPROVE + _AFFIRM_ANY + r"\s+(?i:only)\b"
)

# The SAME gating shape as class 3 but WITHOUT the uppercase-token exemption.
# Used by the same-line NO-FINDINGS rule in check 7: a gating instruction is
# allowed to keep its grammar (output-standards.md now says so explicitly), but
# only if it offers NO-FINDINGS on that same line. This is what makes
# "Never APPROVE until all issues addressed; REJECT otherwise" — which slips
# past every other pattern because both tokens are correctly spelled — fail.
GATING_SHAPE_RE = re.compile(
    _NEG + r"\s+(?:[\w-]+\s+){0,2}" + _AFFIRM_ANY + r"(?![A-Za-z])"
    + r"|(?<![A-Za-z])" + _AFFIRM_ANY + r"\s+(?i:only)\b"
)

# Blanket backstop: the verdict vocabulary may appear only as the exact
# uppercase tokens. Every one of the ten historical defects was spelled in some
# other casing, so this subsumes the three classes above.
#
# The synonym list is EXTENDED beyond approve/reject because class 1 of the
# original defect was literal synonym substitution — "approve or object" — so
# the next synonym is the most likely regression, not the least. An enumerated
# list is inherently incomplete; see the residual-risk note in check 7.
# `block`/`condemn`/`bounce` are NOT here (see _ADVERSE): they occur in
# legitimate Fan-Out Contract prose and are pair-position-only.
_BLANKET_SYN = (
    r"(?:" + _AFFIRM_SYN
    + r"|(?i:veto(?:e?s|ed)?|disapprov(?:e|es|ed|al|als)|nack(?:s|ed)?))"
)
NON_TOKEN_VERDICT_RE = re.compile(
    r"(?<![A-Za-z])"
    r"(?!APPROVE(?![A-Za-z])|REJECT(?![A-Za-z]))"
    r"(?:"
    r"(?i:approv(?:e|es|ed|ing|al|als)|reject(?:s|ed|ing|ion|ions)?)"
    r"|" + _BLANKET_SYN +
    r")"
    r"(?![A-Za-z])"
)

# NO-FINDINGS had NO casing backstop at all — an asymmetry that made lowercase
# "no findings" / "no-findings" invisible while lowercase "approve" was caught.
NON_TOKEN_NO_FINDINGS_RE = re.compile(
    r"(?<![A-Za-z])"
    r"(?!NO-FINDINGS(?![A-Za-z]))"
    r"(?i:no[\s\-]?findings?)"
    r"(?![A-Za-z])"
)

# The frontmatter carve-out, NARROWED from "all of frontmatter" to a single
# (agent, key, matched word) triple.
#
# The old carve-out excluded the whole frontmatter block from the casing
# backstop, and the comment claimed that was not a hole because
# BINARY_VERDICT_RE still scanned it. That claim was FALSE: BINARY_VERDICT_RE
# only joins an adjacent pair via `or`/`/`, so "Approve if maintainable; reject
# with guidance" — a real historical defect — was invisible to both patterns
# once moved into a `description:`. Now every frontmatter line is scanned by
# every pattern, and exactly one match is excused: the word "rejects" in
# grumpy-testing-tyrant's `description`, which reads "rejects inadequate test
# suites" — prose ABOUT the reviewer's job, not a verdict instruction.
FRONTMATTER_VERDICT_EXEMPT = {
    ("grumpy-testing-tyrant", "description", "rejects"),
}
FM_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:")

# Check 8: the committed probe corpus. A detector with no committed negative
# fixtures is a regression ANECDOTE, not a regression test — this repo was
# already burned once by an unprobed detector at a 42% miss rate.
FIXTURES_DIR = Path("scripts/ci/fixtures")
VERDICT_PROBES = FIXTURES_DIR / "verdict_probes.txt"
BOM_PROBES = FIXTURES_DIR / "bom_probes.txt"


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
    # encoding="utf-8" does NOT strip a BOM — that is intentional (see
    # check_bom). Name the BOM explicitly rather than letting the generic
    # "no YAML frontmatter block" message send a contributor hunting for a
    # `---` fence that is plainly right there.
    text = path.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):  # escape, never a literal BOM in source
        raise ValueError(
            "file starts with a UTF-8 BOM, which precedes the '---' fence and "
            "breaks frontmatter parsing (see the 'bom' check for the fix)"
        )
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
# Check 0 — no byte-order mark on any shipped asset
# --------------------------------------------------------------------------

# Shared prose for the leading-UTF-8 case. HEDGING IS DELIBERATE: the two
# version cutoffs below are REPORTED, not verified by this repo, and this
# string is shown to a contributor on every CI failure. Asserting an unverified
# version claim flatly in a contributor-facing message is the exact
# claims-never-verified pattern the last three releases spent effort removing.
# The OPERATIVE INSTRUCTION ("strip the bytes, do not use utf-8-sig") does not
# depend on the version numbers and is stated without hedging.
_BOM_CONSEQUENCE = (
    "Older Claude Code is reported to SILENTLY IGNORE a BOM-prefixed asset "
    "(per the v2.1.24x changelog: shipped assets before v2.1.239, plugin.json "
    "before v2.1.246 — unverified here; confirm before relying on either "
    "cutoff for a release decision). If that behaviour holds it does not "
    "degrade the agent, it REMOVES it from the fleet with no error — and if "
    "the removed agent is a floor reviewer, the orchestrator's enumerated "
    "member set loses its floor without a word, which is the one constructible "
    "path to a false APPROVE. Either way the fix is the same: strip the bytes; "
    'do NOT switch the reader to encoding="utf-8-sig", which hides the fault '
    "from CI while the harness still chokes on it"
)


def classify_boms(data: bytes) -> list[tuple[str, int]]:
    """Return every byte-order mark found in `data` as (label, byte offset).

    Pure function over bytes so the probe corpus (check 8) can replay it
    without writing a BOM'd file to disk.

    UTF-8 is scanned across the WHOLE buffer, not just byte 0: the realistic
    regression is a literal BOM pasted mid-file — into one of this module's own
    error-message string literals, which describe BOM bytes — and a byte-0-only
    check passes that silently. A LEADING and an EMBEDDED BOM are genuinely two
    different defects with two different fixes, so they are reported
    separately. UTF-16/32 are meaningful only at byte 0 (elsewhere those bytes
    are simply invalid UTF-8 and fail on decode), so they are checked there.
    """
    found: list[tuple[str, int]] = []
    for sig, label in BOM_SIGNATURES:
        if data.startswith(sig):
            found.append((label, 0))
            break  # longest-signature-first; never double-report FF FE 00 00
    if data.startswith(UTF8_BOM):
        found.append(("UTF-8-leading", 0))
    embedded = data.find(UTF8_BOM, 1)
    if embedded != -1:
        found.append(("UTF-8-embedded", embedded))
    return found


def check_bom(root: Path, rep: Report) -> None:
    """Refuse a byte-order mark on any shipped asset.

    Registered FIRST on purpose: a BOM already fails the parse-load-bearing
    checks below, but reports as a YAML/JSON error pointing at the wrong
    thing — and on the raw-text assets nobody parses it fails silently.

    GUARD-RAIL (unanimous panel finding — do not "fix" a BOM this way):
    NEVER absorb a BOM by switching a read to encoding="utf-8-sig". That
    silences this gate on a file the Claude Code harness itself still chokes
    on, converting a loud CI failure into a shipped broken plugin. A BOM is
    DETECTED and REFUSED here; it is never tolerated anywhere. read_frontmatter
    reads with encoding="utf-8" for exactly the same reason.
    """
    # Emptiness is guarded PER GLOB, not on the union. A union guard reports
    # green whenever any one pattern still matches, so renaming a directory or
    # nesting files one level deeper silently drops a whole asset class from
    # the scan — precisely the silent coverage loss this check exists to
    # prevent.
    targets: set[Path] = set()
    for pattern in BOM_SCAN_GLOBS:
        matched = [p for p in root.glob(pattern) if p.is_file()]
        if not matched:
            rep.error(
                "scripts/ci/conformance.py",
                f"BOM_SCAN_GLOBS pattern {pattern!r} matched no files — that "
                "asset class is silently unscanned. Fix the pattern or delete "
                "it deliberately; do not leave a glob covering nothing",
            )
        targets.update(matched)

    for path in sorted(targets):
        try:
            data = path.read_bytes()
        except OSError as exc:
            rep.error(rel(root, path), f"unreadable: {exc}")
            continue
        for label, offset in classify_boms(data):
            if label == "UTF-8-leading":
                rep.error(
                    rel(root, path),
                    "starts with a UTF-8 BOM (bytes EF BB BF at byte 0). "
                    + _BOM_CONSEQUENCE,
                )
            elif label == "UTF-8-embedded":
                rep.error(
                    rel(root, path),
                    f"contains an EMBEDDED UTF-8 BOM (bytes EF BB BF at byte "
                    f"offset {offset}, not at byte 0). This is a different "
                    "defect from a leading BOM and has a different fix: the "
                    "bytes are almost certainly inside a string literal or a "
                    "code fence that is describing a BOM. Delete them and "
                    "write the character as the escape \\ufeff (or spell the "
                    "bytes out as text, 'EF BB BF') so the file never carries "
                    "a real mark. Do not strip the file's first bytes — they "
                    "are not the problem here",
                )
            else:
                spelled = " ".join(f"{b:02X}" for b in BOM_LABEL_BYTES[label])
                rep.error(
                    rel(root, path),
                    f"starts with a {label} byte-order mark (bytes {spelled}). "
                    "This asset must be "
                    "UTF-8 without a mark: the harness reads it as UTF-8 and a "
                    "UTF-16/32 BOM breaks that read exactly as a UTF-8 BOM "
                    "does. Re-save the file as plain UTF-8; do NOT teach the "
                    "reader another encoding, which hides the fault from CI "
                    "while the harness still chokes on it",
                )


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
# Check 6 — single-source-LITERALS lint for fan-out-policy.md owned facts
#
# The check is named for its real scope. It is a spot-check on the two literals
# in LINT_PATTERNS, NOT general prose-duplication detection: a green result here
# means "those two literals are not restated uncited" and nothing more. Reading
# it as "no content is duplicated anywhere in the repo" has already produced one
# false review finding.
# --------------------------------------------------------------------------

def check_single_source(root: Path, rep: Report) -> None:
    """Two-literal spot-check — see the banner above for what it does NOT do."""
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
# Check 7 — reviewer verdict vocabulary (output-standards.md; fan-out B6)
# --------------------------------------------------------------------------

def frontmatter_keys_by_line(text: str) -> dict[int, str]:
    """Map each 1-based line number inside the frontmatter block to the
    top-level key that owns it (block scalars and list items included).

    Used to narrow the verdict carve-out from "all of frontmatter" to a single
    exempt (agent, key, word) triple — see FRONTMATTER_VERDICT_EXEMPT.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    owner: dict[int, str] = {}
    current = ""
    for lineno, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            break
        m = FM_KEY_RE.match(line)
        if m:
            current = m.group(1)
        owner[lineno] = current
    return owner


def instruction_region(text: str) -> str:
    """The reviewer's OWN verdict instruction — the file body up to the shared
    Fan-Out Contract boilerplate.

    This scoping is what makes check 7's positive assertion non-vacuous. The
    boilerplate names all three tokens verbatim in every reviewer (check 2
    independently enforces that the section exists), so a whole-file token
    search can NEVER fail: it tests the boilerplate, not the instruction. The
    defect this check exists to catch lives in the Process/Output verdict items
    above that heading.
    """
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            body = parts[2]
    m = FANOUT_HEADING_RE.search(body)
    return body[: m.start()] if m else body


def scan_verdict_line(line: str) -> list[tuple[str, str]]:
    """Return (kind, matched text) for every non-conformant verdict
    construction on `line`. Empty list == conformant.

    Shared by check 7 and the probe corpus (check 8) so the committed fixtures
    exercise the SAME predicate CI runs — a probe corpus that tested a parallel
    copy of the logic would prove nothing.
    """
    binary = [m.group(0) for m in BINARY_VERDICT_RE.finditer(line)]
    if binary:
        # Most specific message wins; do not also report the casing backstop.
        return [("binary", t) for t in binary]

    findings: list[tuple[str, str]] = []
    # Gating grammar is permitted (output-standards.md) — but only when the
    # same line offers NO-FINDINGS its own condition.
    if NO_FINDINGS_TOKEN not in line:
        m = GATING_SHAPE_RE.search(line)
        if m:
            findings.append(("gating", m.group(0)))
    for regex in (NON_TOKEN_VERDICT_RE, NON_TOKEN_NO_FINDINGS_RE):
        findings.extend(("casing", m.group(0)) for m in regex.finditer(line))
    return findings


def check_reviewer_verdicts(root: Path, rep: Report) -> None:
    """Every grumpy reviewer must name all three verdict tokens IN ITS OWN
    verdict instruction, and instruct no binary verdict. Scope is
    agents/grumpy-*.md — see the constants above for why a repo-wide scan is
    wrong, and for the evasion classes.

    RESIDUAL RISK, stated rather than papered over: the synonym families are
    enumerated, and an enumerated list is inherently incomplete. A verdict
    instruction phrased entirely in words nobody listed ("thumbs up or thumbs
    down") still passes. `block`, `condemn` and `bounce` are detected only in
    pair position because they occur in legitimate prose. What is structurally
    closed rather than enumerated is the SHAPE: assertion (a) requires all
    three tokens in the instruction region, so any instruction that omits
    NO-FINDINGS entirely fails regardless of how the other two are spelled.
    """
    files = sorted((root / "agents").glob("grumpy-*.md"))
    if len(files) != EXPECTED_COUNTS["reviewer"]:
        rep.error(
            "agents/",
            f"verdict check expected {EXPECTED_COUNTS['reviewer']} grumpy-*.md "
            f"reviewer files, found {len(files)}",
        )
    for path in files:
        p = rel(root, path)
        stem = path.stem
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            rep.error(p, f"unreadable: {exc}")
            continue

        # (a) Positive — all three tokens present as exact uppercase literals
        # in the reviewer's OWN instruction, i.e. OUTSIDE the shared Fan-Out
        # Contract boilerplate. Scanning the whole file here is vacuous: the
        # boilerplate names all three tokens and check 2 already guarantees it
        # is present, so `missing` could never be non-empty and the assertion
        # tested nothing.
        region = instruction_region(text)
        missing = [t for t in VERDICT_TOKENS if t not in region]
        if missing:
            rep.error(
                p,
                "reviewer's own verdict instruction must name the whole verdict "
                "vocabulary as exact uppercase literals; missing from the file "
                "body above the Fan-Out Contract section: "
                f"{', '.join(missing)}. Naming the tokens only in the shared "
                "boilerplate does not count — a reviewer whose Process/Output "
                "items never offer NO-FINDINGS has no conformant way to say "
                "'reviewed, found nothing', so it falls silent, and silence is "
                "classified Non-reporting",
            )

        # (b)-(d) Negative — binary pairs, uncompensated gating, and the casing
        # backstops, over EVERY line including frontmatter. Only individually
        # allowlisted frontmatter matches are excused.
        fm_owner = frontmatter_keys_by_line(text)
        for lineno, line in enumerate(text.splitlines(), 1):
            key = fm_owner.get(lineno)
            for kind, matched in scan_verdict_line(line):
                if key is not None and (stem, key, matched.lower()) in FRONTMATTER_VERDICT_EXEMPT:
                    continue
                if kind == "binary":
                    rep.error(
                        p,
                        f"line {lineno}: binary verdict instruction {matched!r} — "
                        "a verdict instruction must offer all three of "
                        f"{'/'.join(VERDICT_TOKENS)}; binary formulations are "
                        "non-conformant however they are spelled (synonym pairs, "
                        "nominalised pairs, negative gating). See "
                        ".claude/rules/output-standards.md, Review Output Format "
                        "item 4",
                    )
                elif kind == "gating":
                    rep.error(
                        p,
                        f"line {lineno}: gating verdict instruction {matched!r} "
                        "with no NO-FINDINGS on the same line. Gating grammar is "
                        "allowed, but each of the three tokens needs its own "
                        "condition: 'Never APPROVE until all issues addressed; "
                        "REJECT while any remain; NO-FINDINGS only when the "
                        "review surfaced none'. Stopping at 'REJECT otherwise' "
                        "spells both tokens correctly and still leaves a "
                        "reviewer that found nothing with nothing to say",
                    )
                else:
                    rep.error(
                        p,
                        f"line {lineno}: verdict vocabulary {matched!r} is not an "
                        f"exact uppercase token — write one of {'/'.join(VERDICT_TOKENS)} "
                        "or reword. Every one of the ten historical defects was "
                        "spelled in some casing other than the token's",
                    )


# --------------------------------------------------------------------------
# Check 8 — replay the committed probe corpus against the live detectors
# --------------------------------------------------------------------------

def _read_probe_rows(path: Path) -> list[tuple[int, str, str]]:
    """Yield (line number, expectation field, payload) for a probe file.

    Format, both corpora: `<EXPECTATION><whitespace><payload to end of line>`.
    Blank lines and `#` comments are ignored.
    """
    rows: list[tuple[int, str, str]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        parts = raw.split(None, 1)
        if len(parts) != 2:
            rows.append((lineno, "", ""))  # malformed; reported by the caller
            continue
        rows.append((lineno, parts[0], parts[1]))
    return rows


def check_probe_corpus(root: Path, rep: Report) -> None:
    """Assert the verdict and BOM detectors fire on every committed defective
    probe and on no control probe.

    Registered as a normal check (not only behind --self-test) ON PURPOSE: that
    is what puts it in CI without any change to the workflow file. A detector
    whose only evidence of working is a council transcript is a regression
    anecdote; this repo has already shipped one unprobed detector that missed
    42% of the defects it was written to catch.
    """
    # --- verdict probes -------------------------------------------------
    vp = root / VERDICT_PROBES
    p = str(VERDICT_PROBES)
    if not vp.is_file():
        rep.error(p, "probe corpus is missing — check 7's detectors are unproven")
    else:
        seen = 0
        for lineno, expectation, probe in _read_probe_rows(vp):
            if expectation not in ("DEFECT", "CONTROL"):
                rep.error(p, f"line {lineno}: expectation must be DEFECT or CONTROL, found {expectation!r}")
                continue
            seen += 1
            findings = scan_verdict_line(probe)
            if expectation == "DEFECT" and not findings:
                rep.error(
                    p,
                    f"line {lineno}: MISSED DEFECT — {probe!r} is a known "
                    "non-conformant verdict instruction but check 7's detectors "
                    "do not fire on it",
                )
            elif expectation == "CONTROL" and findings:
                kinds = ", ".join(f"{k}:{t!r}" for k, t in findings)
                rep.error(
                    p,
                    f"line {lineno}: FALSE POSITIVE — {probe!r} is conformant "
                    f"phrasing but check 7 flagged it ({kinds})",
                )
        if seen == 0:
            rep.error(p, "probe corpus contains no probes")

    # --- BOM probes -----------------------------------------------------
    bp = root / BOM_PROBES
    b = str(BOM_PROBES)
    if not bp.is_file():
        rep.error(b, "probe corpus is missing — check 0's detector is unproven")
        return
    seen = 0
    known = {"UTF-8-leading", "UTF-8-embedded"} | {lbl for _, lbl in BOM_SIGNATURES}
    for lineno, expectation, payload in _read_probe_rows(bp):
        labels = [w.split("@", 1)[0] for w in expectation.split(",") if w]
        if expectation != "CLEAN" and (not labels or any(l not in known for l in labels)):
            rep.error(
                b,
                f"line {lineno}: expectation must be CLEAN or a comma-separated "
                f"list of {sorted(known)} (UTF-8-embedded takes an @offset), "
                f"found {expectation!r}",
            )
            continue
        hexbytes = payload.split(None, 1)[0] if payload else ""
        try:
            data = bytes.fromhex(hexbytes)
        except ValueError:
            rep.error(b, f"line {lineno}: payload {hexbytes!r} is not valid hex")
            continue
        seen += 1
        # Probes are hex-encoded rather than committed as real files ON
        # PURPOSE: a fixture file carrying an actual BOM would be caught by
        # check 0 itself, and "never commit a BOM'd file" is the rule this
        # corpus exists to defend.
        want = [] if expectation == "CLEAN" else expectation.split(",")
        got = [
            lbl if lbl != "UTF-8-embedded" else f"UTF-8-embedded@{off}"
            for lbl, off in classify_boms(data)
        ]
        want_norm = [w for w in want if w]
        if got != want_norm:
            rep.error(
                b,
                f"line {lineno}: BOM classification drift for bytes {hexbytes} — "
                f"expected {want_norm or ['CLEAN']}, detector returned {got or ['CLEAN']}",
            )
    if seen == 0:
        rep.error(b, "probe corpus contains no probes")


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

# Order matters: `bom` runs FIRST so an invisible byte is named as the cause
# before a downstream parse error can misdirect the contributor.
CHECKS = [
    ("bom", "no byte-order mark on any shipped asset (runs first, by design)", check_bom),
    ("agent-frontmatter", "agents/*.md fleet standards (incl. fan-out contract)", check_agents),
    ("manifest", "commands/manifest.yaml <-> commands/*.md reconciliation", check_manifest),
    ("version-sync", "plugin.json / marketplace.json / CHANGELOG.md version agreement", check_version_sync),
    ("hooks", "hooks/hooks.json shape, scripts, duplicate-registration guard", check_hooks),
    # Named for what it actually does: a spot-check on two chosen literals, not
    # general prose-duplication detection. A green result here has been
    # over-read as "nothing in the repo is duplicated" — it never meant that.
    ("single-source-literals", "two owned literals from fan-out-policy.md are not restated uncited", check_single_source),
    ("reviewer-verdicts", "grumpy reviewers name all three verdict tokens in their own instruction", check_reviewer_verdicts),
    ("probe-corpus", "checks 0 and 7 detectors replayed against scripts/ci/fixtures/", check_probe_corpus),
]
SELF_TEST_CHECKS = {"probe-corpus"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Parliament of Chaos conformance gate")
    parser.add_argument("--list-checks", action="store_true", help="list check names and exit")
    parser.add_argument("--strict", action="store_true", help="treat WARN as failing")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run only the probe-corpus check: replay the committed defective and "
            "control probes in scripts/ci/fixtures/ against the live detectors. "
            "Also runs as part of a normal invocation"
        ),
    )
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
    selected = [c for c in CHECKS if not args.self_test or c[0] in SELF_TEST_CHECKS]
    for _, _, fn in selected:
        fn(root, rep)

    for severity, path, msg in rep.rows:
        print(f"{severity} {path}: {msg}")

    errors, warns = rep.count("ERROR"), rep.count("WARN")
    label = "self-test" if args.self_test else "conformance"
    print(f"{label}: {errors} error(s), {warns} warning(s)")
    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
