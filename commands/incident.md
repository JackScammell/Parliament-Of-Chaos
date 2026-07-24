---
description: Structured incident triage, hotfix coordination, and postmortem generation
effort: high
context: fork
background: false
agent: senior-council
---

# Incident

Guide structured incident response: severity classification, blast radius assessment, hotfix coordination, and postmortem template generation.

## Usage

```
/incident [--severity <level>] [--postmortem] [--runbook <service>]
```

**Examples**:
```
/incident                            # Start triage for a new incident
/incident --severity critical        # Skip triage, start critical response
/incident --postmortem               # Generate postmortem from recent incident
/incident --runbook payment-service  # Generate runbook for a service
```

## Options

- `--severity` (optional): Skip triage and start at a known severity — `critical`, `high`, `medium`, `low`
- `--postmortem` (optional): Generate a postmortem template from recent git activity and session logs
- `--runbook` (optional): Generate a runbook for a specific service by analysing its dependencies and failure modes

## Process

### Triage Mode (default)

1. **Classify Severity**
   - Ask: what is broken, who is affected, is data at risk?
   - Assign severity based on blast radius and data impact

2. **Identify Affected Systems**
   - Analyse recent changes (`git log --since` recent deploys)
   - Map dependencies of affected components
   - Identify potential root causes from recent commits

3. **Coordinate Hotfix**
   - Create hotfix branch
   - Scope minimal-risk patch (smallest change that fixes the issue)
   - Run targeted tests on the fix
   - Generate expedited review checklist (security + correctness only)

4. **Draft Communications**
   - Status page update template
   - Stakeholder notification template
   - Resolution confirmation template

### Postmortem Mode (`--postmortem`)

1. Analyse git history around the incident timeframe
2. Build timeline: what changed, when, by whom
3. Generate structured postmortem: summary, timeline, root cause, impact, action items
4. Include 5-whys analysis template

### Runbook Mode (`--runbook <service>`)

1. Analyse service code for dependencies (databases, APIs, queues, caches)
2. Identify health check endpoints
3. Generate restart/recovery procedures
4. Document common failure modes and diagnostic commands

## Output

Structured markdown with severity, timeline, affected systems, fix plan, and communication templates.

## Notes

- Triage mode is interactive — asks questions to classify severity
- Postmortem mode reads git history; it cannot access monitoring systems
- Runbook generation analyses code structure, not live infrastructure
