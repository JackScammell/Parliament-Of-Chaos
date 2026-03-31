---
description: Assist with complex git operations — conflicts, cherry-picks, branch cleanup, bisect
effort: medium
---

# Git Workflow

Assist with complex git operations that developers frequently struggle with: merge conflict resolution, cherry-pick strategies, branch cleanup, and bisect-based debugging.

## Usage

```
/git-workflow <subcommand> [options]
```

**Examples**:
```
/git-workflow resolve-conflicts       # Guide through current merge conflicts
/git-workflow cherry-pick abc123      # Plan safe cherry-pick with dependency analysis
/git-workflow branch-cleanup          # Find and clean stale/merged branches
/git-workflow bisect "npm test"       # Find the commit that broke tests
```

## Subcommands

### `resolve-conflicts`
- Read all conflicted files
- Analyse both sides using git log context (who changed what and why)
- Suggest resolution for each conflict with rationale
- Apply resolutions and verify the result compiles/passes lint

### `cherry-pick <commit|range>`
- Analyse the target commit(s) and their dependencies
- Identify if any prerequisite commits need to come along
- Suggest the safe cherry-pick order
- Execute with conflict resolution guidance if needed

### `branch-cleanup`
- Find branches already merged into main
- Find stale branches (no commits in 30+ days)
- Show which branches are safe to delete
- Confirm before deleting, clean up both local and remote

### `bisect <test-command>`
- Set up `git bisect` with the provided test command
- Identify the good commit (last known working) and bad commit (current)
- Walk through the bisect process automatically
- Report the first bad commit with context (diff, author, message)

## Process

1. Detect the current git state (conflicts, branches, remotes)
2. Execute the requested subcommand
3. Explain each action and its rationale
4. Verify the result (clean state, passing tests, correct resolution)

## Notes

- `resolve-conflicts` reads both sides and commit history to understand intent — not just picking "ours" or "theirs"
- `branch-cleanup` always confirms before any deletion
- `bisect` requires a test command that exits 0 for pass and non-zero for fail
