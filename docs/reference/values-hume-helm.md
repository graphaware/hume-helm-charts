# Values Reference: hume-helm

Complete parameter reference for the `hume-helm` chart. Parameters are grouped by concern. For most deployments, you only need a small subset — start with the relevant configuration guides and use this page for lookup.

Legend: **Required** = must be set before install · **Prod** = default is unsafe for production · *italic default* = inherited from chart

---

## Global

| Parameter | Type | Default | Description |
|---|---|---|---|
| `baseDomain` | string | `""` | Domain suffix for ingress hostnames. e.g. `"example.com"` creates `hume-web.example.com`. Required when `ingress.enabled: true`. |
| `imagePullSecrets` | list | `[{name: graphaware-docker-creds}]` | Registry secrets. The named secret must exist in the namespace before install. |
| `imagePullPolicy` | string | `"Always"` | Image pull policy for all Hume images. Use `IfNotPresent` in production. **Prod** |
| `humeCoreBaseRepository` | string | `"docker.graphaware.com/hume-core/"` | Base repository for Hume core images. Override for air-gapped environments. Trailing slash required. |
| `deploymentStrategy.type` | string | `"RollingUpdate"` | Kubernetes deployment strategy. |
| `nodeSelector` | object | `{}` | Node selector applied to all pods (can be overridden per service). |
| `tolerations` | list | `[]` | Tolerations applied to all pods. |
| `affinity` | object | `{}` | Affinity rules applied to all pods. |
| `annotations` | object | `{}` | Annotations added to all resources. |
| `podAnnotations` | object | `{}` | Annotations added to all pods. |
| `nameOverride` | string | `""` | Partial override for resource names. |
| `fullnameOverride` | string | `"hume"` | Full override for resource names. |

### Autoscaling (global)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `autoscaling.enabled` | bool | `false` | Enable HPA for API and Web deployments. Requires metrics server. |
| `autoscaling.minReplicas` | int | `1` | Minimum replicas for autoscaled services. |
| `autoscaling.maxReplicas` | int | `100` | Maximum replicas for autoscaled services. |
| `autoscaling.targetCPUUtilizationPercentage` | int | `80` | CPU utilization target for HPA. |

---

## Ingress

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ingress.enabled` | bool | `false` | Create Ingress resources for Web, API, and Keycloak (if enabled). |
| `ingress.apiVersion` | string | `"networking.k8s.io/v1"` | Ingress API version. |
| `ingress.ingressClassName` | string | `""` | Ingress class (e.g. `nginx`, `alb`). |
| `ingress.annotations` | object | `{}` | Ingress annotations. See [Ingress guide](../configuration/ingress.md) for provider-specific examples. |
| `ingress.pathType` | string | `"Prefix"` | Path type for ingress rules. |
| `ingress.path` | string | `"/"` | Base path. |
| `ingress.protocol.scheme` | string | `"https"` | Protocol scheme used to compose internal URLs. |

---

## Keycloak

| Parameter | Type | Default | Description |
|---|---|---|---|
| `keycloak.useKeycloak.enabled` | bool | `false` | Enable Keycloak authentication integration. |
| `keycloak.internal.enabled` | bool | `false` | Deploy bundled Bitnami Keycloak. If false, uses `customKeycloak.customKeycloakEndpoint`. |
| `keycloak.customKeycloak.customKeycloakEndpoint` | string | `""` | URL of external Keycloak (e.g. `https://identity.example.com/auth`). Used when `internal.enabled: false`. |
| `keycloak.realm` | string | `""` | Keycloak realm name. Required when Keycloak is enabled. |
| `keycloak.client` | string | `""` | Keycloak client ID. Required when Keycloak is enabled. |
| `keycloak.fullnameOverride` | string | `"hume-keycloak"` | Name for the Keycloak deployment. |
| `keycloak.service.ports.http` | int | `8180` | Keycloak service port. |

---

## Hume API (`api`)

### Core

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.image.name` | string | `"hume-api"` | Image name. Full image: `humeCoreBaseRepository + api.image.name`. |
| `api.image.tag` | string | `""` | Image tag. Defaults to chart `appVersion` (3.0.0). |
| `api.port` | int | `8080` | API port. |
| `api.service.type` | string | `"NodePort"` | Service type. Use `ClusterIP` when behind an ingress. |
| `api.deployment.replicas` | string | `""` | Replica count. Empty = 1. |
| `api.app.name` | string | `"hume-api"` | App label value. |
| `api.env` | list | `[]` | Additional environment variables. Overrides take precedence. See [Environment Variables](../configuration/databases.md) for database override example. |
| `api.volumes` | list | `[]` | Additional volumes for the API pod. |
| `api.volumeMounts` | list | `[]` | Additional volume mounts for the API container. |
| `api.extraSecrets` | list | `[]` | Additional secrets to mount. |

### Admin User

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.admin.auto_create` | bool | `true` | Create the admin user on first startup. |
| `api.admin.username` | string | `"admin@hume.k8s"` | Admin username. **Prod** — change to a real address. |
| `api.admin.password` | string | `"password"` | Admin password. **Prod** — must be changed before going live. |

### Neo4j Driver

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.neo4j.driver.transaction.timeout` | int | `90000` | Neo4j transaction timeout in milliseconds. |

### Features

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.features.mde` | bool | `false` | Enable MDE (separately licensed). Requires appropriate licence. |

### Remote API

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.remoteApi.enabled` | bool | `false` | Enable machine-to-machine API access. Required for Maestro and initial API key creation. |

### Media Integration (API-side)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.media.enabled` | bool | `true` | Enable API-to-Media service integration. |
| `api.media.uri` | string | `"http://hume-media:8008"` | Media service URL. |
| `api.media.initialKey.create` | bool | `false` | Create an initial API key for the Media service on first start. |
| `api.media.initialKey.name` | string | `"initial-api-key"` | Name of the initial key. |
| `api.media.initialKey.token` | string | `"my-super-secret-token"` | Token value. **Prod** — use `existingSecret` instead. |
| `api.media.initialKey.roles` | string | `"USER"` | Comma-separated roles for the initial key. |

### Probes

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.probes.startupProbe.initialDelaySeconds` | int | `30` | Startup probe initial delay. |
| `api.probes.startupProbe.periodSeconds` | int | `5` | Startup probe interval. |
| `api.probes.startupProbe.failureThreshold` | int | `60` | Startup probe failure threshold (300s total startup budget). |
| `api.probes.livenessProbe.periodSeconds` | int | `10` | Liveness probe interval. |
| `api.probes.livenessProbe.failureThreshold` | int | `3` | Liveness probe failure threshold. |

### Metrics

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.metrics.enabled` | bool | `false` | Enable metrics service on port 7001. |
| `api.metrics.service.port` | int | `7001` | Metrics service port. |
| `api.metrics.serviceMonitor.enabled` | bool | `false` | Create a Prometheus ServiceMonitor. Requires Prometheus Operator. |
| `api.metrics.serviceMonitor.labels` | object | `{}` | Labels for ServiceMonitor discovery (e.g. `release: kube-prometheus-stack`). |
| `api.metrics.serviceMonitor.interval` | string | `"30s"` | Scrape interval. |
| `api.metrics.serviceMonitor.path` | string | `"/actuator/prometheus"` | Metrics path. |

### Security Server

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api.securityServer.service.port` | int | `9080` | Security server port. |

---

## Hume Web (`web`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `web.image.name` | string | `"hume-web"` | Image name. |
| `web.image.tag` | string | `""` | Image tag. Defaults to chart `appVersion`. |
| `web.port` | int | `8081` | Web service port. |
| `web.service.type` | string | `"ClusterIP"` | Service type. |
| `web.deployment.replicas` | string | `""` | Replica count. Empty = 1. |
| `web.env` | list | `[]` | Additional/override environment variables. Use to set `KEYCLOAK_URL` etc. for external Keycloak. |
| `web.extraHeaders` | list | `[]` | Custom nginx headers. Each entry is a raw `add_header` directive, e.g. `add_header X-Frame-Options "SAMEORIGIN";` |
| `web.extraSecrets` | list | `[]` | Additional secrets to mount. |

---

## Hume Orchestra (`orchestra`)

### Core

| Parameter | Type | Default | Description |
|---|---|---|---|
| `orchestra.enabled` | bool | `true` | Enable Orchestra. |
| `orchestra.image.name` | string | `"hume-orchestra"` | Image name. |
| `orchestra.image.tag` | string | `""` | Image tag. Defaults to chart `appVersion`. |
| `orchestra.port` | int | `8100` | Orchestra service port. |
| `orchestra.service.type` | string | `"ClusterIP"` | Service type. |
| `orchestra.deployment.replicas` | string | `""` | Replica count. Empty = 1. Set to `3` for cluster mode. |
| `orchestra.env` | list | `[]` | Additional environment variables. |
| `orchestra.volumes` | list | `[]` | Additional volumes. |
| `orchestra.volumeMounts` | list | `[]` | Additional volume mounts. |
| `orchestra.initContainers` | list | `[]` | Init containers (e.g. to download plugins from S3). |
| `orchestra.volumeClaimTemplates` | list | `[]` | Additional PVC templates for the StatefulSet. |
| `orchestra.extraSecrets` | list | `[]` | Additional secrets to mount. |

### Clustering

| Parameter | Type | Default | Description |
|---|---|---|---|
| `orchestra.cluster.enabled` | bool | `false` | Enable cluster mode (zookeeper-less leader election). Set `deployment.replicas` to 3 when enabling. |
| `orchestra.cluster.service.type` | string | `"ClusterIP"` | Cluster discovery service type. |

### Webhooks

| Parameter | Type | Default | Description |
|---|---|---|---|
| `orchestra.webhooks.enabled` | bool | `true` | Enable webhook listener on port 8101. |
| `orchestra.webhooks.port` | int | `8101` | Webhook port. One service per replica in cluster mode. |
| `orchestra.webhooks.service.type` | string | `"ClusterIP"` | Webhook service type. |

### Persistence

| Parameter | Type | Default | Description |
|---|---|---|---|
| `orchestra.persistence.enabled` | bool | `true` | Enable persistent volume for workflow state. |
| `orchestra.persistence.size` | string | `"1Gi"` | PVC size. **Prod** — increase to 50Gi+ for production. |
| `orchestra.persistence.mountPath` | string | `"/data"` | Mount path inside the container. |
| `orchestra.persistence.accessModes` | list | `[ReadWriteOnce]` | PVC access modes. |
| `orchestra.persistence.annotations` | object | `{}` | PVC annotations. |

### Probes

Same pattern as API probes. Orchestra probes check `/actuator/metrics` on port `metrics`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `orchestra.startupProbe.failureThreshold` | int | `20` | Startup failure threshold (~140s startup budget at 7s period). |
| `orchestra.livenessProbe.failureThreshold` | int | `10` | Liveness failure threshold. |

### Metrics

Same pattern as API metrics. See [Monitoring](../production/monitoring.md).

---

## Hume EventStore (`eventstore`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `eventstore.enabled` | bool | `true` | Enable EventStore. |
| `eventstore.image.name` | string | `"hume-eventstore"` | Image name. |
| `eventstore.image.tag` | string | `""` | Image tag. Defaults to chart `appVersion`. |
| `eventstore.port` | int | `9090` | EventStore API port. |
| `eventstore.service.type` | string | `"NodePort"` | Service type. Use `ClusterIP` behind ingress. |
| `eventstore.deployment.replicas` | string | `""` | Replica count. |
| `eventstore.username` | string | `"hume"` | Basic auth username for EventStore API. |
| `eventstore.password` | string | `"megaSecretPwd"` | Basic auth password. **Prod** — change this. |
| `eventstore.env` | list | `[]` | Additional environment variables. |
| `eventstore.extraSecrets` | list | `[]` | Additional secrets. |
| `eventstore.metrics.serviceMonitor.basicAuth.enabled` | bool | `false` | Enable basic auth for the metrics scrape. |
| `eventstore.metrics.serviceMonitor.basicAuth.secretName` | string | `"eventstore-credentials-secret"` | Secret containing `username` and `password` for metrics basic auth. |

---

## Hume Media (`media`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `media.enabled` | bool | `true` | Enable Media service. |
| `media.image.name` | string | `"hume-media"` | Image name. |
| `media.image.tag` | string | `""` | Image tag. Defaults to chart `appVersion`. |
| `media.port` | int | `8008` | Media API port. |
| `media.service.type` | string | `"NodePort"` | Service type. |
| `media.deployment.replicas` | string | `""` | Replica count. |
| `media.username` | string | `"hume"` | Basic auth username. |
| `media.password` | string | `"megaSecretPwd"` | Basic auth password. **Prod** — change this. |
| `media.security.apiKey` | string | `"hms_api_key"` | API key for machine authentication. **Prod** — change this. |
| `media.security.native.jwt.signingKey` | string | `""` | JWT signing key for token verification. **Required** — generate with `openssl rand -hex 32`. |
| `media.storage.local.enabled` | bool | `false` | Use local filesystem storage. Dev/test only. |
| `media.storage.local.uploadPath` | string | `"/tmp/upload"` | Upload staging path (local). |
| `media.storage.local.readyPath` | string | `"/tmp/upload"` | Ready files path (local). |
| `media.storage.s3.enabled` | bool | `false` | Use S3 storage. |
| `media.storage.s3.uploadPath` | string | `""` | S3 upload path (e.g. `s3://bucket/upload`). |
| `media.storage.s3.readyPath` | string | `""` | S3 ready path. |
| `media.storage.minio.enabled` | bool | `false` | Use MinIO storage. |
| `media.storage.minio.uploadPath` | string | `""` | MinIO upload path. |
| `media.storage.minio.readyPath` | string | `""` | MinIO ready path. |
| `media.storage.minio.accessKey` | string | `""` | MinIO access key. |
| `media.storage.minio.accessSecret` | string | `""` | MinIO secret key. **Prod** — use `media.env` with a secretKeyRef instead. |
| `media.storage.file.max_size` | string | `"200MB"` | Maximum file upload size. |
| `media.storage.file.initial_status` | string | `"READY"` | Status assigned to files on upload. |
| `media.resources.requests.cpu` | string | `"500m"` | CPU request. |
| `media.resources.requests.memory` | string | `"2048Mi"` | Memory request. |

---

## Hume Maestro (`maestro`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `maestro.enabled` | bool | `false` | Enable Maestro. Requires `api.remoteApi.enabled: true`. |
| `maestro.model.provider` | string | `"ollama"` | LLM provider: `ollama`, `openai`, or `azure-openai`. |
| `maestro.primaryConfigMapRef` | string | `"api-maestro-primary-configmap"` | ConfigMap name containing agent definitions. |
| `maestro.additionalConfigMapRef` | string | `""` | Optional additional agent ConfigMap. |
| `maestro.ollama.base-url` | string | `""` | Ollama server URL (e.g. `http://ollama:11434`). Required when provider is `ollama`. |
| `maestro.openai.apiKey.secretKeyName` | string | `""` | K8s secret name containing OpenAI API key. |
| `maestro.openai.apiKey.secretKeyRef` | string | `""` | Key within the secret. |
| `maestro.azure-openai.deployment.name` | string | `""` | Azure OpenAI deployment name. |
| `maestro.azure-openai.endpoint` | string | `""` | Azure OpenAI endpoint URL. |
| `maestro.azure-openai.apiKey.secretKeyName` | string | `""` | K8s secret name containing Azure OpenAI key. |
| `maestro.azure-openai.apiKey.secretKeyRef` | string | `""` | Key within the secret. |
| `maestro.log-llm-requests` | string | `"false"` | Log all LLM requests/responses. Enable for debugging. Disable in production. |
| `maestro.port` | int | `8090` | Maestro API port. |
| `maestro.image.name` | string | `"hume-maestro"` | Image name. |

---

## Alerting (`alerting`)

These values configure the hume-alerting sub-chart when bundled with hume-helm. For standalone deployment, see [hume-alerting values reference](values-alerting.md).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `alerting.enabled` | bool | `false` | Enable the alerting sub-chart. Requires separate Alerting licence. |
| `alerting.uri` | string | `"http://hume-alerting-development"` | URI the API uses to reach the alerting service. Update to match your release name. |
| `hume-alerting.*` | — | — | All hume-alerting values are passed through under the `hume-alerting:` key. See [Alerting reference](values-alerting.md). |

---

## PostgreSQL — Core (`postgresqlCore`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `postgresqlCore.enabled` | bool | `true` | Deploy embedded PostgreSQL for the API. Set to `false` when using external database. |
| `postgresqlCore.global.postgresql.auth.database` | string | `"hume"` | Database name. **Prod** — change credentials. |
| `postgresqlCore.global.postgresql.auth.username` | string | `"hume"` | Database username. |
| `postgresqlCore.global.postgresql.auth.password` | string | `"hume"` | Database password. **Prod** — change this. |
| `postgresqlCore.global.postgresql.auth.servicePort` | int | `5432` | PostgreSQL port. |
| `postgresqlCore.image.registry` | string | `"docker.graphaware.com"` | Image registry. |
| `postgresqlCore.image.repository` | string | `"mirror/bitnami/postgresql"` | Image repository. |
| `postgresqlCore.image.tag` | string | `"15.1.0-debian-11-r12"` | Image tag. |

**External database** — disable embedded and fill `customApiPostgresql`:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `customApiPostgresql.global.postgresql.auth.hostname` | string | `""` | External host. |
| `customApiPostgresql.global.postgresql.auth.database` | string | `""` | Database name. |
| `customApiPostgresql.global.postgresql.auth.username` | string | `""` | Username. |
| `customApiPostgresql.global.postgresql.auth.servicePort` | int | `5432` | Port. |
| `customApiPostgresql.global.postgresql.secretRef.existingSecret` | string | `""` | K8s secret name containing the password. |
| `customApiPostgresql.global.postgresql.secretRef.passwordSecretKey` | string | `""` | Key within the secret. |

---

## PostgreSQL — Orchestra (`postgresqlOrchestra`)

Same structure as `postgresqlCore`. Key differences:

| Parameter | Default | Description |
|---|---|---|
| `postgresqlOrchestra.enabled` | `true` | Enable embedded Orchestra PostgreSQL. |
| `postgresqlOrchestra.global.postgresql.auth.database` | `"orchestra"` | Database name. |
| `postgresqlOrchestra.global.postgresql.auth.username` | `"orchestra"` | Username. |
| `postgresqlOrchestra.global.postgresql.auth.password` | `"pgsqls3cr3t"` | **Prod** — change this. |

External database override key: `customOrchestraPostgresql` (same structure as `customApiPostgresql`).

---

## PostgreSQL — EventStore (`postgresqlEventStore`)

| Parameter | Default | Description |
|---|---|---|
| `postgresqlEventStore.enabled` | `true` | Deploy embedded PostgreSQL for EventStore. Set to `false` when using external database. |
| `postgresqlEventStore.global.postgresql.auth.database` | `"eventstore"` | Database name. |
| `postgresqlEventStore.global.postgresql.auth.username` | `"eventstore"` | Username. |
| `postgresqlEventStore.global.postgresql.auth.password` | `"eventstore"` | **Prod** — change this. |

External database override key: `customEventstorePostgresql`.

---

## PostgreSQL — Media (`postgresqlMedia`)

| Parameter | Default | Description |
|---|---|---|
| `postgresqlMedia.enabled` | `true` | Deploy embedded PostgreSQL for Media. Set to `false` when using external database. |
| `postgresqlMedia.global.postgresql.auth.database` | `"media"` | Database name. |
| `postgresqlMedia.global.postgresql.auth.username` | `"media"` | Username. |
| `postgresqlMedia.global.postgresql.auth.password` | `"media"` | **Prod** — change this. |

External database override key: `customMediaPostgresql`.

---

## Service Account

| Parameter | Type | Default | Description |
|---|---|---|---|
| `serviceAccount.create` | bool | `true` | Create a Kubernetes ServiceAccount. |
| `serviceAccount.name` | string | `""` | Name override. If empty, generated from fullname. |
| `serviceAccount.annotations` | object | `{}` | Annotations (e.g. IAM role ARN for IRSA). |

---

## Pod Security

| Parameter | Type | Default | Description |
|---|---|---|---|
| `podSecurityContext.fsGroup` | int | `2000` | File system group for volume ownership. |
| `securityContext.runAsNonRoot` | bool | `true` | Enforce non-root execution. |
| `securityContext.runAsUser` | int | `1001` | UID for container processes. |
| `securityContext.capabilities.drop` | list | `[ALL]` | Linux capabilities dropped. |
