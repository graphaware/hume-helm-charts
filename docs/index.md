# Hume Helm Chart Documentation

Hume is an enterprise graph analytics platform by GraphAware that lets teams build, explore, and operationalize graph-based intelligence on top of Neo4j.

This documentation covers everything you need to deploy and operate Hume on Kubernetes using the official Helm charts.

---

## Start Here

| Goal | Where to go |
|---|---|
| I want to understand what gets deployed | [Architecture Overview](getting-started/architecture.md) |
| I want to run Hume locally in minutes | [Quick Start](getting-started/quick-start.md) |
| I'm deploying to a real cluster | [Prerequisites](getting-started/prerequisites.md) → [Basic Installation](installation/basic-installation.md) |
| I'm upgrading from a previous version | [Upgrade Guide](installation/upgrade-guide.md) |
| I need to connect to an existing database | [Databases](configuration/databases.md) |
| I'm setting up SSO | [Authentication](configuration/authentication.md) |
| Something is broken | [Troubleshooting](operations/troubleshooting.md) |

---

## Documentation Sections

### Getting Started

| Page | Description |
|---|---|
| [Architecture Overview](getting-started/architecture.md) | Component diagram, service responsibilities, what gets deployed |
| [Prerequisites](getting-started/prerequisites.md) | Kubernetes, Helm, registry access, licence requirements |
| [Quick Start](getting-started/quick-start.md) | Local deployment with port-forwarding, no ingress required |

### Installation

| Page | Description |
|---|---|
| [Basic Installation](installation/basic-installation.md) | Full install walkthrough with verification steps |
| [Upgrade Guide](installation/upgrade-guide.md) | Version-by-version upgrade notes, including breaking changes |

### Configuration

| Page | Description |
|---|---|
| [Ingress](configuration/ingress.md) | AWS ALB, Nginx, and no-ingress patterns |
| [Authentication](configuration/authentication.md) | Native auth vs Keycloak SSO (internal and external) |
| [Databases](configuration/databases.md) | Choosing between embedded and external PostgreSQL |
| [Storage](configuration/storage.md) | Orchestra PVCs and Media storage backends (local, S3, MinIO) |
| [EventStore](configuration/eventstore.md) | Audit log service configuration |
| [Media](configuration/media.md) | File storage service configuration |

### Optional Services

| Page | Description |
|---|---|
| [Maestro](optional-services/maestro.md) | LLM integration (Ollama, OpenAI, Azure OpenAI) |
| [Alerting](optional-services/alerting.md) | Rule-based alert engine with Kafka or Azure Service Bus |

### Production

| Page | Description |
|---|---|
| [High Availability](production/high-availability.md) | Orchestra clustering, HPA, resource limits, anti-affinity |
| [Monitoring](production/monitoring.md) | Prometheus ServiceMonitors, alert rules, structured logging |
| [Security](production/security.md) | Secrets management, pod security, air-gapped deployments |
| [Backup and Restore](production/backup-restore.md) | Database backup patterns and restore procedures |

### Operations

| Page | Description |
|---|---|
| [Troubleshooting](operations/troubleshooting.md) | Symptom-driven diagnosis for common failures |

### Reference

| Page | Description |
|---|---|
| [Values Reference: hume-helm](reference/values-hume-helm.md) | Complete parameter reference for the core chart |
| [Values Reference: hume-alerting](reference/values-alerting.md) | Complete parameter reference for the alerting chart |

---

## Licence

Hume requires a licence from GraphAware. The Alerting module requires a separate licence.

Contact the GraphAware team or visit [graphaware.com/products/hume](https://www.graphaware.com/products/hume/) to obtain a licence before deploying.
