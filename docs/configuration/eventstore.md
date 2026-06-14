# EventStore Configuration

EventStore is a required Hume service that records an immutable, append-only audit log of all platform events — user actions, graph changes, and API calls — and is essential for compliance, audit trails, and event replay.

EventStore and its PostgreSQL database are enabled by default. Hume API automatically discovers the EventStore service and connects to it using the default credentials.

---

## Change Default Credentials

The default credentials (`hume` / `megaSecretPwd`) must be changed before going to production:

```yaml
eventstore:
  enabled: true
  username: hume
  password: "<strong-password>"

postgresqlEventStore:
  enabled: true
  global:
    postgresql:
      auth:
        database: eventstore
        username: eventstore
        password: "<strong-db-password>"
```

> **Production callout:** The default password `megaSecretPwd` is publicly documented. Change it before any deployment that is reachable from a network.

---

## API Integration

When EventStore is enabled, the Hume API connects to it automatically at `http://hume-eventstore:9090` using HTTP basic auth with the credentials configured under `eventstore.username` and `eventstore.password`. No additional API configuration is needed — the API configmap picks up EventStore settings from the chart.

---

## Use External PostgreSQL

To connect EventStore to an external PostgreSQL database instead of the embedded Bitnami instance:

```yaml
eventstore:
  enabled: true
  password: "<eventstore-service-password>"

# Disable the embedded PostgreSQL
postgresqlEventStore:
  enabled: false

# Provide external connection details
customEventstorePostgresql:
  global:
    postgresql:
      auth:
        database: "eventstore"
        hostname: "<db-host>"
        username: "<db-username>"
        servicePort: 5432
      secretRef:
        existingSecret: "eventstore-db-credentials"   # name of the Kubernetes secret
        passwordSecretKey: "password"                 # key within that secret
```

Create the credentials secret:

```bash
kubectl create secret generic eventstore-db-credentials \
  --from-literal=password='<db-password>' \
  -n hume
```

---

## Prometheus Metrics

EventStore exposes metrics on port `7001` at `/actuator/prometheus`. To enable scraping:

```yaml
eventstore:
  enabled: true
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      interval: 30s
      labels:
        release: kube-prometheus-stack   # must match your Prometheus operator's label selector
```

### ServiceMonitor with Basic Auth

The EventStore metrics endpoint is protected by basic auth. If your Prometheus operator requires basic auth credentials in the ServiceMonitor:

```yaml
eventstore:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack
      basicAuth:
        enabled: true
        secretName: eventstore-credentials-secret
```

Create the secret that the ServiceMonitor references:

```bash
kubectl create secret generic eventstore-credentials-secret \
  --from-literal=username=hume \
  --from-literal=password='<your-eventstore-password>' \
  -n hume
```

---

## Inject Custom Environment Variables

Use `eventstore.env` to pass additional environment variables or override defaults:

```yaml
eventstore:
  enabled: true
  env:
    - name: spring.datasource.username
      valueFrom:
        secretKeyRef:
          name: eventstore-postgres-db-username
          key: db-username
```

---

## Verify It Works

Check that the EventStore pod started successfully:

```bash
kubectl get pods -n hume -l app.kubernetes.io/name=hume-eventstore
```

Expected output:

```
NAME                              READY   STATUS    RESTARTS   AGE
hume-eventstore-6b9f7c8d4-xr2pq  1/1     Running   0          2m
```

Confirm the service is listening:

```bash
kubectl logs -l app.kubernetes.io/name=hume-eventstore -n hume | grep -i "started\|listening\|running"
```

---

## Next Steps

- [Media Configuration](media.md) — configure binary file storage
- [Databases](databases.md) — using external PostgreSQL for all services
- [Monitoring](../production/monitoring.md) — Prometheus ServiceMonitor setup
