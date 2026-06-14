# High Availability

Configure Hume for production resilience with Orchestra clustering, autoscaling, and appropriate resource limits.

---

## Orchestra Clustering

By default, Orchestra runs as a single StatefulSet pod. For production, run 3 replicas with automatic leader election (zookeeper-less since v2.19.0).

```yaml
orchestra:
  deployment:
    replicas: 3
  cluster:
    enabled: true
```

**What this does:** Orchestra pods elect a leader automatically. The leader handles job scheduling and execution; followers replicate state. If the leader pod is lost, election happens within seconds.

**Anti-affinity:** Since v2.27.0, Orchestra pods are configured with anti-affinity rules by default — they will spread across nodes automatically. No additional configuration needed.

**Storage in cluster mode:** Each Orchestra replica gets its own PVC (StatefulSet behavior). Size all replicas the same:

```yaml
orchestra:
  persistence:
    size: 10Gi
    storageClass: "gp3"
```

**Webhook routing in cluster mode:** Each replica exposes its own webhook service (`hume-orchestra-webhook-0`, `hume-orchestra-webhook-1`, `hume-orchestra-webhook-2`). If you use webhooks, you need a separate ingress rule per replica — or a proxy that load-balances across them. See [Ingress](../configuration/ingress.md) for the ingress pattern.

---

## API Horizontal Pod Autoscaler

The API and Web services support HPA. Enable metrics first — HPA requires them:

```yaml
api:
  metrics:
    enabled: true

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

The HPA applies globally. To disable it for specific services, do not set replicas via autoscaling — instead pin them with `deployment.replicas`.

---

## Resource Requests and Limits

Set requests and limits to prevent resource contention. These values are based on real-world deployments:

| Service | CPU request | CPU limit | Memory request | Memory limit |
|---|---|---|---|---|
| Hume API | 500m | 1000m | 2500Mi | 3000Mi |
| Hume Orchestra | 500m | 1000m | 4000Mi | 4400Mi |
| Hume EventStore | 200m | 500m | 6000Mi | 6000Mi |
| Hume Media | 500m | 1000m | 2000Mi | 2000Mi |
| Hume Web | 100m | 200m | 128Mi | 256Mi |

Set per service in values:

```yaml
api:
  resources:
    requests:
      cpu: "500m"
      memory: "2500Mi"
    limits:
      cpu: "1000m"
      memory: "3000Mi"

orchestra:
  resources:
    requests:
      cpu: "500m"
      memory: "4000Mi"
    limits:
      cpu: "1000m"
      memory: "4400Mi"

eventstore:
  resources:
    requests:
      cpu: "200m"
      memory: "6000Mi"
    limits:
      cpu: "500m"
      memory: "6000Mi"

media:
  resources:
    requests:
      cpu: "500m"
      memory: "2000Mi"
    limits:
      cpu: "1000m"
      memory: "2000Mi"
```

> **Production callout:** Orchestra and EventStore are memory-hungry JVM services. Setting limits too low causes OOMKilled pods. Start with these values and adjust based on observed usage (`kubectl top pods -n hume`).

---

## Pod Anti-Affinity

Anti-affinity for API, Orchestra, and Alerting is pre-configured since v2.27.0. Pods spread across nodes without any additional configuration.

To customize — for example, to enforce zone-level spreading:

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app.kubernetes.io/name: hume-api
        topologyKey: topology.kubernetes.io/zone
```

---

## Node Selection (AWS example)

To pin Orchestra to on-demand nodes and avoid spot interruptions:

```yaml
orchestra:
  nodeSelector:
    karpenter.sh/capacity-type: on-demand
```

---

## Startup and Liveness Probes

The default startup probe allows up to 300 seconds for a service to start (`failureThreshold: 60`, `periodSeconds: 5`). In slow environments with large databases, increase this:

```yaml
api:
  probes:
    startupProbe:
      initialDelaySeconds: 30
      periodSeconds: 5
      failureThreshold: 120  # 600s max startup
```

---

## Verify

```bash
# Check pods are spread across nodes
kubectl get pods -n hume -o wide

# Check Orchestra is in a healthy cluster
kubectl logs hume-orchestra-0 -n hume | grep -i "leader\|cluster\|elected"

# Check HPA status
kubectl get hpa -n hume

# Check resource usage
kubectl top pods -n hume
```

Expected: Orchestra pods on different nodes; HPA reporting current/desired replicas; no OOMKilled events in `kubectl describe pods`.

---

## Next Steps

- [Monitoring](monitoring.md) — Set up Prometheus metrics and alerting
- [Backup and Restore](backup-restore.md) — Back up Orchestra PVCs and databases
