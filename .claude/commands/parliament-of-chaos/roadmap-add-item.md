# Roadmap Add Item

Add a new item to an existing phase in the project roadmap without re-running `/plan-project`.

## Purpose

Quickly extend a project's roadmap with a new item. This is the lightweight path to add features, agents, commands, or other work items to an existing project.

## Arguments

**Required**:
- `<item-name>` - Kebab-case identifier (e.g., `cache-keeper`, `cmd-export-report`)
- `--phase <n>` - Phase number to add the item to (1, 2, 3, etc.)

**Optional**:
- `--depends <items>` - Comma-separated list of dependency item names

## Examples

```
/roadmap-add-item cache-keeper --phase 1
/roadmap-add-item grumpy-ux-critic --phase 2
/roadmap-add-item cmd-export-report --phase 3 --depends review-report-export
```

## Pre-conditions

- `.project-files/Roadmap.md` must exist (run `/plan-project` first)
- The specified phase must already exist in the roadmap
- The item name must not already exist in any phase

## Agent

**Delegated to: scope-weaver**

## Instructions

1. **Parse and validate arguments**:
   - Extract item-name, phase number, and optional dependencies
   - Validate item-name is kebab-case: `^[a-z][a-z0-9-]*[a-z0-9]$`
   - If validation fails, explain the requirement

2. **Validate roadmap state**:
   - Read `.project-files/Roadmap.md`
   - Verify the specified phase section exists (e.g., "### Phase 1:")
   - Verify item name is unique across ALL phases
   - If dependencies specified, verify each dependency exists in the roadmap

3. **Modify Roadmap.md** (SINGLE FILE ONLY):
   - Find the table in the specified phase section
   - Append new row: `| [item-name](./roadmap/item-name/) | Not Started | <deps or None> |`
   - Update the "Overall Progress" count in the Current Status section

4. **Report success**:
   - Confirm item was added to Phase N
   - Show the new table row
   - Suggest next step: `/roadmap-item-scope <item-name>`

## Error Handling

| Condition | Response |
|-----------|----------|
| No `.project-files/Roadmap.md` | "No roadmap found. Run `/plan-project` first to create your project." |
| Phase not found | "Phase {n} not found in Roadmap.md. Available phases: [list phase numbers and names]" |
| Item already exists | "Item '{name}' already exists in Phase {n}. To scope it, run `/roadmap-item-scope {name}`" |
| Invalid item name | "Item name must be kebab-case (lowercase letters, numbers, hyphens). Example: 'my-new-feature'" |
| Dependency not found | "Dependency '{dep}' not found in roadmap. Available items: [list]" |

## What This Command Does NOT Do

- **Create folders** - Deferred to `/roadmap-item-scope`
- **Create Spec.md or tasks.md** - Deferred to `/roadmap-item-scope`
- **Update feature-implementation.md** - Update manually if needed
- **Update dependency graph** - The ASCII graph is informational; update manually if needed

## Workflow Integration

```
/plan-project                    # Creates initial Roadmap.md
    ↓
/roadmap-add-item <name> --phase N   # Adds item to roadmap (THIS COMMAND)
    ↓
/roadmap-item-scope <name>       # Creates Spec.md and tasks.md
    ↓
/implement-task-list <name>      # Executes the tasks
```

## Example Output

```
Added to Roadmap.md, Phase 1 (New Specialist Agents):

| [cache-keeper](./roadmap/cache-keeper/) | Not Started | None |

Updated overall progress: 0 of 17 items

Next step: Run `/roadmap-item-scope cache-keeper` to create the specification and task list.
```
