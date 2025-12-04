# Roadmap

<!--
PURPOSE: Sequence features into a timeline with clear milestones.
This is the single source of truth for "what happens when."
Update weekly or when priorities shift.
-->

## Current Status

**Last Updated**: YYYY-MM-DD

**Current Phase**: Phase 1 - Foundation

**Overall Progress**: 2 of 8 items complete

---

## Timeline Overview

```
Q1 2025                    Q2 2025                    Q3 2025
|--------------------------|--------------------------|
[Auth System    ]
        [Dashboard Builder          ]
                    [PDF Export ]
                           [Scheduled Reports    ]
                                      [API Access      ]
```

---

## Phases

### Phase 1: Foundation (Weeks 1-4)

_Goal: Core infrastructure and authentication_

| Item | Owner | Status | ETA |
|------|-------|--------|-----|
| [auth-system](./roadmap/auth-system/Spec.md) | @alice | Complete | Week 2 |
| [data-pipeline](./roadmap/data-pipeline/Spec.md) | @bob | In Progress | Week 4 |

**Milestone**: Users can log in and access sample data

---

### Phase 2: Core Features (Weeks 5-10)

_Goal: Primary user-facing functionality_

| Item | Owner | Status | ETA |
|------|-------|--------|-----|
| [dashboard-builder](./roadmap/dashboard-builder/Spec.md) | @carol | Planned | Week 8 |
| [widget-library](./roadmap/widget-library/Spec.md) | @dan | Planned | Week 7 |
| [sharing-permissions](./roadmap/sharing-permissions/Spec.md) | @alice | Planned | Week 10 |

**Milestone**: Users can build and share dashboards

---

### Phase 3: Polish (Weeks 11-14)

_Goal: Production readiness and user delight_

| Item | Owner | Status | ETA |
|------|-------|--------|-----|
| [pdf-export](./roadmap/pdf-export/Spec.md) | @eve | Backlog | Week 12 |
| [performance-optimization](./roadmap/performance-optimization/Spec.md) | @bob | Backlog | Week 13 |
| [user-onboarding](./roadmap/user-onboarding/Spec.md) | @carol | Backlog | Week 14 |

**Milestone**: Ready for public launch

---

## Dependencies Graph

```
auth-system
    |
    v
data-pipeline --> dashboard-builder --> pdf-export
                        |
                        v
                  widget-library
                        |
                        v
                sharing-permissions
```

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| SSO integration delays | High | Medium | Start integration early, have fallback auth |
| Performance at scale | High | Low | Load test at 2x expected volume |
| Scope creep | Medium | High | Strict change control, defer to v2 |

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-01-15 | Added pdf-export to Phase 3 | User research feedback |
| 2025-01-10 | Moved auth-system to Phase 1 | Dependency blocker |

---

**Related Documents**:
- [Project Outline](./project-outline.md) — Goals and constraints
- [Feature Implementation](./feature-implementation.md) — Feature details
