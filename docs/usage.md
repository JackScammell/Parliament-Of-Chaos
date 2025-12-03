# Usage Guide

This guide explains how to use Parliament of Chaos commands effectively.

## Commands Overview

| Command | Purpose | Best For |
|---------|---------|----------|
| `/summon-council` | Full multi-agent review and development | Complex tasks, new features, architectural decisions |
| `/summon-grumpy-reviewer` | Quick critical code review | Code review, PR feedback, refactoring validation |

---

## /summon-council

The Senior Council orchestrates multiple specialist agents and grumpy reviewers to tackle complex tasks.

### When to Use

- Designing new features or systems
- Refactoring complex code
- Making architectural decisions
- Tasks spanning multiple domains (backend, security, testing, etc.)
- When you want thorough, multi-perspective review

### How It Works

1. **Task Analysis** - The council restates your goal and identifies relevant domains
2. **Agent Selection** - Appropriate specialists are chosen based on the task
3. **Specialist Work** - Each agent contributes from their domain expertise
4. **Grumpy Review** - All outputs go through the panel of critical reviewers
5. **Iteration** - Feedback is routed back to specialists until reviewers approve
6. **Synthesis** - Final solution is presented with trade-offs documented

### Example Usage

```
/summon-council

Design an authentication system for our Laravel API. It needs to support:
- JWT tokens for mobile clients
- Session-based auth for the web app
- Role-based access control
- Rate limiting on login attempts
```

The council will engage:
- **security-knight** for authentication design and threat modelling
- **backend-goblin** for performance of auth checks
- **api-keeper** for token handling and API contracts
- **system-architect** for overall design
- **grumpy-security-nag** and others for critical review

### Response Structure

The council returns:

1. **Agents Consulted** - Which specialists were involved and why
2. **Grump Review Summary** - Issues raised and fixes applied per iteration
3. **Final Solution** - The approved code, design, or recommendation
4. **Notes and Trade-offs** - Important context and decisions made

### Optional: Enable Logging

Add `scribe: on` to your request to save the deliberation process:

```
/summon-council
scribe: on

Refactor the payment processing module for better testability.
```

Logs are saved to `.parliament-of-chaos/{task-name}-{timestamp}.md`.

---

## /summon-grumpy-reviewer

A focused, critical code review from a senior developer perspective.

### When to Use

- Quick code review before committing
- Validating a refactor
- Getting feedback on a PR
- Finding issues in existing code
- When you want honest, blunt feedback

### How It Works

1. **Goal Clarification** - The reviewer restates what success looks like
2. **Review Angles** - Defines the perspectives for review (correctness, readability, etc.)
3. **Detailed Analysis** - Goes through code from each angle
4. **Structured Feedback** - Returns issues, recommendations, and a verdict

### Example Usage

```
/summon-grumpy-reviewer

Review this service class:

class OrderService
{
    public function process($order)
    {
        $user = User::find($order->user_id);
        $items = OrderItem::where('order_id', $order->id)->get();

        foreach ($items as $item) {
            $product = Product::find($item->product_id);
            $item->price = $product->price;
            $item->save();
        }

        $order->total = $items->sum('price');
        $order->save();

        Mail::send(new OrderConfirmation($order));

        return $order;
    }
}
```

### Response Structure

1. **Quality Summary** - Overall assessment (usually grumpy)
2. **Issues by Category** - Problems organised by type with severity ratings
   - Correctness and Bugs
   - Clarity and Readability
   - Structure and Architecture
   - Reusability and DRY
   - Standards and Conventions
   - Maintainability
   - Testability
3. **Refactor Suggestions** - Concrete improvements with code examples
4. **Definition of Done** - Checklist of required fixes before approval

### Severity Levels

- **HIGH** - Must fix before merging
- **MEDIUM** - Should fix, technical debt if ignored
- **LOW** - Nice to have, minor improvements

---

## Tips for Best Results

### Be Specific About Context

The more context you provide, the better the review:

```
/summon-council

We're building a multi-tenant SaaS. Each tenant has isolated data.
Current stack: Laravel 11, PostgreSQL, Redis.
Constraint: Must work with existing User model.

Design the tenant isolation layer.
```

### State Your Constraints

Mention what cannot change:

```
/summon-grumpy-reviewer

This code must remain backwards compatible with v2 API clients.
Review for security issues only.

[code here]
```

### Use the Right Tool

- Use `/summon-council` for open-ended design tasks
- Use `/summon-grumpy-reviewer` for reviewing existing code

### Iterate on Feedback

Both commands support follow-up. After receiving feedback:

```
I've addressed the N+1 query issue. Here's the updated code:

[updated code]
```

The reviewer will re-evaluate.

---

## Available Specialist Agents

You can reference these directly when asking the council to focus on specific areas:

| Agent | Expertise |
|-------|-----------|
| backend-goblin | Performance, caching, async patterns |
| system-architect | High-level design, patterns, trade-offs |
| security-knight | Auth, vulnerabilities, hardening |
| data-warlock | Database design, queries, migrations |
| api-keeper | API design, versioning, contracts |
| test-prophet | Testing strategy, coverage, TDD |
| ui-ux-guru | Accessibility, UX patterns, frontend |
| pipeline-engineer | CI/CD, deployment, infrastructure |
| doc-bard | Documentation, comments, READMEs |
| package-wizard | Dependencies, versions, compatibility |
| resilience-tamer | Error handling, retries, failure modes |

## Available Grumpy Reviewers

| Reviewer | Focus |
|----------|-------|
| grumpy-code-reviewer | Overall code quality |
| grumpy-standards-enforcer | Coding standards compliance |
| grumpy-architecture-skeptic | Architectural decisions |
| grumpy-maintainability-curmudgeon | Long-term maintenance burden |
| grumpy-security-nag | Security oversights |
| grumpy-performance-troll | Performance issues |
