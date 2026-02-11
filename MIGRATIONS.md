# Database Migrations

Parkly uses **Alembic** for database schema migrations. Migrations are **not auto-generated** — each revision must be written manually.

Migration scripts live in:
```
src/parkly/adapters/outbound/persistence/migrations/versions/
```

## Prerequisites

Make sure `PARKLY_DATABASE_URL` is set (via `.env` or environment variable):
```bash
export PARKLY_DATABASE_URL=postgresql+asyncpg://parkly:parkly@localhost:5432/parkly
```

## Commands

### Create a new migration

```bash
uv run alembic revision -m "describe_the_change"
```

This creates an empty revision file in `versions/`. Edit the generated file to write your `upgrade()` and `downgrade()` functions manually.

### Apply all pending migrations

```bash
uv run alembic upgrade head
```

### Apply up to a specific revision

```bash
uv run alembic upgrade <revision_id>
```

### Rollback the last migration

```bash
uv run alembic downgrade -1
```

### Rollback to a specific revision

```bash
uv run alembic downgrade <revision_id>
```

### Rollback all migrations

```bash
uv run alembic downgrade base
```

### Show current revision

```bash
uv run alembic current
```

### Show migration history

```bash
uv run alembic history --verbose
```

### Generate SQL without executing (offline mode)

```bash
uv run alembic upgrade head --sql
```
