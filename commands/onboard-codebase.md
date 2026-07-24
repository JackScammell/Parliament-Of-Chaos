---
description: Analyse an undocumented codebase and generate comprehensive getting-started documentation
effort: medium
context: fork
background: false
agent: senior-council
---

# Onboard Codebase

Generate comprehensive onboarding documentation for an undocumented codebase by running specialists in parallel.

## Purpose

When a developer joins a project with little or no documentation, this command reverse-engineers the codebase and produces a complete `docs/getting_started/` directory covering everything they need to get productive.

## Arguments

This command accepts optional arguments:

- No argument: Analyse the current working directory
- With path: Analyse a specific directory (e.g., `/onboard-codebase /path/to/project`)

## Pre-conditions

Before starting, verify:

1. **Target directory exists** and contains source code files
2. **Write access** to create `docs/getting_started/` in the target directory
3. **Existing documentation check**: If `docs/getting_started/` already exists, ask the user whether to:
   - Overwrite all files (start fresh)
   - Skip existing files and only generate missing ones
   - Archive existing to `docs/getting_started_backup_<date>/` and regenerate

## Process

### Phase 1: Parallel Analysis

Fan out the following specialists **in parallel** to analyse the codebase. Each specialist focuses on their domain and returns a structured analysis report. Do NOT ask them to write files — they analyse and report only.

**IMPORTANT: Inventory Header Requirement.** Every specialist MUST begin their report with a structured `## Inventory` section containing counts and a complexity self-assessment. This metadata drives adaptive document splitting in Phase 2. The format:

```markdown
## Inventory
- <item_type>: <count>
- <item_type>: <count>
- estimated_complexity: small | large | massive
- logical_groups:
  - <group_name>: <brief description> (<count> items)
  - <group_name>: <brief description> (<count> items)
```

Complexity thresholds (specialists MUST use these to self-assess):

| Specialist | Small | Large | Massive |
|---|---|---|---|
| data-warlock | <30 tables | 30-100 tables | 100+ tables |
| api-keeper | <50 endpoints | 50-200 endpoints | 200+ endpoints |
| config-curator | <30 env vars | 30-100 env vars | 100+ env vars |
| dependency-detective | <30 deps | 30-100 deps | 100+ deps |
| system-architect | <5 services/modules | 5-15 services/modules | 15+ services/modules |
| backend-goblin | <10 entry points/controllers | 10-40 entry points/controllers | 40+ entry points/controllers |
| test-prophet | <20 test files | 20-80 test files | 80+ test files |
| pipeline-engineer | <3 CI/CD configs | 3-10 CI/CD configs | 10+ CI/CD configs |
| security-knight | <5 auth/security layers | 5-15 auth/security layers | 15+ auth/security layers |
| observability-oracle | <5 logging/monitoring configs | 5-15 logging/monitoring configs | 15+ logging/monitoring configs |
| package-wizard | <3 build tool configs | 3-10 build tool configs | 10+ build tool configs |

The `logical_groups` field is critical — specialists MUST group their findings by domain/feature area (e.g., data-warlock groups tables by domain: "authentication", "billing", "products"). These groups become the natural split boundaries for documentation.

**Expected report structure for ALL specialists:**

```markdown
## Inventory
- <item_type>: <count>
- estimated_complexity: small | large | massive
- logical_groups:
  - <group_name>: <description> (<count> items)

## Findings

### <Logical Group 1 Name>
<Detailed analysis of this group — files, classes, patterns, relationships, config values, etc. Include real file paths, real names, real code references.>

### <Logical Group 2 Name>
<...>

## Key Patterns
<Cross-cutting patterns, conventions, or notable architectural decisions observed>

## Gaps & Concerns
<Anything missing, misconfigured, or notable — e.g., "no test coverage for billing module", "hardcoded secrets in config/app.php">
```

If a specialist finds **nothing in their domain** (e.g., no database, no tests), they should return a minimal report:

```markdown
## Inventory
- tables: 0
- estimated_complexity: small
- logical_groups: none

## Findings
No database schema, migrations, or ORM models detected in this codebase.

## Gaps & Concerns
This project has no database layer. If one is expected, it may not yet be implemented.
```

Launch ALL of these simultaneously:

1. **system-architect** — First, identify the primary language(s), framework(s), and package manager(s) (this context is available to all other specialists via their own codebase access). Then analyse overall architecture, components, boundaries, data flow, communication patterns. Map the high-level structure of the application. Group findings by bounded context or module.

2. **backend-goblin** — Analyse server-side code patterns, frameworks used, entry points, middleware, request lifecycle, code conventions, and common patterns throughout the codebase. Group findings by module or feature area.

3. **api-keeper** — Catalogue all API endpoints, routes, request/response shapes, authentication requirements, error formats. Map the full API surface. Group endpoints by resource/domain.

4. **data-warlock** — Analyse database schema, models, relationships, migrations, seeders, query patterns. Map the data layer completely. Group tables by domain using foreign key relationships and naming conventions. Classify each table into tiers:
   - **Tier 1** (core): Tables with many inbound foreign keys, corresponding application models — document fully (all columns, relationships, indexes, query patterns)
   - **Tier 2** (supporting): Tables with some relationships and business logic — document purpose, key columns, relationships
   - **Tier 3** (infrastructure): Pivot tables, framework tables (jobs, cache, sessions, telescope_*), audit logs — one-line description only

5. **config-curator** — Catalogue all configuration: env vars, config files, secrets references, feature flags, environment-specific settings. Document every config value needed to run the project. Group by service/feature area.

6. **test-prophet** — Analyse the test suite: frameworks used, how to run tests, coverage patterns, test organization, fixtures/factories.

7. **pipeline-engineer** — Analyse CI/CD configuration, build process, deployment targets, scripts, Dockerfiles, infrastructure-as-code.

8. **dependency-detective** — Analyse all dependencies: package managers, major libraries, their purposes, version constraints, any known issues. Group by category (framework, database, auth, testing, utilities, etc.).

9. **security-knight** — Analyse authentication, authorization, security middleware, CORS, rate limiting, input validation, security patterns.

10. **observability-oracle** — Analyse logging, monitoring, error tracking, health checks, metrics collection, alerting configuration.

11. **package-wizard** — Analyse package structure, build tools, scripts in package.json/Makefile/composer.json, development tools, linters, formatters.

### Phase 2: Documentation Generation

Once ALL specialist analyses are complete, invoke **doc-bard** to write the documentation files. Pass ALL specialist reports to doc-bard so it has the complete picture.

#### Step 2a: Build a Document Plan (MANDATORY)

Before writing ANY files, doc-bard MUST review the `## Inventory` headers from all specialist reports and build a document plan. For each section below, decide:

- **Single file** — if the specialist reported `estimated_complexity: small`. Write the section as one file (e.g., `database_guide.md`).
- **Subdirectory** — if the specialist reported `estimated_complexity: large` or `massive`. Create a subdirectory (e.g., `database/`) containing:
  - `index.md` — Overview, key patterns, navigation table linking to all sub-files
  - One file per logical group from the specialist's report (e.g., `database/core.md`, `database/billing.md`, `database/products.md`)
  - For `massive` complexity: also generate `appendix_all_items.md` with a complete one-line-per-item reference list

**Splitting rules:**
1. Split along the specialist's `logical_groups` boundaries — never split mechanically by alphabet or size alone
2. Aim for roughly 15-25 items per sub-file as a soft guideline (e.g., 15-25 tables, 15-25 endpoints). If a logical group exceeds this but the items are tightly coupled with no natural split boundary, keep the group intact — coherence takes priority over file size
3. For `massive` databases: Tier 1 tables get full documentation, Tier 2 get standard docs, Tier 3 get one-line descriptions collected into an appendix
4. Every sub-file must be self-contained and coherent — a developer reading just that file should understand that domain
5. The subdirectory `index.md` must include: overview, key patterns/conventions, schema statistics (counts), and a navigation table

**Example document plan for a large codebase:**
```
Document Plan:
- project_description.md          -> SINGLE FILE (small)
- project_setup.md                -> SINGLE FILE (small)
- architecture_overview.md        -> SINGLE FILE (small)
- directory_structure.md          -> SINGLE FILE (small)
- tech_stack.md                   -> SINGLE FILE (small)
- database/                       -> SUBDIRECTORY (large: 87 tables)
  - index.md                        (overview, ER diagram, navigation)
  - core.md                         (users, roles, permissions — 12 tables)
  - billing.md                      (plans, subscriptions, invoices — 18 tables)
  - products.md                     (products, categories, variants — 15 tables)
  - orders.md                       (orders, line_items, shipments — 14 tables)
  - notifications.md                (notifications, channels, templates — 8 tables)
  - appendix_all_tables.md          (complete 87-table reference list)
- api/                            -> SUBDIRECTORY (large: 156 endpoints)
  - index.md                        (overview, auth, errors, pagination)
  - users.md                        (user endpoints — 12 endpoints)
  - billing.md                      (billing endpoints — 24 endpoints)
  - ...
- configuration_reference.md      -> SINGLE FILE (small)
- testing_guide.md                -> SINGLE FILE (small)
- ...
```

**Adapting index.md:** The top-level `index.md` MUST link correctly based on the document plan. For single-file sections, link to the file. For subdirectory sections, link to the subdirectory's `index.md`:
```markdown
- [Database Guide](database/index.md)     <!-- split section -->
- [API Reference](api/index.md)           <!-- split section -->
- [Configuration](configuration_reference.md)  <!-- single file -->
```

#### Step 2b: Write Documentation Files

Following the document plan, doc-bard creates the following sections in `docs/getting_started/`. Each section is written as either a single file or a subdirectory depending on the plan from Step 2a:

#### 1. `index.md` — Getting Started Guide
- Quick-start steps (clone, install, configure, run — the absolute minimum to get running)
- Table of contents linking to all other docs in this directory
- Estimated time to get set up
- Prerequisites at a glance

#### 2. `project_description.md` — Project Description
- What the project is and what problem it solves
- Key features and capabilities
- Target users/audience
- Project status and maturity
- Links to any existing documentation found

*Source: system-architect analysis*

#### 3. `project_setup.md` — Project Setup
- System prerequisites (language versions, tools, databases, services)
- Step-by-step installation instructions
- Environment configuration (every env var documented with purpose, type, default, required/optional)
- Database setup (migrations, seeds)
- First run instructions
- Verification steps ("you know it's working when...")
- Common setup issues and fixes

*Source: config-curator + pipeline-engineer + data-warlock analyses*

#### 4. `architecture_overview.md` — Architecture Overview
- High-level architecture diagram (ASCII or Mermaid)
- Component breakdown with responsibilities
- Communication patterns (sync/async, events, queues)
- Data flow through the system
- External service dependencies
- Domain boundaries and bounded contexts

*Source: system-architect analysis*

#### 5. `directory_structure.md` — Directory Structure
- Annotated tree of the project directory
- Purpose of each top-level directory
- Key files and their roles
- Where to find things (routes, models, controllers, config, tests, etc.)
- Naming conventions used

*Source: system-architect + backend-goblin analyses*

#### 6. `tech_stack.md` — Technology Stack
- Languages and their versions
- Frameworks and libraries (with brief "why this was chosen" where apparent)
- Databases and data stores
- Build tools and task runners
- Development tools (linters, formatters, debuggers)
- Infrastructure and deployment tools

*Source: dependency-detective + package-wizard analyses*

#### 7. `api_reference.md` OR `api/` — API Reference
- API overview and base URL configuration
- Authentication requirements
- Endpoint catalogue grouped by domain/resource
- For each endpoint: method, path, description, request shape, response shape, status codes
- Common query parameters (pagination, filtering, sorting)
- Error response format
- Rate limiting details
- **If split:** One sub-file per resource group from api-keeper's logical_groups. The `api/index.md` contains overview, auth, error format, and navigation table.

*Source: api-keeper analysis*

#### 8. `database_guide.md` OR `database/` — Database Guide
- Database engine and version
- Schema overview with table descriptions
- Entity relationships (ASCII or Mermaid ER diagram)
- Key models and their responsibilities
- Migration workflow (how to create, run, rollback)
- Seeders and factories
- Common query patterns used in the codebase
- **If split:** One sub-file per domain cluster from data-warlock's logical_groups. Tier 1 tables get full column-level documentation. Tier 2 get standard docs. Tier 3 get one-line descriptions in an appendix. The `database/index.md` contains overview, ER diagram, migration workflow, statistics, and navigation table.

*Source: data-warlock analysis*

#### 9. `configuration_reference.md` OR `configuration/` — Configuration Reference
- Complete env var reference table: name, purpose, type, default, required, example
- Config file locations and their purposes
- Environment-specific configuration (dev vs staging vs prod)
- Secret management approach
- Feature flags (if any)
- How to add new configuration values
- **If split:** One sub-file per service/feature area from config-curator's logical_groups. The `configuration/index.md` contains overview, config hierarchy, and navigation table.

*Source: config-curator analysis*

#### 10. `testing_guide.md` — Testing Guide
- Test framework(s) used
- How to run the full test suite
- How to run specific test types (unit, integration, feature, e2e)
- Test directory structure and conventions
- How to write a new test (with example)
- Fixtures, factories, and test data
- Mocking and stubbing patterns
- CI test configuration

*Source: test-prophet analysis*

#### 11. `deployment_guide.md` — Deployment Guide
- Environments overview (dev, staging, production)
- CI/CD pipeline description
- Build process step-by-step
- Deployment process step-by-step
- Environment variables needed per environment
- Docker/container setup (if applicable)
- Infrastructure overview
- Rollback procedures

*Source: pipeline-engineer analysis*

#### 12. `key_dependencies.md` — Key Dependencies
- Major dependencies grouped by category (framework, database, auth, testing, etc.)
- For each: name, version, purpose in this project, documentation link
- Development-only dependencies
- Known version constraints or compatibility notes
- How to add/update/remove dependencies

*Source: dependency-detective + package-wizard analyses*

#### 13. `common_patterns.md` — Common Patterns & Conventions
- Code style and formatting rules
- Naming conventions (files, classes, functions, variables, routes)
- Architectural patterns used (MVC, repository, service layer, etc.)
- Error handling patterns
- Logging conventions
- Request lifecycle walkthrough
- Common abstractions and how to use them
- Example: "How to add a new [endpoint/page/feature]" walkthrough

*Source: backend-goblin + system-architect analyses*

#### 14. `security_overview.md` — Security Overview
- Authentication mechanism and flow
- Authorization model (roles, permissions, policies)
- Security middleware stack
- Input validation approach
- CORS configuration
- Rate limiting
- Known security considerations
- Security-related env vars

*Source: security-knight analysis*

#### 15. `observability_guide.md` — Observability Guide
- Logging: where logs go, log levels, how to add logging
- Error tracking: service used, how errors are reported
- Monitoring: health checks, metrics endpoints
- Debugging: how to debug locally, useful tools
- Performance profiling: available tools and approach

*Source: observability-oracle analysis*

#### 16. `troubleshooting.md` — Troubleshooting
- Common setup problems and solutions
- Frequent runtime errors and fixes
- Database connection issues
- Environment configuration mistakes
- Port conflicts and service dependencies
- "It works on my machine" scenarios
- Where to ask for help

*Source: All specialist analyses — common issues surfaced*

#### 17. `contributing.md` — Contributing Guide
- Development workflow (branch, develop, test, PR)
- Code review process (if detectable from CI config)
- Commit message conventions (if detectable from git history)
- PR template or checklist
- Code style enforcement (linters, formatters, pre-commit hooks)
- How to run checks locally before pushing

*Source: pipeline-engineer + backend-goblin + test-prophet analyses*

### Phase 3: Documentation Review

After doc-bard has written ALL files, invoke the following reviewers **in parallel**:

- **grumpy-documentation-pedant** — Primary reviewer for documentation quality, accuracy, and completeness
- **grumpy-standards-enforcer** — Verify documentation follows consistent conventions and formatting
- **grumpy-maintainability-curmudgeon** — Assess whether the documentation structure is maintainable long-term

The documentation pedant is the primary gate. The reviewers must collectively:

- Verify all file paths, function names, and code references are accurate
- Check for completeness — no sections left as TODO or placeholder
- Ensure consistency across all documents
- Flag any fabricated or unverifiable claims
- Check that setup instructions are actually followable
- Verify cross-references between documents are correct
- **For split sections:** Verify that subdirectory index.md files link to all sub-files correctly. Check that no items from the specialist's inventory are missing (every table documented, every endpoint listed). Verify sub-files are neither too granular (single-item files) nor too coarse (500+ line files). Confirm cross-references between documents point to correct paths (e.g., references to database tables link to the right sub-file, not a non-existent single file)

### Phase 4: Iteration

Route any issues from grumpy-documentation-pedant back to doc-bard for fixes. Re-review until approved. If specific technical claims cannot be verified, mark them with `[NEEDS VERIFICATION]` rather than removing them.

## Important Rules

1. **NEVER fabricate information.** Every file path, function name, endpoint, and config value MUST be verified against the actual codebase. If something cannot be determined, say so explicitly.
2. **Maximise parallelism.** All Phase 1 specialists MUST run in parallel, not sequentially.
3. **Be specific, not generic.** Documentation must reference THIS project's actual code, not generic best practices. Use real file paths, real class names, real endpoints.
4. **Include examples.** Every guide should include concrete examples from the actual codebase.
5. **Assume zero prior knowledge.** A developer with no context should be able to go from clone to running the app using only these docs.
6. **Skip what doesn't exist.** If the project has no database, skip `database_guide.md`. If there are no tests, note that in `testing_guide.md` and skip the detailed guide. Only produce docs for features that actually exist in the codebase. But DO document the absence of important things (e.g., "This project currently has no test suite").
7. **Respect complexity thresholds.** NEVER attempt to document a large schema, API surface, or config set in a single file. If a specialist reports `large` or `massive` complexity, the section MUST be split into a subdirectory. This is a hard rule, not a suggestion — single-file output for large sections will exceed context limits and produce incomplete documentation.
8. **Nothing gets missed.** For split sections, reconcile the final output against the specialist's inventory. Every item in the inventory must appear in at least one documentation file. If a table, endpoint, or config value was reported by a specialist but is missing from the docs, it must be added before the review phase completes.

## Error Handling

- **Empty or trivial codebase** (fewer than 5 source files): Inform the user that the project is too small for full onboarding documentation. Offer to generate a single `README.md` instead.
- **Specialist finds nothing**: The specialist returns a minimal "nothing found" report (see report structure above). doc-bard notes the absence in the relevant section or skips the file entirely per Rule 6.
- **Context limits during generation**: If a section is too large even after splitting, doc-bard should write what it can, mark incomplete sections with `[CONTINUED IN NEXT FILE]`, and create additional sub-files as needed. Never silently truncate.
- **Review cycle not converging**: If reviewers and doc-bard cannot agree after 3 iterations, present the remaining issues to the user and let them decide which to accept and which to fix manually.
- **Target directory is not a code project**: If no recognisable source files, package managers, or framework markers are found, inform the user and abort.

## Output

Present to the user:

1. **Files Generated** — List of all docs created with brief description of each
2. **Coverage Summary** — What was documented and what was skipped (and why)
3. **Confidence Notes** — Areas where documentation may need human verification
4. **Suggested Next Steps** — What the user should verify or add manually
