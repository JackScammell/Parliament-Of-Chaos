---
description: Generate convention-compliant boilerplate by reading existing project patterns
effort: medium
---

# Scaffold

Generate new files following the project's existing conventions. Reads your codebase to infer naming patterns, directory structure, imports, and code style, then produces consistent boilerplate.

## Usage

```
/scaffold <type> <name> [--path <directory>]
```

**Examples**:
```
/scaffold model User                 # New model following existing model patterns
/scaffold endpoint /api/invoices     # New API endpoint with route, controller, validation
/scaffold service PaymentService     # New service class
/scaffold test UserService           # New test file for an existing module
/scaffold feature billing            # Full feature: model + service + controller + test
/scaffold migration add_status_to_orders  # New migration file
/scaffold middleware RateLimit       # New middleware
/scaffold command SendReminders      # New CLI command
```

## Options

- `<type>`: What to generate — `model`, `endpoint`, `service`, `test`, `feature`, `migration`, `middleware`, `command`, `component`
- `<name>`: Name for the generated entity
- `--path` (optional): Target directory (auto-detected from project structure if omitted)

## Process

1. **Detect Stack**
   - Identify framework: Laravel, Django, Express, Rails, Spring, Next.js, etc.
   - Identify language conventions: naming case, file extensions, module system

2. **Read Existing Patterns**
   - Find the most recent examples of the requested type
   - Extract: file naming, directory placement, import patterns, class structure, error handling, documentation style
   - Identify barrel files, route registrations, or module indexes that need updating

3. **Generate Files**
   - Create new files matching extracted conventions exactly
   - Include appropriate imports, type annotations, and boilerplate
   - For `feature` type: generate the full vertical slice (model + migration + service + controller + route + test)

4. **Update Registrations**
   - Add routes to route files
   - Update barrel/index files
   - Register in dependency injection containers if applicable

5. **Format**
   - Run the project's formatter on generated files

## Output

```
Created:
  - app/Models/User.php
  - database/migrations/2026_03_31_create_users_table.php
  - app/Http/Controllers/UserController.php
  - tests/Feature/UserTest.php

Updated:
  - routes/api.php (added /users routes)
```

## Notes

- Never uses templates — always reads your actual code to infer conventions
- Supports any framework by pattern detection, not hardcoded templates
- For `feature` scaffolding, generates the minimal vertical slice needed
