# Architecture Overview

This page describes what Hume is, what gets deployed when you install the Helm chart, and how the components relate to each other. Read this before touching any configuration.

---

## What is Hume?

Hume is a graph analytics platform by GraphAware. It lets teams build, explore, and operationalize graph-based data models on top of Neo4j. The platform consists of a set of cooperating services, each with a distinct responsibility.

---

## Component Map

```
                          ┌─────────────────────────────────────────────────┐
                          │              Kubernetes Cluster                  │
                          │                                                  │
  [Browser / API Client]  │                                                  │
          │               │   ┌──────────────┐     ┌──────────────────────┐ │
          ▼               │   │  Hume Web    │     │     Hume API         │ │
   [ Ingress / LB ]  ─────┼──▶│  :8081       │────▶│     :8080            │ │
                          │   │  (nginx SPA) │     │  (Spring Boot)       │ │
                          │   └──────────────┘     └──────┬───────────────┘ │
                          │                               │                  │
                          │            ┌──────────────────┼──────────────┐   │
                          │            │                  │              │   │
                          │            ▼                  ▼              ▼   │
                          │   ┌──────────────┐  ┌──────────────┐  ┌────────┐│
                          │   │   Orchestra  │  │  EventStore  │  │ Media  ││
                          │   │   :8100      │  │  :9090       │  │ :8008  ││
                          │   │  (StatefulSet│  │  (audit log) │  │ (files)││
                          │   │  :8101 hooks)│  └──────┬───────┘  └───┬────┘│
                          │   └──────┬───────┘         │              │     │
                          │          │                  │              │     │
                          │          ▼                  ▼              ▼     │
                          │   ┌──────────┐    ┌──────────────┐  ┌────────┐  │
                          │   │  PG:orch │    │  PG:eventstore│  │PG:media│  │
                          │   └──────────┘    └──────────────┘  └────────┘  │
                          │                                                  │
                          │   ┌──────────┐  (external — you provide this)   │
                          │   │  PG:core │                                  │
                          │   └──────────┘   ┌───────────────────────────┐  │
                          │                  │  Neo4j  (not in chart)    │  │
                          │                  └───────────────────────────┘  │
                          │                                                  │
                          │  ─ ─ ─ ─ ─ Optional services below ─ ─ ─ ─ ─   │
                          │                                                  │
                          │   ┌──────────────┐     ┌──────────────────────┐ │
                          │   │   Maestro    │     │ Alerting Controller  │ │
                          │   │   :8090      │     │ Alerting Operator    │ │
                          │   │ (LLM bridge) │     │ + Kafka              │ │
                          │   └──────────────┘     └──────────────────────┘ │
                          └─────────────────────────────────────────────────┘
```

---

## Core Services

These services are deployed in every Hume installation.

### Hume Web (`hume-web`)

| | |
|---|---|
| **Image** | `docker.graphaware.com/hume-core/hume-web` |
| **Port** | 8081 |
| **Kind** | Deployment |

The browser-facing front end. An nginx container serving a React single-page application. It communicates with Hume API at runtime — users' browsers call the API directly, so both Web and API must be reachable from wherever users are browsing.

### Hume API (`hume-api`)

| | |
|---|---|
| **Image** | `docker.graphaware.com/hume-core/hume-api` |
| **Port** | 8080 (API), 9080 (security server), 7001 (metrics) |
| **Kind** | Deployment |

The platform's Spring Boot backend. Handles authentication, user management, graph connectivity (to Neo4j), and coordination between all other services. All other Hume services register with or are called by the API. The API owns the core PostgreSQL database.

### Hume Orchestra (`hume-orchestra`)

| | |
|---|---|
| **Image** | `docker.graphaware.com/hume-core/hume-orchestra` |
| **Ports** | 8100 (main), 8101 (webhooks), 7001 (metrics) |
| **Kind** | StatefulSet |

The workflow orchestration engine. Runs background jobs, scheduled tasks, and data pipelines. Orchestra persists its state to a PersistentVolume (`/data`) and has its own PostgreSQL database. Webhooks on port 8101 allow external systems to trigger workflows. Can run in cluster mode (multiple replicas with automatic leader election).

### Hume EventStore (`hume-eventstore`)

| | |
|---|---|
| **Image** | `docker.graphaware.com/hume-core/hume-eventstore` |
| **Port** | 9090 (API), 7001 (metrics) |
| **Kind** | Deployment |

An immutable audit log that records all platform events. Required for compliance use cases and for event replay. Communicates with the API via HTTP basic auth. Has its own PostgreSQL database.

> See [EventStore Configuration](../configuration/eventstore.md) for database and metrics options.

### Hume Media (`hume-media`)

| | |
|---|---|
| **Image** | `docker.graphaware.com/hume-core/hume-media` |
| **Port** | 8008 (API), 7001 (metrics) |
| **Kind** | StatefulSet |

Binary file storage — images, documents, and other attachments that can be linked to graph entities. Supports local filesystem, Amazon S3, and MinIO backends. Has its own PostgreSQL database for metadata.

> See [Media Configuration](../configuration/media.md) for storage backend options.

---

## Optional Services

These services require explicit enablement and, in the case of Alerting, an additional licence.

### Hume Maestro (`hume-maestro`)

| | |
|---|---|
| **Port** | 8090 (API), 7001 (metrics) |
| **Kind** | Deployment |

A bridge between the Hume platform and large language models. Enables natural-language queries, AI-powered insights, and conversational interfaces embedded in the Hume UI. Supports Ollama (local), OpenAI, and Azure OpenAI as model providers. See [Maestro](../optional-services/maestro.md).

### Hume Alerting (separately licensed)

| | |
|---|---|
| **Components** | Controller (alert evaluation) + Operator (notification dispatch) |
| **Kind** | 2 × Deployment |
| **Messaging** | Kafka (internal or external) or Azure Service Bus |

A rule-based alert engine. The Controller evaluates alert conditions; the Operator dispatches notifications via email, webhook, and other channels. Uses Kafka as a message bus between components. Each component has its own PostgreSQL database. See [Alerting](../optional-services/alerting.md).

> Alerting requires a separate licence from GraphAware. Contact your account team before enabling it.

---

## Databases

Each Hume service owns its own PostgreSQL schema. The chart can deploy embedded Bitnami PostgreSQL instances or connect to external databases you manage.

| Service | Database alias | Default |
|---|---|---|
| Hume API | `postgresqlCore` | Embedded |
| Orchestra | `postgresqlOrchestra` | Embedded |
| EventStore | `postgresqlEventStore` | Embedded |
| Media | `postgresqlMedia` | Embedded |
| Alerting Controller | `postgresqlAlertingController` | Embedded |
| Alerting Operator | `postgresqlAlertingOperator` | Embedded |

> **Production rule:** Embedded PostgreSQL is a single-pod StatefulSet with no replication or automated backups. Use external managed PostgreSQL (AWS RDS, Azure Database, Cloud SQL, etc.) for any environment where data matters. See [Databases](../configuration/databases.md).

---

## Charts

The repository contains two Helm charts:

| Chart | Purpose |
|---|---|
| `hume-helm` | Core platform (Web, API, Orchestra, EventStore, Media, Maestro) |
| `hume-alerting` | Alerting engine (Controller, Operator, Kafka) |

`hume-alerting` is bundled as a sub-chart of `hume-helm`. When you install `hume-helm` with `alerting.enabled: true`, the alerting chart is installed automatically. You can also install `hume-alerting` standalone if you prefer to manage it separately.

---

## What the Chart Does NOT Provide

- **Neo4j**: Hume connects to Neo4j but does not deploy it. You must provision your own Neo4j instance. See the [Neo4j Helm chart](https://helm.neo4j.com/).
- **Load Balancer / Ingress Controller**: You bring your own (AWS ALB, Nginx, Traefik, etc.). See [Ingress](../configuration/ingress.md).
- **TLS Certificates**: Managed by your ingress controller or cert-manager.

---

## Next Steps

- [Prerequisites](prerequisites.md) — What you need before installing
- [Quick Start](quick-start.md) — Running Hume locally in under 10 minutes
