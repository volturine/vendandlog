# Decision 0001 — Database

**Status:** accepted (implemented 2026-08-29) · **Date:** 2026-08-29 · **Decides:** production database for Vendandlog

## Context

The skeleton runs SQLite via SQLModel. The premise expects **millions of listings and
transactions** over time, an **append-only event log that never shrinks**, an evolving
**category tree** (flexible listing attributes), a planned **AI matching service**
(embeddings), a **trust scoring service**, and a modular `packages/services` architecture.
Deployment is Docker Compose on a single host today.

## Research summary (2026 sources)

**SQLite in 2026 is legitimately production-grade** — WAL mode, Litestream backups, STRICT
tables. The honest criteria from current writing (ByteLedger, goilerplate, devops-daily,
Kunal Ganglani):

- SQLite shines: single-server, single-writer process, read-heavy, embedded/edge, one file
  per tenant, zero-ops deploys.
- SQLite's fault line **is not data size — it is concurrent writers from multiple
  processes** and the lack of an extension ecosystem.

**Postgres is the standard relational core for marketplaces** (UpCloud workload table:
"SaaS CRUD apps, marketplaces → relational core (PostgreSQL)"). Its extension ecosystem is
the differentiator: **pgvector** (the production standard for AI/RAG retrieval),
**JSONB + GIN indexes** (flexible attributes with real indexing), full-text search +
`pg_trgm`, TimescaleDB, declarative partitioning, MVCC for many concurrent writers.

**MongoDB** wins on native sharding and change streams, loses on relational integrity
(ratings ↔ sales ↔ users), joins, and "we moved from Mongo to Postgres" is the common
migration direction. Marketplaces are join-heavy: not our shape.

**Distributed SQL (CockroachDB, TiDB, Yugabyte)** solves multi-region writes we will not
have for years; heavy operational cost. **ClickHouse** is OLAP analytics — a possible
*future addition* for log analytics, never the OLTP core. **MySQL/MariaDB** fine but
weaker extension ecosystem; no reason to prefer over Postgres in a greenfield.

**Scale sanity check:** millions of listings is small for a single tuned Postgres
(tens of millions of rows is ordinary). The one table that grows without bound is
`listingevent` (append-only, ~tens of events per listing). That is a partitioning problem,
not a different-database problem.

## Decision

**Adopt PostgreSQL as the production database now. Keep SQLite for tests.**

1. **Why now, not "when we scale":** SQLite's limit is *concurrent writers from multiple
   processes* — which is exactly the modular-services future (API + trust scoring + AI
   matching writing concurrently). Migrating later means a real downtime + data migration
   under load; migrating now is a config change plus a reseed (no real data exists yet).
2. **Feature pull is concrete, not speculative:** pgvector (AI matching is in the premise),
   JSONB (dynamic category trees and per-category listing attributes), FTS/pg_trgm
   (marketplace search v1), declarative partitioning (the immutable log).
3. **Tests stay on in-memory SQLite** — fast, no infra. This forces us to avoid
   Postgres-only SQL in domain code; anything that must be dialect-specific lives behind
   a small adapter (the event-log hash chain and search are the likely candidates).
4. **Introduce Alembic migrations now** (data-forge precedent). `create_all` cannot
   evolve a schema that holds real user data.
5. **Event log strategy:** append-only table partitioned by month on `created_at` once it
   grows (declare the intent now, apply partitioning when volume justifies it); the log is
   also the natural change feed for the future services (CDC via logical replication
   later — no Kafka yet).
6. **Search:** Postgres FTS first. Only add Meilisearch/Typesense when search *quality*
   (typo tolerance, faceting, ranking) demands a dedicated engine. Same for Redis: not
   until a cache/queue need is real.

## Consequences

- Backend gains a `postgres` service in compose (dev + prod); SQLite remains the default
  for tests via `VDL_DB_URL=sqlite://`.
- Alembic becomes the only way schema changes ship; `create_all` stays only for fresh
  test databases.
- The Dockerfile runtime image needs a Postgres driver (`psycopg`).
- First real migration: add Alembic, port schema, keep demo seeding.
- Revisit triggers: sustained multi-region writes, event-log analytics at Petabyte scale
  (→ ClickHouse), search quality ceiling (→ Meilisearch/Typesense), per-tenant isolation.

## Rejected alternatives (why)

| Option | Why not |
| --- | --- |
| Stay on SQLite | Blocks the multi-writer service architecture; no pgvector/JSONB/partitioning; migration cost only grows |
| MongoDB | Marketplace is join-heavy and integrity-critical; ratings/sales/users want FKs; we would keep a second query language for no gain |
| CockroachDB / TiDB | Solves multi-region scale we do not have; real ops burden |
| MySQL/MariaDB | Fine, but smaller extension ecosystem; greenfield default is Postgres |
| Dedicated vector DB (Pinecone/Qdrant) | pgvector covers matching at our scale; add later if it truly limits |
