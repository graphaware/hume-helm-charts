# Databases

Configure PostgreSQL for each Hume service — either embedded (chart-managed) or external (your own managed PostgreSQL).

---

## Database Architecture

Each Hume service owns its own PostgreSQL database. They do not share a server in the default configuration.

| Service | Chart alias | Default state |
|---|---|---|
| Hume API | `postgresqlCore` | Embedded, enabled |
| Orchestra | `postgresqlOrchestra` | Embedded, enabled |
| EventStore | `postgresqlEventStore` | Embedded, enabled with EventStore |
| Media | `postgresqlMedia` | Embedded, enabled with Media |
| Alerting Controller | `postgresqlAlertingController` | Embedded, enabled with Alerting |
| Alerting Operator | `postgresqlAlertingOperator` | Embedded, enabled with Alerting |

PostgreSQL version: **15.1.0**, pulled from `docker.graphaware.com/mirror/bitnami/postgresql:15.1.0-debian-11-r12`.

---

## Option 1: Embedded PostgreSQL

The chart deploys a Bitnami PostgreSQL StatefulSet for each service. This is the default and requires no database configuration.

### Default credentials

> **Security callout:** These are insecure defaults. Change all passwords before running Hume in any shared or accessible environment.

| Service | Database | Username | Default password |
|---|---|---|---|
| API (core) | `hume` | `hume` | `hume` |
| Orchestra | `orchestra` | `orchestra` | `pgsqls3cr3t` |
| EventStore | `eventstore` | `eventstore` | `eventstore` |
| Media | `media` | `media` | `media` |

To change a password, override it in your values:

```yaml
postgresqlCore:
  global:
    postgresql:
      auth:
        password: "<strong-random-password>"

postgresqlOrchestra:
  global:
    postgresql:
      auth:
        password: "<strong-random-password>"
```

Apply the same pattern to `postgresqlEventStore` and `postgresqlMedia`.

### When to use embedded PostgreSQL

- Local development and evaluation
- Small internal deployments where data loss is acceptable
- Getting started quickly without pre-existing database infrastructure

### Limitation callout

Each embedded PostgreSQL runs as a **single pod with no replication**. There are no automated backups. A pod restart will not lose data (PVC persists), but a PVC deletion or node failure without proper storage replication will. Do not use embedded PostgreSQL if data durability is required — use external PostgreSQL instead.

---

## Option 2: External PostgreSQL

Point each Hume service at an external PostgreSQL server you manage. This is the correct choice for production.

**Requirements:** PostgreSQL 14 or later.

### Method A: Using `customXxxPostgresql` values (recommended)

Disable the embedded chart for each service and supply connection details via the `custom*` values blocks. This approach keeps credentials in a Kubernetes secret rather than in your values file.

**Create a credentials secret first:**

```bash
kubectl create secret generic hume-db-credentials \
  --from-literal=password='<your-db-password>' \
  -n hume
```

If each database uses a different password, create a secret per database or use separate keys:

```bash
kubectl create secret generic hume-db-credentials \
  --from-literal=core-password='<core-db-password>' \
  --from-literal=orchestra-password='<orchestra-db-password>' \
  --from-literal=eventstore-password='<eventstore-db-password>' \
  --from-literal=media-password='<media-db-password>' \
  -n hume
```

**values.yaml — complete external database example:**

```yaml
# Disable all embedded PostgreSQL instances
postgresqlCore:
  enabled: false
postgresqlOrchestra:
  enabled: false
postgresqlEventStore:
  enabled: false
postgresqlMedia:
  enabled: false

# API / core database
customApiPostgresql:
  global:
    postgresql:
      auth:
        database: "hume_core"
        hostname: "<rds-endpoint>.rds.amazonaws.com"
        username: "hume"
        servicePort: 5432
      secretRef:
        existingSecret: "hume-db-credentials"
        passwordSecretKey: "core-password"

# Orchestra database
customOrchestraPostgresql:
  global:
    postgresql:
      auth:
        database: "hume_orchestra"
        hostname: "<rds-endpoint>.rds.amazonaws.com"
        username: "orchestra"
        servicePort: 5432
      secretRef:
        existingSecret: "hume-db-credentials"
        passwordSecretKey: "orchestra-password"

# EventStore database
customEventstorePostgresql:
  global:
    postgresql:
      auth:
        database: "hume_eventstore"
        hostname: "<rds-endpoint>.rds.amazonaws.com"
        username: "eventstore"
        servicePort: 5432
      secretRef:
        existingSecret: "hume-db-credentials"
        passwordSecretKey: "eventstore-password"

# Media database
customMediaPostgresql:
  global:
    postgresql:
      auth:
        database: "hume_media"
        hostname: "<rds-endpoint>.rds.amazonaws.com"
        username: "media"
        servicePort: 5432
      secretRef:
        existingSecret: "hume-db-credentials"
        passwordSecretKey: "media-password"
```

### Method B: Using environment variable overrides

Pass JDBC connection strings directly via the service's `env` section. Use this when you prefer explicit JDBC URLs or when `customXxx` values are not sufficient for your setup.

```yaml
postgresqlCore:
  enabled: false

api:
  env:
    - name: "spring.datasource.url"
      value: "jdbc:postgresql://<rds-endpoint>.rds.amazonaws.com:5432/hume_core"
    - name: "spring.datasource.username"
      value: "hume"
    - name: "spring.datasource.password"
      valueFrom:
        secretKeyRef:
          name: "hume-db-credentials"
          key: "core-password"

postgresqlOrchestra:
  enabled: false

orchestra:
  env:
    - name: "spring.datasource.url"
      value: "jdbc:postgresql://<rds-endpoint>.rds.amazonaws.com:5432/hume_orchestra"
    - name: "spring.datasource.username"
      value: "orchestra"
    - name: "spring.datasource.password"
      valueFrom:
        secretKeyRef:
          name: "hume-db-credentials"
          key: "orchestra-password"
```

---

## Verify It Works

Check that each service pod started without database connection errors:

```bash
# Check API connection
kubectl logs deployment/hume-api -n hume | grep -i "datasource\|database\|connection"

# Check Orchestra connection
kubectl logs statefulset/hume-orchestra -n hume | grep -i "datasource\|database\|connection"
```

A successful connection shows log entries like:
```
HikariPool-1 - Start completed.
```

A failed connection shows:
```
Unable to acquire JDBC Connection
Connection refused
```

To run a direct database query from inside a pod:

```bash
kubectl exec -it deployment/hume-api -n hume -- \
  psql "jdbc:postgresql://<hostname>:5432/hume_core" -U hume -c "\dt"
```

---

## Next Steps

- [Storage](storage.md) — Size PVCs for embedded PostgreSQL and Orchestra
- [EventStore](eventstore.md) — Configure the EventStore database
- [Media](media.md) — Configure the Media database and file storage backend
- [Production: Backup & Restore](../production/backup-restore.md) — Back up your databases
