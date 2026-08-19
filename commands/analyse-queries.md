---
description: Analyse SQL queries and ORM code for performance issues and missing indexes
effort: medium
argument-hint: "[<path>] [--scan] [--sql <query>]"
---

# Analyse Queries

Analyse SQL queries or ORM code for performance problems: missing indexes, N+1 patterns, full table scans, and inefficient joins. Recommends specific indexes and query optimisations.

## Usage

```
/analyse-queries [<path>] [--scan] [--sql <query>]
```

**Examples**:
```
/analyse-queries src/repositories/    # Analyse ORM queries in a directory
/analyse-queries --scan               # Scan entire codebase for query patterns
/analyse-queries --sql "SELECT * FROM orders WHERE status = 'pending' AND created_at > '2026-01-01'"
```

## Options

- `<path>` (optional): File or directory containing queries to analyse
- `--scan` (optional): Scan the entire codebase for query patterns
- `--sql` (optional): Analyse a specific SQL query string

## Process

1. **Detect Query Patterns**
   - Find raw SQL queries, ORM query builders, and repository methods
   - Support: Eloquent, SQLAlchemy, ActiveRecord, Prisma, TypeORM, GORM, raw SQL
   - Detect N+1 patterns (loops with lazy-loaded relations)

2. **Analyse Schema**
   - Read migration files or schema dumps for table definitions
   - Map existing indexes, foreign keys, and constraints
   - Identify column types and cardinality estimates

3. **Evaluate Each Query**
   - Identify missing indexes for WHERE, JOIN, and ORDER BY columns
   - Flag full table scans on large tables
   - Detect SELECT * where specific columns would suffice
   - Flag unbounded queries missing LIMIT/pagination
   - Identify redundant or duplicate indexes

4. **Recommend Optimisations**
   - Generate specific `CREATE INDEX` statements
   - Suggest query rewrites for better execution plans
   - Recommend eager loading to resolve N+1 patterns
   - Estimate order-of-magnitude improvement

## Output

```markdown
# Query Analysis Report

## Issues Found: 7

### Critical: N+1 query in OrderRepository (src/repositories/OrderRepository.php:42)
- Pattern: Loading user for each order in a loop
- Fix: Use eager loading — `Order::with('user')->get()`
- Impact: ~100x fewer queries for typical page load

### High: Missing index on orders.status (src/migrations/create_orders.php)
- Query: `WHERE status = 'pending' AND created_at > ?`
- Fix: `CREATE INDEX idx_orders_status_created ON orders(status, created_at)`
- Impact: Table scan → index lookup

## Recommended Indexes
| Table | Columns | Type | Reason |
|-------|---------|------|--------|
| orders | (status, created_at) | composite | Covers status filter + date range |
```

## Notes

- Static analysis only — cannot run EXPLAIN against a live database
- Reads migration files to understand schema; works best when migrations are in the repo
- Pairs naturally with data-warlock for deeper database architecture questions
