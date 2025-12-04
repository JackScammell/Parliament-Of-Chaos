# Project Outline

<!--
PURPOSE: Define the "why" and "what" of the project at the highest level.
This is the source of truth for project goals—everything else flows from here.
Update this document when project direction changes significantly.
-->

## Vision

_One paragraph describing what success looks like when the project is complete._

Example:
> A self-service analytics platform that enables marketing teams to build dashboards
> without engineering support, reducing report turnaround from 2 weeks to 2 hours.

## Problem Statement

_What pain point or opportunity does this project address?_

- Who experiences this problem?
- How are they currently solving it (or failing to)?
- What's the cost of not solving it?

## Goals

_Measurable outcomes that define project success._

| Goal | Metric | Target |
|------|--------|--------|
| Reduce support tickets | Tickets/week | < 10 |
| Increase adoption | Active users | 500+ |
| Improve performance | P95 latency | < 200ms |

## Non-Goals

_Explicitly state what this project will NOT do. This prevents scope creep._

- Will not replace the existing admin dashboard
- Will not support real-time streaming data (batch only for v1)
- Will not include mobile apps

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Sponsor | [Name] | Budget, final decisions |
| Lead | [Name] | Day-to-day ownership |
| Contributors | [Names] | Implementation |
| Reviewers | [Names] | Feedback and approval |

## Constraints

_Technical, timeline, budget, or regulatory constraints that shape the solution._

- Must integrate with existing SSO (Okta)
- Budget: $50k for infrastructure
- Deadline: Q2 launch for conference demo
- Must comply with GDPR for EU users

## Success Criteria

_How will we know when we're done?_

- [ ] All goals meet their target metrics
- [ ] Documentation complete and reviewed
- [ ] Stakeholder sign-off received
- [ ] Monitoring and alerting in place

---

**Related Documents**:
- [Feature Implementation](./feature-implementation.md) — Detailed breakdown of features
- [Roadmap](./Roadmap.md) — Timeline and sequencing
