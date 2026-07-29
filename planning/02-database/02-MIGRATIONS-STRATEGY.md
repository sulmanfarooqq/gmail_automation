# Database Migrations Strategy

## Tool: Prisma Migrate

### Principles

1. **Every schema change = new migration file** — never edit existing migrations
2. **Migrations run in CI/CD pipeline** — never manually on production
3. **Rollback plan** — each migration must be reversible
4. **Zero-downtime migrations preferred** — avoid locking tables on large datasets

### Migration Workflow

```bash
# Development
npx prisma migrate dev --name add_email_classification

# Staging (auto-applied via CI)
npx prisma migrate deploy

# Production (via CI/CD with approval gate)
npx prisma migrate deploy --preview-feature
```

### Safe Migration Patterns

| Change Type | Safe? | Strategy |
|-------------|-------|----------|
| Add nullable column | ✅ | No downtime |
| Add non-nullable column | ⚠️ | Add as nullable → backfill → alter to not null |
| Remove column | ⚠️ | Stop reading → deploy app → remove column in next release |
| Rename column | ⚠️ | Add new → dual-write → backfill → stop reading old → drop old |
| Add index | ✅ | CONCURRENTLY to avoid table lock |
| Remove index | ✅ | No downtime |
| Create table | ✅ | No downtime |
| Add foreign key | ⚠️ | Validate existing data first |

### Seed Data

- Development: `prisma/seed.ts` with realistic sample data (fake agencies, users, emails)
- Staging: Anonymized copy of production data
- Production: Never seed automatically
