# [Item Name] Tasks

<!--
PURPOSE: Break the spec into actionable, assignable work units.
Each task should be completable in 1-3 days.
Update status daily during active development.
-->

## Progress

**Spec**: [Spec.md](./Spec.md)

**Status**: Not Started | In Progress | Blocked | Complete

**Progress**: 0 of 12 tasks complete

| Metric | Target | Current |
|--------|--------|---------|
| Start Date | YYYY-MM-DD | - |
| Target Complete | YYYY-MM-DD | - |
| Actual Complete | - | - |

---

## Task List

### Setup (Phase 1)

- [ ] **T-001**: Set up auth service project structure
  - Owner: @alice
  - Estimate: 2 hours
  - Notes: Use standard service template

- [ ] **T-002**: Configure Okta sandbox environment
  - Owner: @alice
  - Estimate: 4 hours
  - Depends on: Okta admin access (requested 2025-01-10)

- [ ] **T-003**: Add Redis session store configuration
  - Owner: @bob
  - Estimate: 3 hours
  - Notes: Use existing Redis cluster

### Implementation (Phase 2)

- [ ] **T-004**: Implement SAML authentication flow
  - Owner: @alice
  - Estimate: 1 day
  - Depends on: T-002
  - Acceptance: Can complete login via Okta sandbox

- [ ] **T-005**: Implement session management
  - Owner: @alice
  - Estimate: 4 hours
  - Depends on: T-003, T-004
  - Acceptance: Sessions stored in Redis with TTL

- [ ] **T-006**: Implement role-based access control
  - Owner: @bob
  - Estimate: 1 day
  - Depends on: T-004
  - Acceptance: Three roles enforced on API endpoints

- [ ] **T-007**: Add logout functionality
  - Owner: @alice
  - Estimate: 2 hours
  - Depends on: T-005

- [ ] **T-008**: Handle edge cases (expired session, Okta errors)
  - Owner: @alice
  - Estimate: 4 hours
  - Depends on: T-004, T-005

### Testing (Phase 3)

- [ ] **T-009**: Write unit tests for auth service
  - Owner: @bob
  - Estimate: 1 day
  - Coverage target: 80%

- [ ] **T-010**: Write integration tests with Okta sandbox
  - Owner: @alice
  - Estimate: 4 hours

- [ ] **T-011**: Security review and penetration testing
  - Owner: @security-team
  - Estimate: 2 days
  - Notes: Schedule with security team by Week 3

### Deployment (Phase 4)

- [ ] **T-012**: Deploy to staging and verify with production Okta
  - Owner: @alice
  - Estimate: 4 hours
  - Depends on: T-009, T-010, T-011

---

## Blocked Tasks

| Task | Blocker | Owner | Since | Action Needed |
|------|---------|-------|-------|---------------|
| T-002 | Awaiting Okta admin access | @admin | 2025-01-10 | Follow up with IT |

---

## Completed Tasks

_Move tasks here when done. Include completion date and any notes._

<!--
Example:
- [x] **T-001**: Set up auth service project structure
  - Completed: 2025-01-12
  - Owner: @alice
  - Notes: Used new Golang template, added to monorepo
-->

---

## Notes and Decisions

_Capture decisions made during implementation that affect the spec._

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |

---

**Related Documents**:
- [Spec](./Spec.md) — Requirements and design
- [Work Complete](./work_complete.md) — Final documentation
