# Database decision: deferred, no database service enabled

Initial SBC uses file-based dispatcher destinations, in-memory transaction
state and no registrar/CDR storage. A database would add credentials, schema,
backups and operations without a required feature. It is intentionally absent.

When persistent routing/accounting is approved, prefer a separate PostgreSQL
service with a pinned major version/digest and a named data volume. Install the
matching kamailio-postgres-modules version (Bookworm index: 5.6.3-2); use SQL
schema shipped by that exact package, check version table and test in disposable
DB before migration. Runtime account gets only needed table privileges; schema
owner/migrator is separate. No superuser in Kamailio. Secrets injected from
external files/vault, never example passwords or environment dumps.

Add pg_isready plus actual least-privilege SELECT/transaction readiness checks;
connection pool/timeouts must match process counts. Transactions, dispatcher
probe state and active connections stay in memory; persistence does not restore
active calls. Registrar state needs explicit ownership and replication design.
CDRs may contain personal data; define retention/access and durable delivery.

Backups: encrypted pg_dump custom format plus role definitions and recovery
metadata to separate storage. Restore to NEW database/volume, validate schema,
row counts and app queries, then switch traffic after approval. Volume alone
is not backup. Never run destructive schema init or overwrite old volume.
Use additive reviewed migrations, backup first, rehearse rollback/restore before
major changes. No DB connectivity or persistence test is claimed executed.
