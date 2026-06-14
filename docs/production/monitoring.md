# Monitoring and Observability

Enable Prometheus metrics, ServiceMonitors, and alert rules for all Hume services.

---

## Prerequisites

- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) (or `kube-prometheus-stack`) installed in the cluster
- ServiceMonitors are discovered by Prometheus via label selectors — the standard label is `release: kube-prometheus-stack`

Confirm the Prometheus Operator CRDs exist:

```bash
kubectl get crd servicemonitors.monitoring.coreos.com
```

---

## Enabling Metrics Per Service

All Hume services expose metrics at port `7001` via `/actuator/prometheus`. Each service has an independent `metrics` block.

Add to your values file:

```yaml
api:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

orchestra:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

eventstore:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack
      basicAuth:
        enabled: true
        secretName: eventstore-credentials-secret  # see EventStore docs

media:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

maestro:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack
```

> EventStore's metrics endpoint requires HTTP basic auth. Create the secret before enabling — see [EventStore Configuration](../configuration/eventstore.md).

---

## Alerting ServiceMonitors

Pass alerting monitor config through the `hume-alerting` sub-chart key:

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

## PostgreSQL Metrics (Embedded Databases)

Enable the Bitnami `postgres-exporter` sidecar for each embedded PostgreSQL instance:

```yaml
postgresqlCore:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

postgresqlOrchestra:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

postgresqlEventStore:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

postgresqlMedia:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack
```

---

## Alert Rules

Deploy a `PrometheusRule` to alert on service unavailability. Apply this manifest to your cluster (it is not managed by the Helm chart):

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: hume-alerts
  namespace: hume
  labels:
    release: kube-prometheus-stack
spec:
  groups:
    - name: hume.availability
      rules:
        - alert: HumeApiDown
          expr: kube_deployment_status_replicas_available{deployment="hume-api", namespace="hume"} < 1
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "Hume API has no available replicas"
            description: "hume-api in namespace hume has been unavailable for more than 2 minutes."

        - alert: HumeOrchestraDown
          expr: kube_statefulset_status_replicas_ready{statefulset="hume-orchestra", namespace="hume"} < 1
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "Hume Orchestra has no ready replicas"

        - alert: HumeEventstoreDown
          expr: kube_deployment_status_replicas_available{deployment="hume-eventstore", namespace="hume"} < 1
          for: 2m
          labels:
            severity: error
          annotations:
            summary: "Hume EventStore has no available replicas"

        - alert: HumeMediaDown
          expr: kube_statefulset_status_replicas_ready{statefulset="hume-media", namespace="hume"} < 1
          for: 2m
          labels:
            severity: error
          annotations:
            summary: "Hume Media has no ready replicas"

        - alert: HumeAlertingControllerDown
          expr: kube_deployment_status_replicas_available{deployment="hume-alerting-controller", namespace="hume"} < 1
          for: 2m
          labels:
            severity: error
          annotations:
            summary: "Hume Alerting Controller is down"

        - alert: HumeAlertingOperatorDown
          expr: kube_deployment_status_replicas_available{deployment="hume-alerting-operator", namespace="hume"} < 1
          for: 2m
          labels:
            severity: error
          annotations:
            summary: "Hume Alerting Operator is down"
```

Apply it:

```bash
kubectl apply -f hume-alerts.yaml
```

---

## Structured (JSON) Logging

Switch services to JSON format for ingestion by Loki, Elasticsearch, or Datadog:

```yaml
api:
  env:
    - name: hume.logging.format
      value: json

orchestra:
  env:
    - name: hume.logging.format
      value: json

eventstore:
  env:
    - name: hume.logging.format
      value: json
```

---

## Audit Logging

To include audit events in the standard log stream (useful for centralised logging), mount a custom log4j2 configuration. See the full example in the [main README](../../README.md#audit-logging-to-console-logs) — the key env vars are:

```yaml
api:
  env:
    - name: hume.security.audit.enabled
      value: 'true'
    - name: hume.security.audit.appender
      value: 'console_plain'
    - name: hume.logging.config.location
      value: "/conf/server-logs.xml"
  volumes:
    - configMap:
        name: api-log4j2-configmap
      name: api-log4j2-volume
  volumeMounts:
    - mountPath: /conf
      name: api-log4j2-volume
```

---

## Verify

```bash
# List ServiceMonitors
kubectl get servicemonitor -n hume

# Check Prometheus has picked them up (port-forward if needed)
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring
# Then visit http://localhost:9090/targets and look for hume jobs

# Check PrometheusRules
kubectl get prometheusrule -n hume

# Scrape metrics manually from a pod
kubectl exec -it deployment/hume-api -n hume -- \
  curl -s http://localhost:7001/actuator/prometheus | head -20
```

Expected output: ServiceMonitors listed for each enabled service; Prometheus targets page shows all Hume targets as `UP`.

---

## Next Steps

- [High Availability](high-availability.md) — Scale services for production resilience
- [Security](security.md) — Harden secrets and pod permissions
