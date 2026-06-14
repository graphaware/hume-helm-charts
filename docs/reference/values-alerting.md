# Values Reference: hume-alerting

Complete parameter reference for the `hume-alerting` chart. This chart can be deployed standalone (`helm install hume-alerting oci://...`) or bundled inside `hume-helm` when `alerting.enabled: true`.

When bundled, all parameters listed here are prefixed with `hume-alerting:` in your `hume-helm` values file.

Legend: **Required** = must be set · **Prod** = default is unsafe for production

---

## Global

| Parameter | Type | Default | Description |
|---|---|---|---|
| `replicaCount` | int | `1` | Default replica count (used as fallback for controller and operator). |
| `imagePullSecrets` | list | `[{name: graphaware-docker-creds}]` | Registry pull secret. Must exist in the namespace. |
| `humeAlertingControllerBaseRepository` | string | `"docker.graphaware.com/hume-alerting/"` | Base image repository for the controller. Trailing slash required. |
| `humeAlertingOperatorBaseRepository` | string | `"docker.graphaware.com/hume-alerting/"` | Base image repository for the operator. |
| `humeMessagingProvider` | string | `"kafka"` | Messaging backend: `"kafka"` or `"azure-service-bus"`. |
| `nameOverride` | string | `""` | Partial name override. |
| `fullnameOverride` | string | `""` | Full name override. |
| `nodeSelector` | object | `{}` | Node selector for all pods. |
| `tolerations` | list | `[]` | Pod tolerations. |
| `affinity` | object | `{}` | Pod affinity rules. |

### Autoscaling

| Parameter | Type | Default | Description |
|---|---|---|---|
| `autoscaling.enabled` | bool | `false` | Enable HPA. |
| `autoscaling.minReplicas` | int | `1` | Minimum replicas. |
| `autoscaling.maxReplicas` | int | `100` | Maximum replicas. |
| `autoscaling.targetCPUUtilizationPercentage` | int | `80` | HPA CPU target. |

---

## Messaging: Kafka

### Internal Kafka (embedded)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kafka.internal.enabled` | bool | `true` | Deploy a Bitnami Kafka StatefulSet inside the cluster. |
| `kafka.internal.port` | int | `9092` | Kafka broker port. |
| `kafka.image.registry` | string | `"docker.graphaware.com"` | Kafka image registry. |
| `kafka.image.repository` | string | `"mirror/bitnami/kafka"` | Kafka image repository. |
| `kafka.image.tag` | string | `"3.5.0-debian-11-r7"` | Kafka image tag. |

### External Kafka

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kafka.internal.enabled` | bool | `true` | Set to `false` to use external Kafka. |
| `kafka.external.host` | string | `""` | External Kafka broker hostname. |
| `kafka.external.port` | string | `"9092"` | External Kafka broker port. |
| `kafka.external.security.enabled` | bool | `false` | Enable SASL/SSL for external Kafka. |

### External Kafka SASL/SSL

When `kafka.external.security.enabled: true`, configure these:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kafka.spring_cloud_stream_kafka_binder_configuration_security_protocol` | string | `"SASL_SSL"` | Security protocol. |
| `kafka.spring_cloud_stream_kafka_binder_configuration_sasl_mechanism` | string | `"PLAIN"` | SASL mechanism. |
| `kafka.spring_cloud_stream_kafka_binder_configuration_sasl_jaas_config` | string | `""` | JAAS config string (include credentials here). **Prod** — inject via `controller.env` secretKeyRef instead. |
| `kafka.spring_cloud_stream_kafka_binder_configuration_ssl_endpoint_identification_algorithm` | string | `"https"` | SSL endpoint ID algorithm. |

### Topics

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kafka.topics.prefix` | string | `""` | Prefix for all topic names. Useful for multi-tenant Kafka clusters (e.g. `"prod-"`). |
| `kafka.topics.names.notification` | string | `"notification"` | Notification topic name. |
| `kafka.topics.names.action` | string | `"action"` | Action topic name. |
| `kafka.topics.names.scheduler` | string | `"scheduler"` | Scheduler topic name. |
| `kafka.topics.names.feedback` | string | `"feedback"` | Feedback topic name. |
| `kafka.topics.names.dryRunRequest` | string | `"dryrun-request"` | Dry-run request topic. |
| `kafka.topics.names.dryRunResult` | string | `"dryrun-result"` | Dry-run result topic. |
| `kafka.topics.names.remoteEvents` | string | `"events"` | Remote events topic. |
| `kafka.topics.names.operatorMetrics` | string | `"operator-metrics"` | Operator metrics topic. |

All 8 topics must exist before the alerting services start. With internal Kafka, they are created automatically during provisioning.

---

## Messaging: Azure Service Bus

Used when `humeMessagingProvider: "azure-service-bus"`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `azure.serviceBus.connection_string` | string | `""` | Azure Service Bus connection string. **Prod** — inject via `controller.env` secretKeyRef. |
| `azure.serviceBus.subscription_id` | string | `""` | Azure subscription ID. |
| `azure.serviceBus.topics_names_scheduler` | string | `"scheduler"` | Scheduler topic name. |
| `azure.serviceBus.topics_names_action` | string | `"action"` | Action topic name. |
| `azure.serviceBus.topics_names_notification` | string | `"notification"` | Notification topic name. |
| `azure.serviceBus.topics_names_feedback` | string | `"feedback"` | Feedback topic name. |
| `azure.serviceBus.topics_names_operator_metrics` | string | `"operator-metrics"` | Operator metrics topic. |
| `azure.serviceBus.topics_names_dryRunRequest` | string | `"dryrun-request"` | Dry-run request topic. |
| `azure.serviceBus.topics_names_dryRunResult` | string | `"dryrun-result"` | Dry-run result topic. |

---

## Alerting Controller (`controller`)

The Controller evaluates alert rules and routes results to the Operator.

### Core

| Parameter | Type | Default | Description |
|---|---|---|---|
| `controller.image.name` | string | `"hume-alerting-controller"` | Image name. |
| `controller.image.tag` | string | `""` | Image tag. Defaults to chart `appVersion`. |
| `controller.deployment.replicas` | string | `""` | Replica count. Empty = 1. |
| `controller.logging_format` | string | `"json"` | Log format: `json` or `plain`. |
| `controller.remoteEventsEnabled` | string | `"true"` | Enable remote event processing. |
| `controller.execution_ttl_active` | string | `"true"` | Enable execution TTL cleanup. |
| `controller.execution_ttl_ms` | string | `"60000"` | TTL for completed executions in milliseconds (default 60s). |
| `controller.env` | list | `[]` | Additional environment variables. Use for credentials via secretKeyRef. |
| `controller.extraSecrets` | list | `[]` | Additional secrets to mount. |

### Email (SMTP)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `controller.mail_host` | string | `"smtp"` | SMTP host. |
| `controller.mail_port` | int | `1025` | SMTP port. **Prod** — use 587 (STARTTLS) or 465 (SSL). |
| `controller.mail_username` | string | `""` | SMTP username. |
| `controller.mail_password` | string | `""` | SMTP password. **Prod** — inject via `controller.env` secretKeyRef. |
| `controller.mail_from` | string | `""` | Sender email address. |
| `controller.mail_to` | string | `""` | Default recipient (fallback when no recipient configured in alert rule). |
| `controller.mail_properties_mail_smtp_auth` | string | `""` | SMTP auth property (set to `"true"` when authentication is required). |

### Probes

| Parameter | Type | Default | Description |
|---|---|---|---|
| `controller.probes.livenessProbe.inititalDelaySeconds` | int | `20` | Liveness initial delay. |
| `controller.probes.livenessProbe.periodSeconds` | int | `20` | Liveness interval. |
| `controller.probes.livenessProbe.failureThreshold` | int | `3` | Liveness failure threshold. |
| `controller.probes.readinessProbe.initialDelaySeconds` | int | `10` | Readiness initial delay. |
| `controller.probes.readinessProbe.periodSeconds` | int | `20` | Readiness interval. |
| `controller.probes.readinessProbe.failureThreshold` | int | `20` | Readiness failure threshold. |

### Metrics

| Parameter | Type | Default | Description |
|---|---|---|---|
| `controller.metrics.enabled` | bool | `false` | Enable metrics service. |
| `controller.metrics.service.port` | int | `7001` | Metrics port. |
| `controller.metrics.serviceMonitor.enabled` | bool | `false` | Create Prometheus ServiceMonitor. |
| `controller.metrics.serviceMonitor.labels` | object | `{}` | ServiceMonitor discovery labels. |
| `controller.metrics.serviceMonitor.interval` | string | `"30s"` | Scrape interval. |

---

## Alerting Operator (`operator`)

The Operator receives processed alerts from the Controller and dispatches notifications.

### Core

| Parameter | Type | Default | Description |
|---|---|---|---|
| `operator.image.name` | string | `"hume-alerting-operator"` | Image name. |
| `operator.image.tag` | string | `""` | Image tag. Defaults to chart `appVersion`. |
| `operator.image.pullPolicy` | string | `"Always"` | Image pull policy. |
| `operator.deployment.replicas` | string | `""` | Replica count. |
| `operator.logging_format` | string | `"json"` | Log format: `json` or `plain`. |
| `operator.env` | list | `[]` | Additional environment variables. |
| `operator.extraSecrets` | list | `[]` | Additional secrets. |

### Tuning

| Parameter | Type | Default | Description |
|---|---|---|---|
| `operator.maxTransactionRetry` | int | `0` | Number of transaction retries. |
| `operator.connectionAcquisitionTimeoutSeconds` | int | `3` | Database connection acquisition timeout. |
| `operator.connectionTimeoutSeconds` | int | `3` | Database connection timeout. |
| `operator.maxPollRecords` | int | `1` | Max Kafka records per poll. |
| `operator.maxPollIntervalMs` | int | `600000000` | Max time between Kafka polls (ms). |
| `operator.globalBatchSize` | int | `50000` | Global processing batch size. |
| `operator.slotBatchSize` | int | `25000` | Per-slot batch size. |

### Encryption

The Operator encrypts sensitive alert data using a Java keystore.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `operator.hume_security_encryption_engine` | string | `"keystore"` | Encryption engine type. |
| `operator.hume_security_encryption_keystore_file` | string | `"/opt/hume-keystore"` | Path to keystore file inside the container. |
| `operator.hume_security_encryption_keystore_password` | string | `"changeit"` | Keystore password. **Prod** — must be changed. |
| `operator.hume_security_encryption_keystore_secret_alias` | string | `"secret"` | Secret alias within the keystore. |

### Metrics

Same structure as controller metrics. See `operator.metrics.*`.

---

## PostgreSQL — Alerting Controller

| Parameter | Type | Default | Description |
|---|---|---|---|
| `postgresqlAlertingController.enabled` | bool | `true` | Deploy embedded PostgreSQL for the controller. |
| `postgresqlAlertingController.global.postgresql.auth.database` | string | `"alert-controller"` | Database name. |
| `postgresqlAlertingController.global.postgresql.auth.username` | string | `"alert-controller"` | Username. |
| `postgresqlAlertingController.global.postgresql.auth.password` | string | `"controller-password"` | Password. **Prod** — change this. |
| `postgresqlAlertingController.global.postgresql.auth.servicePort` | int | `5432` | Port. |

**External database** — disable embedded and fill `customAlertingControllerPostgresql`:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `customAlertingControllerPostgresql.global.postgresql.auth.hostname` | string | `""` | External host. |
| `customAlertingControllerPostgresql.global.postgresql.auth.database` | string | `""` | Database name. |
| `customAlertingControllerPostgresql.global.postgresql.auth.username` | string | `""` | Username. |
| `customAlertingControllerPostgresql.global.postgresql.secretRef.existingSecret` | string | `""` | K8s secret name. |
| `customAlertingControllerPostgresql.global.postgresql.secretRef.passwordSecretKey` | string | `""` | Key within the secret. |

---

## PostgreSQL — Alerting Operator

| Parameter | Type | Default | Description |
|---|---|---|---|
| `postgresqlAlertingOperator.enabled` | bool | `true` | Deploy embedded PostgreSQL for the operator. |
| `postgresqlAlertingOperator.global.postgresql.auth.database` | string | `"alert-operator"` | Database name. |
| `postgresqlAlertingOperator.global.postgresql.auth.username` | string | `"alert-operator"` | Username. |
| `postgresqlAlertingOperator.global.postgresql.auth.password` | string | `"operator-password"` | Password. **Prod** — change this. |

External database override key: `customAlertingOperatorPostgresql` (same structure as controller).

---

## Service Account

| Parameter | Type | Default | Description |
|---|---|---|---|
| `serviceAccount.create` | bool | `true` | Create a Kubernetes ServiceAccount. |
| `serviceAccount.name` | string | `""` | Name override. |
| `serviceAccount.annotations` | object | `{}` | Annotations (e.g. IRSA role ARN). |

---

## Ingress (standalone only)

The bundled alerting service is not typically exposed externally. When running standalone and you need an ingress:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ingress.enabled` | bool | `false` | Create an Ingress for the alerting service. |
| `ingress.className` | string | `""` | Ingress class. |
| `ingress.annotations` | object | `{}` | Ingress annotations. |
| `ingress.hosts` | list | see values | Ingress host/path rules. |
| `ingress.tls` | list | `[]` | TLS configuration. |

---

## Resources

No default resource requests/limits are set. Set these for production:

```yaml
controller:
  resources:
    requests:
      cpu: "200m"
      memory: "512Mi"
    limits:
      cpu: "500m"
      memory: "1Gi"

operator:
  resources:
    requests:
      cpu: "200m"
      memory: "512Mi"
    limits:
      cpu: "500m"
      memory: "1Gi"
```
