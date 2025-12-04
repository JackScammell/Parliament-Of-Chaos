# Safe Progress Assurance Mechanism

A resilience mechanism for AI-driven planning systems that prevents regressions and ensures new work does not break completed features.

## Overview

Safe Progress Assurance (SPA) is a pre-flight check system that runs before any new roadmap item begins. It scans all `work_complete.md` files, builds a dependency graph, and cross-checks proposed changes against established contracts.

---

## 1. Structure of `work_complete.md`

Each completed roadmap item must produce a `work_complete.md` file with machine-parseable sections.

### File Location

```
.project-files/roadmap/{item-id}/work_complete.md
```

### Required Sections

```markdown
# Work Complete: {item-id}

## Metadata
- **ID**: feature-auth-001
- **Title**: User Authentication System
- **Completed**: 2025-01-15
- **Status**: COMPLETE
- **Depends On**: [feature-users-001, feature-database-001]
- **Depended On By**: [] <!-- Populated by downstream items -->

## Contracts Established

### Files Owned
<!-- Files this feature created or significantly modified -->
- src/auth/AuthService.php
- src/auth/TokenManager.php
- config/auth.php
- database/migrations/2025_01_15_create_auth_tokens_table.php

### Public Interfaces
<!-- Interfaces other code may depend on -->
```yaml
- interface: AuthServiceInterface
  file: src/auth/AuthServiceInterface.php
  methods:
    - name: authenticate
      signature: "authenticate(string $email, string $password): ?User"
      stability: STABLE
    - name: validateToken
      signature: "validateToken(string $token): ?TokenPayload"
      stability: STABLE
```

### Database Schema
<!-- Tables and columns this feature owns -->
```yaml
- table: auth_tokens
  columns: [id, user_id, token, expires_at, created_at]
  constraints:
    - foreign_key: user_id -> users.id
```

### Configuration Keys
<!-- Config values this feature depends on or introduces -->
```yaml
- key: auth.token_ttl
  type: integer
  default: 3600
  required: true
- key: auth.refresh_enabled
  type: boolean
  default: true
```

### API Endpoints
<!-- Routes this feature exposes -->
```yaml
- method: POST
  path: /api/v1/auth/login
  request_schema: LoginRequest
  response_schema: TokenResponse
  stability: STABLE
- method: POST
  path: /api/v1/auth/refresh
  stability: STABLE
```

### Events Published
<!-- Events other features may listen to -->
```yaml
- event: UserAuthenticated
  payload: {user_id: int, timestamp: datetime}
- event: TokenRefreshed
  payload: {user_id: int, old_token: string, new_token: string}
```

### Events Consumed
<!-- Events this feature listens to -->
```yaml
- event: UserDeleted
  handler: RevokeUserTokensListener
  action: "Revokes all tokens for deleted user"
```

## Invariants

<!-- Conditions that must remain true for this feature to work -->
1. The `users` table must have an `id` and `email` column
2. The `auth_tokens` table must exist with the schema above
3. `AuthServiceInterface::authenticate()` must return null on failure, never throw
4. Token TTL must be configurable via `auth.token_ttl`
5. All tokens must be revoked when a user is deleted

## Regression Tests

<!-- Tests that verify this feature works -->
```yaml
- test: Tests\Auth\AuthServiceTest::test_authenticate_returns_user_on_valid_credentials
  criticality: HIGH
- test: Tests\Auth\AuthServiceTest::test_authenticate_returns_null_on_invalid_password
  criticality: HIGH
- test: Tests\Auth\TokenManagerTest::test_token_expires_after_ttl
  criticality: MEDIUM
- test: Tests\Integration\AuthFlowTest::test_full_login_refresh_logout_cycle
  criticality: HIGH
```

## Breaking Change Triggers

<!-- Changes that would break this feature -->
1. Removing or renaming `users.id` or `users.email` columns
2. Changing `AuthServiceInterface::authenticate()` signature
3. Removing `auth.token_ttl` configuration
4. Dropping `auth_tokens` table
5. Changing `UserDeleted` event structure
```

---

## 2. Information Captured for Regression Detection

The `work_complete.md` structure captures these categories:

| Category | Purpose | Regression Risk |
|----------|---------|-----------------|
| **Files Owned** | Detect modification conflicts | HIGH - Direct file changes |
| **Public Interfaces** | API contract enforcement | CRITICAL - Signature changes break consumers |
| **Database Schema** | Schema migration conflicts | HIGH - Data integrity |
| **Configuration Keys** | Config dependency tracking | MEDIUM - Missing config crashes |
| **API Endpoints** | REST contract enforcement | HIGH - Client breakage |
| **Events Published** | Event contract enforcement | HIGH - Downstream handlers break |
| **Events Consumed** | Upstream dependency tracking | MEDIUM - Missing handlers |
| **Invariants** | Business rule enforcement | CRITICAL - Logic corruption |
| **Regression Tests** | Verification coverage | HIGH - Undetected breaks |
| **Breaking Change Triggers** | Explicit danger zones | CRITICAL - Known failure points |

---

## 3. Cross-Check Algorithm

### Phase 1: Discovery

```
FUNCTION discover_completed_work():
    completed_items = []
    FOR each directory in .project-files/roadmap/*/:
        IF exists(directory/work_complete.md):
            item = parse_work_complete(directory/work_complete.md)
            completed_items.append(item)
    RETURN completed_items
```

### Phase 2: Dependency Graph Construction

```
FUNCTION build_dependency_graph(completed_items):
    graph = DirectedGraph()

    FOR each item in completed_items:
        graph.add_node(item.id, item)
        FOR each dependency in item.depends_on:
            graph.add_edge(dependency -> item.id)

    // Detect cycles (invalid state)
    IF graph.has_cycle():
        RAISE DependencyCycleError

    RETURN graph
```

### Phase 3: Conflict Detection

```
FUNCTION check_conflicts(new_item_spec, completed_items):
    conflicts = []

    FOR each completed in completed_items:
        // Check file ownership conflicts
        FOR each file in new_item_spec.files_to_modify:
            IF file IN completed.files_owned:
                conflicts.append(FileOwnershipConflict(
                    file=file,
                    owner=completed.id,
                    severity=HIGH
                ))

        // Check interface contract violations
        FOR each interface_change in new_item_spec.interface_changes:
            IF interface_change.interface IN completed.public_interfaces:
                existing = completed.public_interfaces[interface_change.interface]
                IF NOT is_backward_compatible(existing, interface_change):
                    conflicts.append(ContractViolation(
                        interface=interface_change.interface,
                        breaking_change=describe_break(existing, interface_change),
                        affected_feature=completed.id,
                        severity=CRITICAL
                    ))

        // Check database schema conflicts
        FOR each migration in new_item_spec.migrations:
            FOR each schema in completed.database_schema:
                IF migration.affects_table(schema.table):
                    IF migration.drops_column(schema.columns):
                        conflicts.append(SchemaConflict(...))
                    IF migration.breaks_constraint(schema.constraints):
                        conflicts.append(SchemaConflict(...))

        // Check invariant violations
        FOR each invariant in completed.invariants:
            IF new_item_spec.would_violate(invariant):
                conflicts.append(InvariantViolation(
                    invariant=invariant,
                    feature=completed.id,
                    severity=CRITICAL
                ))

        // Check breaking change triggers
        FOR each trigger in completed.breaking_change_triggers:
            IF new_item_spec.matches_trigger(trigger):
                conflicts.append(KnownBreakingChange(
                    trigger=trigger,
                    feature=completed.id,
                    severity=CRITICAL
                ))

    RETURN conflicts
```

### Phase 4: Dependency Validation

```
FUNCTION validate_dependencies(new_item_spec, dependency_graph):
    issues = []

    FOR each required_dep in new_item_spec.depends_on:
        IF required_dep NOT IN dependency_graph.nodes:
            issues.append(MissingDependency(
                required=required_dep,
                status="NOT_COMPLETED"
            ))
        ELSE:
            dep_node = dependency_graph.get_node(required_dep)
            IF dep_node.status != "COMPLETE":
                issues.append(IncompleteDependency(
                    required=required_dep,
                    current_status=dep_node.status
                ))

    // Check for implicit dependencies
    FOR each file in new_item_spec.files_to_read:
        owner = find_file_owner(file, dependency_graph)
        IF owner AND owner NOT IN new_item_spec.depends_on:
            issues.append(ImplicitDependency(
                file=file,
                owner=owner,
                recommendation="Add to depends_on or ensure compatibility"
            ))

    RETURN issues
```

### Phase 5: Regression Test Mapping

```
FUNCTION identify_regression_tests(new_item_spec, completed_items):
    tests_to_run = []

    FOR each completed in completed_items:
        risk_score = calculate_risk_score(new_item_spec, completed)

        IF risk_score > 0:
            FOR each test in completed.regression_tests:
                tests_to_run.append(RegressionTest(
                    test=test.test,
                    reason=f"Changes may affect {completed.id}",
                    criticality=test.criticality,
                    risk_score=risk_score
                ))

    // Sort by criticality and risk
    RETURN sorted(tests_to_run, key=lambda t: (t.criticality, t.risk_score))

FUNCTION calculate_risk_score(new_spec, completed):
    score = 0

    // File overlap
    file_overlap = intersection(new_spec.files_touched, completed.files_owned)
    score += len(file_overlap) * 10

    // Interface usage
    IF new_spec.uses_interfaces(completed.public_interfaces):
        score += 20

    // Event coupling
    IF new_spec.publishes_events(completed.events_consumed):
        score += 15
    IF new_spec.consumes_events(completed.events_published):
        score += 15

    // Schema overlap
    IF new_spec.touches_tables(completed.database_schema):
        score += 25

    RETURN score
```

---

## 4. Conflict Resolution Protocol

When a conflict is detected, the system follows this protocol:

### Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| **CRITICAL** | Will definitely break existing functionality | BLOCK - Cannot proceed |
| **HIGH** | Likely to cause issues | WARN - Require explicit acknowledgment |
| **MEDIUM** | Potential for issues | INFORM - Note in work log |
| **LOW** | Minor concerns | LOG - Record for audit |

### Resolution Actions

#### For CRITICAL Conflicts

```markdown
## BLOCKED: Safe Progress Check Failed

### Critical Conflicts Detected

1. **Contract Violation** in `AuthServiceInterface`
   - **Affected Feature**: feature-auth-001
   - **Issue**: Proposed change removes `validateToken()` method
   - **Impact**: All token validation will fail

### Required Resolution

Choose one of:
1. **Modify Approach**: Change implementation to preserve the interface
2. **Coordinated Migration**: Create migration plan that updates all consumers
3. **Deprecation Path**: Add new method, deprecate old, migrate consumers, then remove

### Cannot Proceed Until Resolved
```

#### For HIGH Conflicts

```markdown
## WARNING: Potential Regression Risk

### High-Risk Changes Detected

1. **File Ownership Overlap**: `src/auth/AuthService.php`
   - **Owner**: feature-auth-001
   - **Risk**: Modifications may break authentication flow

### Required Acknowledgment

To proceed, add to your work spec:
```yaml
acknowledged_risks:
  - conflict: file_ownership_auth_service
    mitigation: "Will only add new private methods, no changes to public interface"
    reviewed_by: [architect, security]
```

### Regression Tests Required
- [ ] Tests\Auth\AuthServiceTest (all)
- [ ] Tests\Integration\AuthFlowTest (all)
```

#### For MEDIUM/LOW Conflicts

```markdown
## INFO: Compatibility Notes

### Considerations for This Work Item

1. **Implicit Dependency**: Your feature reads from `users` table
   - **Managed By**: feature-users-001
   - **Recommendation**: Add explicit dependency or document assumption

### Logged for Reference
These items have been recorded in the work log for audit purposes.
```

### Conflict Resolution Workflow

```
FUNCTION resolve_conflicts(conflicts):
    critical = filter(conflicts, severity=CRITICAL)
    high = filter(conflicts, severity=HIGH)

    IF critical:
        // Cannot proceed - require redesign
        present_blocking_conflicts(critical)
        request_resolution_plan()
        RETURN BLOCKED

    IF high:
        // Can proceed with acknowledgment
        present_warnings(high)
        acknowledgments = request_acknowledgments(high)

        IF NOT all_acknowledged(acknowledgments):
            RETURN BLOCKED

        record_acknowledged_risks(acknowledgments)

    // Medium/Low - inform and proceed
    log_compatibility_notes(conflicts)

    RETURN PROCEED_WITH_CAUTION
```

---

## 5. Dependency Management

### Explicit Dependencies

Defined in the roadmap item specification:

```yaml
# .project-files/roadmap/feature-payments-001/spec.yaml
id: feature-payments-001
title: Payment Processing
depends_on:
  - feature-auth-001      # Need authenticated users
  - feature-users-001     # Need user records
  - feature-orders-001    # Need order system
```

### Implicit Dependency Detection

The system detects implicit dependencies by analyzing:

1. **File Imports**: What modules does the new code import?
2. **Database Access**: What tables does it read/write?
3. **Event Subscriptions**: What events does it listen to?
4. **API Calls**: What internal APIs does it invoke?

```
FUNCTION detect_implicit_dependencies(new_spec, completed_items):
    implicit = []

    // Analyze planned code for imports
    FOR each file in new_spec.planned_files:
        imports = extract_imports(file)
        FOR each import in imports:
            owner = find_owner_of(import, completed_items)
            IF owner AND owner NOT IN new_spec.depends_on:
                implicit.append(ImplicitDependency(
                    type="import",
                    target=import,
                    owner=owner
                ))

    RETURN implicit
```

### Dependency Graph Visualization

```
feature-database-001
        |
        v
feature-users-001
        |
        +------------------+
        |                  |
        v                  v
feature-auth-001    feature-profiles-001
        |
        v
feature-payments-001 (NEW - being checked)
```

### Circular Dependency Prevention

```
FUNCTION check_circular_dependencies(new_spec, graph):
    // Temporarily add new item to graph
    test_graph = graph.copy()
    test_graph.add_node(new_spec.id)

    FOR each dep in new_spec.depends_on:
        test_graph.add_edge(dep -> new_spec.id)

    // Check for cycles
    cycles = test_graph.find_cycles()

    IF cycles:
        RAISE CircularDependencyError(
            message="Adding this item would create a dependency cycle",
            cycle=cycles[0],
            recommendation="Review dependency declarations"
        )
```

---

## 6. Implementation: Pre-Flight Check Command

### Command: `/safe-progress-check`

```markdown
# Safe Progress Check

Validates that a new roadmap item can proceed without breaking existing work.

## Usage

```
/safe-progress-check {item-id}
```

## Process

1. Load item specification from `.project-files/roadmap/{item-id}/spec.yaml`
2. Discover all completed work in `.project-files/roadmap/*/work_complete.md`
3. Build dependency graph
4. Run conflict detection
5. Identify required regression tests
6. Present findings with recommended action

## Output

### If Safe to Proceed

```
SAFE PROGRESS CHECK: PASSED

Item: feature-payments-001
Dependencies: 3 satisfied, 0 missing
Conflicts: 0 critical, 0 high, 2 medium
Regression Tests: 12 tests mapped (run before completion)

Proceed with implementation.
```

### If Blocked

```
SAFE PROGRESS CHECK: BLOCKED

Item: feature-payments-001

CRITICAL CONFLICTS (must resolve):
1. Contract violation: UserService.getUser() signature change
   - Affected: feature-auth-001, feature-profiles-001
   - Resolution required before proceeding

See detailed report: .project-files/roadmap/feature-payments-001/preflight-report.md
```
```

---

## 7. Integration with Parliament of Chaos

### Senior Council Integration

The Senior Council should invoke Safe Progress Assurance before delegating work:

```markdown
## Senior Council Pre-Work Protocol

Before delegating a roadmap item to specialists:

1. **Run Safe Progress Check**
   - Invoke: `/safe-progress-check {item-id}`
   - If BLOCKED: Present conflicts to user, request resolution
   - If PROCEED_WITH_CAUTION: Brief specialists on acknowledged risks

2. **Brief Specialists on Constraints**
   - Files owned by other features (do not modify without coordination)
   - Interfaces that must be preserved
   - Events that must maintain their contracts
   - Regression tests that must pass

3. **Post-Work Validation**
   - Run all mapped regression tests
   - Verify no invariants were violated
   - Update dependency graph
```

### Resilience Tamer Role

The Resilience Tamer agent should review:
- Failure modes introduced by new dependencies
- Circuit breaker placement for new external calls
- Fallback strategies when dependent features fail
- Timeout configurations for cross-feature calls

---

## 8. Failure Scenarios and Recovery

### Scenario: Stale `work_complete.md`

**Problem**: A `work_complete.md` file is outdated and doesn't reflect recent changes.

**Detection**:
- File checksums don't match recorded values
- Tests listed in regression tests no longer exist
- Interfaces defined don't match actual code

**Recovery**:
```
FUNCTION validate_work_complete(item):
    issues = []

    // Check file ownership still valid
    FOR each file in item.files_owned:
        IF NOT exists(file):
            issues.append(StaleFileReference(file))
        ELIF get_checksum(file) != item.file_checksums[file]:
            issues.append(UnrecordedModification(file))

    // Check interfaces still exist
    FOR each interface in item.public_interfaces:
        IF NOT interface_exists(interface):
            issues.append(MissingInterface(interface))

    IF issues:
        flag_for_review(item, issues)
        RETURN STALE

    RETURN VALID
```

### Scenario: Missing `work_complete.md`

**Problem**: A feature was completed but no `work_complete.md` was created.

**Detection**: Directory exists with implementation but no completion record.

**Recovery**: Generate from analysis:
```
FUNCTION generate_work_complete(item_directory):
    spec = load(item_directory/spec.yaml)

    // Analyze implemented code
    files = scan_directory(item_directory)
    interfaces = extract_interfaces(files)
    schema = extract_migrations(files)
    events = extract_events(files)
    tests = find_related_tests(spec.id)

    // Generate work_complete.md
    work_complete = WorkComplete(
        id=spec.id,
        files_owned=files,
        public_interfaces=interfaces,
        database_schema=schema,
        events=events,
        regression_tests=tests,
        invariants=[] // Requires manual input
    )

    // Flag for human review
    work_complete.status = "GENERATED_NEEDS_REVIEW"

    write(item_directory/work_complete.md, work_complete)
```

### Scenario: Conflict Detected After Work Started

**Problem**: A conflict was missed or emerged during implementation.

**Detection**: Mid-implementation check or failing regression tests.

**Recovery**:
```
FUNCTION handle_mid_work_conflict(item, conflict):
    // Stop further implementation
    pause_work(item)

    // Assess damage
    changes_made = get_changes_since_start(item)
    affected_features = identify_affected(changes_made, conflict)

    // Options
    IF can_rollback(changes_made):
        option_1 = RollbackOption(
            action="Revert all changes, redesign approach",
            risk="LOW",
            effort="MEDIUM"
        )

    IF can_isolate(conflict):
        option_2 = IsolationOption(
            action="Isolate conflicting change behind feature flag",
            risk="MEDIUM",
            effort="LOW"
        )

    option_3 = CoordinatedFixOption(
        action="Fix conflict and update all affected features",
        risk="HIGH",
        effort="HIGH"
    )

    present_options([option_1, option_2, option_3])
```

---

## 9. Metrics and Monitoring

### Track These Metrics

| Metric | Purpose | Alert Threshold |
|--------|---------|-----------------|
| Conflicts per item | Trend of integration issues | > 3 critical/month |
| Resolution time | How long conflicts take to resolve | > 2 days average |
| Stale records | work_complete.md accuracy | > 10% stale |
| Regression test coverage | Features with mapped tests | < 80% coverage |
| Dependency depth | Complexity of dependency chains | > 5 levels deep |

### Audit Log

Every safe progress check should be logged:

```yaml
# .project-files/audit/safe-progress-checks.yaml
- timestamp: 2025-01-20T14:30:00Z
  item: feature-payments-001
  result: PROCEED_WITH_CAUTION
  conflicts:
    critical: 0
    high: 1
    medium: 2
  acknowledged_by: developer@example.com
  regression_tests_mapped: 12
```

---

## 10. Summary

Safe Progress Assurance provides:

1. **Structured Completion Records**: `work_complete.md` files capture contracts, dependencies, and invariants
2. **Automated Cross-Checking**: Algorithm detects file, interface, schema, and event conflicts
3. **Clear Resolution Protocols**: Severity-based handling with concrete resolution paths
4. **Dependency Management**: Explicit and implicit dependency tracking with cycle detection
5. **Integration Points**: Hooks into the Parliament of Chaos workflow

The mechanism is intentionally conservative - it prefers false positives (blocking safe changes) over false negatives (allowing breaking changes). Teams can tune the sensitivity based on their risk tolerance.
