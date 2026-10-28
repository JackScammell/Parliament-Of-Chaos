# Security Policy

Parliament of Chaos is a Claude Code plugin. Installing it runs the hook scripts under
`src/hooks/` and the agent and command definitions on your machine, so a vulnerability
here is a vulnerability on every machine that has the plugin enabled.

## Reporting a vulnerability

Please do not open a public issue for anything you believe is exploitable.

Use GitHub's private vulnerability reporting instead:
https://github.com/JackScammell/Parliament-Of-Chaos/security/advisories/new

Include the plugin version (`claude plugin list`), the Claude Code version
(`claude --version`), and the smallest reproduction you can manage. Reports are
read on a best-effort basis by a single maintainer; expect an acknowledgement within
a week.

## Supported versions

Only the latest release receives fixes. Pin to a tag if you need stability; release tags
cannot be moved or deleted once published.

## What the plugin does and does not do

- Hooks run with your user's permissions and only shell out to tools already on your
  `PATH`. They do not download or execute remote code.
- The CI gate runs with a read-only token and no secrets. See the comment at the top of
  `.github/workflows/gate.yml`.
- Agents and commands are prompt files. They ask Claude Code to act; they cannot bypass
  the permission mode you run Claude Code in.
