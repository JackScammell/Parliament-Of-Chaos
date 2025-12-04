# Roadmap Item Scope

You are scoping a specific roadmap item using the **scope-weaver** agent.

## Agent

**Delegated to: scope-weaver**

## Purpose

Create a detailed specification and task breakdown for a roadmap item, enabling systematic implementation.

## Arguments

**Required**: `<item-name>` - The name of the roadmap item to scope (should match an item in Roadmap.md)

Example:
- `/roadmap-item-scope user-authentication`
- `/roadmap-item-scope api-integration`

## Instructions

1. **Validate the item exists**:
   - Read `.project-files/Roadmap.md`
   - Find the specified item
   - If not found, list available items and ask user to choose

2. **Check for existing scope**:
   - Look for `.project-files/roadmap/<item>/`
   - If Spec.md exists, ask if user wants to:
     - View existing scope
     - Re-scope (will archive existing)
   - If work_complete.md exists, warn that this item is already done

3. **Cross-reference previous work**:
   - Read all `.project-files/roadmap/*/work_complete.md` files
   - Identify any overlap or dependencies
   - Report findings to user

4. **Invoke scope-weaver agent** to create:
   - `.project-files/roadmap/<item>/Spec.md` - Detailed specification
   - `.project-files/roadmap/<item>/tasks.md` - Actionable task list

5. **Report summary**:
   - Number of tasks created
   - Estimated complexity
   - Dependencies identified
   - Next step: `/implement-task-list <item>`

## Output Structure

```
.project-files/
  roadmap/
    <item-name>/
      Spec.md      # Detailed requirements and technical approach
      tasks.md     # Actionable implementation checklist
```

## Pre-conditions

- `.project-files/Roadmap.md` must exist (run `/plan-project` first)
- The specified item must be listed in the roadmap

## Error Handling

- **No Roadmap.md**: Suggest running `/plan-project` first
- **Item not found**: List available items from Roadmap.md
- **Already scoped**: Offer to view, update, or re-scope
- **Already complete**: Warn but allow re-scoping if requested
