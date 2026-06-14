# Alerting

Hume Alerting is an optional, rule-based alert engine: the Controller evaluates alert conditions against graph data, and the Operator dispatches notifications via email, webhook, or other channels, using Kafka or Azure Service Bus as the message bus between them.

> **Licence required:** Alerting is a separately licensed Hume module. Contact your GraphAware account team to obtain an Alerting licence before enabling this service.

---

## Deployment Modes

Alerting can be deployed in two ways.

### Mode 1: Sub-chart (bundled with hume-helm)

The simplest approach. Add these values to your `hume-helm` values file:

```yaml
alerting:
  enabled: true
  uri: "http://hume-alerting"   # how the API reaches the alerting controller

hume-alerting:                  # settings passed through to the hume-alerting sub-chart
  kafka:
    internal:
      enabled: true             # deploy embedded Kafka alongside alerting
  controller:
    mail_host: "<smtp-host>"
    mail_port: 587
    mail_username: "<smtp-username>"
    mail_password: "<smtp-password>"
    mail_from: "hume-alerts@<your-domain>"
```

### Mode 2: Standalone Chart

Install alerting separately from the core Hume chart. Useful when you want independent lifecycle management or when Alerting is deployed in a different namespace.

```bash
helm install hume-alerting oci://docker.graphaware.com/public/hume-alerting \
  --version 3.0.0 \
  -n hume \
  -f alerting-values.yaml
```

When using standalone mode, point the Hume API at the standalone service:

```yaml
# in your hume-helm values.yaml
alerting:
  enabled: false   # do not deploy the sub-chart
  uri: "http://hume-alerting.<alerting-namespace>.svc.cluster.local"
```

---

## Messaging Backend

### Internal Kafka (Default)

Use the embedded Bitnami Kafka deployed by the chart. Best for single-cluster deployments where you want minimal external dependencies:

```yaml
hume-alerting:
  kafka:
    internal:
      enabled: true
```

### External Kafka

Point Alerting at a Kafka cluster you manage:

```yaml
hume-alerting:
  kafka:
    internal:
      enabled: false
    external:
      host: "<kafka-broker-host>"
      port: "9092"
      security:
        enabled: true
    spring_cloud_stream_kafka_binder_configuration_security_protocol: "SASL_SSL"
    spring_cloud_stream_kafka_binder_configuration_sasl_mechanism: "PLAIN"
    spring_cloud_stream_kafka_binder_configuration_sasl_jaas_config: >
      org.apache.kafka.common.security.plain.PlainLoginModule required
      username="<kafka-username>" password="<kafka-password>";
    spring_kafka_properties_security_protocol: "SASL_SSL"
    spring_kafka_properties_sasl_mechanism: "PLAIN"
    spring_kafka_properties_sasl_jaas_config: >
      org.apache.kafka.common.security.plain.PlainLoginModule required
      username="<kafka-username>" password="<kafka-password>";
```

### Azure Service Bus

Switch the messaging provider to Azure Service Bus:

```yaml
hume-alerting:
  humeMessagingProvider: "azure-service-bus"
  azure:
    serviceBus:
      connection_string: "<connection-string>"
      subscription_id: "<subscription-id>"
      topics_names_scheduler: "scheduler"
      topics_names_action: "action"
      topics_names_notification: "notification"
      topics_names_feedback: "feedback"
      topics_names_operator_metrics: "operator-metrics"
      topics_names_dryRunRequest: "dryrun-request"
      topics_names_dryRunResult: "dryrun-result"
```

---

## Topic Naming

Alerting requires 8 Kafka topics. By default, topics use bare names. In shared Kafka clusters or multi-environment setups, use a prefix:

```yaml
hume-alerting:
  kafka:
    topics:
      prefix: "prod-"   # topics become: prod-notification, prod-action, etc.
```

The 8 required topics (with prefix applied):

| Topic key | Default name |
|---|---|
| `notification` | `notification` |
| `action` | `action` |
| `scheduler` | `scheduler` |
| `feedback` | `feedback` |
| `dryRunRequest` | `dryrun-request` |
| `dryRunResult` | `dryrun-result` |
| `remoteEvents` | `events` |
| `operatorMetrics` | `operator-metrics` |

---

## SMTP (Email) Configuration

Configure the Controller to send email notifications:

```yaml
hume-alerting:
  controller:
    mail_host: "smtp.example.com"
    mail_port: 587
    mail_username: "<smtp-username>"
    mail_password: "<smtp-password>"
    mail_from: "hume-alerts@example.com"
```

To override using a Kubernetes Secret (recommended for production):

```yaml
hume-alerting:
  controller:
    env:
      - name: spring.mail.password
        valueFrom:
          secretKeyRef:
            name: smtp-credentials
            key: password
```

---

## External PostgreSQL for Alerting

By default, Alerting deploys embedded PostgreSQL for both Controller and Operator. For production, use external databases:

```yaml
hume-alerting:
  # Controller database
  postgresqlAlertingController:
    enabled: false
  customAlertingControllerPostgresql:
    global:
      postgresql:
        auth:
          database: "alert_controller"
          hostname: "<db-host>"
          username: "<db-username>"
          servicePort: 5432
        secretRef:
          existingSecret: "alerting-db-credentials"
          passwordSecretKey: "controller-password"

  # Operator database
  postgresqlAlertingOperator:
    enabled: false
  customAlertingOperatorPostgresql:
    global:
      postgresql:
        auth:
          database: "alert_operator"
          hostname: "<db-host>"
          username: "<db-username>"
          servicePort: 5432
        secretRef:
          existingSecret: "alerting-db-credentials"
          passwordSecretKey: "operator-password"
```

Create the credentials secret:

```bash
kubectl create secret generic alerting-db-credentials \
  --from-literal=controller-password='<controller-db-password>' \
  --from-literal=operator-password='<operator-db-password>' \
  -n hume
```

---

## Operator Encryption Keystore

The Operator encrypts sensitive alert payload data using a Java keystore. The default keystore password (`changeit`) must be changed for production:

```yaml
hume-alerting:
  operator:
    hume_security_encryption_keystore_password: "<strong-keystore-password>"
    hume_security_encryption_keystore_secret_alias: secret
```

> **Production callout:** `changeit` is a well-known default. Any deployment with encrypted alert data must use a custom password.

---

## Execution TTL

Completed alert executions are cleaned up after a configurable TTL (default 60 seconds). Increase this if you need to inspect historical execution records in the UI:

```yaml
hume-alerting:
  controller:
    execution_ttl_active: "true"
    execution_ttl_ms: "3600000"   # 1 hour
```

---

## Prometheus Metrics

Enable metrics scraping for both components:

```yaml
hume-alerting:
  controller:
    metrics:
      enabled: true
      serviceMonitor:
        enabled: true
        labels:
          release: kube-prometheus-stack

  operator:
    metrics:
      enabled: true
      serviceMonitor:
        enabled: true
        labels:
          release: kube-prometheus-stack
```

---

## Complete Example (Sub-chart, Internal Kafka)

```yaml
# hume-helm values.yaml

alerting:
  enabled: true
  uri: "http://hume-alerting"

hume-alerting:
  kafka:
    internal:
      enabled: true
    topics:
      prefix: ""

  controller:
    mail_host: "smtp.example.com"
    mail_port: 587
    mail_username: "<smtp-username>"
    mail_password: "<smtp-password>"
    mail_from: "hume-alerts@example.com"
    execution_ttl_active: "true"
    execution_ttl_ms: "60000"
    metrics:
      enabled: true
      serviceMonitor:
        enabled: true
        labels:
          release: kube-prometheus-stack

  operator:
    hume_security_encryption_keystore_password: "<strong-keystore-password>"
    metrics:
      enabled: true
      serviceMonitor:
        enabled: true
        labels:
          release: kube-prometheus-stack

  postgresqlAlertingController:
    enabled: false
  customAlertingControllerPostgresql:
    global:
      postgresql:
        auth:
          database: "alert_controller"
          hostname: "<db-host>"
          username: "<db-username>"
          servicePort: 5432
        secretRef:
          existingSecret: "alerting-db-credentials"
          passwordSecretKey: "controller-password"

  postgresqlAlertingOperator:
    enabled: false
  customAlertingOperatorPostgresql:
    global:
      postgresql:
        auth:
          database: "alert_operator"
          hostname: "<db-host>"
          username: "<db-username>"
          servicePort: 5432
        secretRef:
          existingSecret: "alerting-db-credentials"
          passwordSecretKey: "operator-password"
```

---

## Verify It Works

Check both Alerting pods are running:

```bash
kubectl get pods -n hume | grep alerting
```

Expected output:

```
hume-alerting-controller-6b9f7c8d4-xr2pq   1/1     Running   0          3m
hume-alerting-operator-7d9c84b5f-lkp2q      1/1     Running   0          3m
```

If using internal Kafka, verify topics were created (replace pod name with your Kafka pod):

```bash
kubectl exec -n hume kafka-0 -- \
  kafka-topics.sh --bootstrap-server localhost:9092 --list
```

You should see the 8 alerting topics in the output.

---

## Next Steps

- [Databases](../configuration/databases.md) — external PostgreSQL for all services
- [Monitoring](../production/monitoring.md) — Prometheus alert rules for alerting components
- [High Availability](../production/high-availability.md) — multi-replica alerting setup
