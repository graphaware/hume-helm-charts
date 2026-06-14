# Troubleshooting

Symptom-driven reference for diagnosing and fixing common Hume deployment problems.

---

## Pod Stuck in ImagePullBackOff

**Symptom:** One or more Hume pods show `ImagePullBackOff` or `ErrImagePull`.

**Diagnose:**

```bash
kubectl describe pod <pod-name> -n hume | grep -A 10 Events
```

Look for: `failed to pull image ... unauthorized` or `secret "graphaware-docker-creds" not found`.

**Fix:**

The `graphaware-docker-creds` secret is missing or has expired credentials.

```bash
# Check if the secret exists in the right namespace
kubectl get secret graphaware-docker-creds -n hume

# Recreate it (delete first if it exists with bad credentials)
kubectl delete secret graphaware-docker-creds -n hume
kubectl create secret docker-registry graphaware-docker-creds \
  --docker-server='docker.graphaware.com' \
  --docker-username='<username>' \
  --docker-password='<password>' \
  -n hume

# Restart the affected pods
kubectl rollout restart deployment/hume-api -n hume
```

---

## Pod Stuck in Init:0/N or Pending

**Symptom:** Pod shows `Init:0/1` or stays `Pending` indefinitely.

**Diagnose:**

```bash
kubectl describe pod <pod-name> -n hume
```

Look at `Init Containers` status and the `Events` section at the bottom.

**Likely causes and fixes:**

- **PostgreSQL not ready:** The API and Orchestra have init containers that wait for their database. Check PostgreSQL pods:
  ```bash
  kubectl get pods -n hume | grep postgres
  kubectl logs postgresql-core-0 -n hume
  ```

- **PVC not bound:** No StorageClass matches the requested storage class name:
  ```bash
  kubectl get pvc -n hume
  kubectl describe pvc <pvc-name> -n hume
  ```
  Fix by setting the correct `storageClass` in values or creating the required StorageClass.

---

## hume-api in CrashLoopBackOff

**Symptom:** `hume-api` pod keeps restarting.

**Diagnose:**

```bash
kubectl logs deployment/hume-api -n hume --previous
```

**What to look for:**

| Log message | Cause |
|---|---|
| `Connection refused` | PostgreSQL not accepting connections |
| `FATAL: database "hume" does not exist` | Database not created |
| `password authentication failed` | Wrong credentials |
| `Unable to connect to Neo4j` | Neo4j not reachable or wrong bolt URL |

**Fix — database connection:**

```bash
# See what connection string the pod is using
kubectl exec -it deployment/hume-api -n hume -- env | grep -E "datasource|spring"
```

If using external PostgreSQL, verify hostname, port, database name, and credentials match what's in the database server.

**Fix — startup too slow:** If the database is slow on first run (schema creation takes time), increase the startup probe:

```yaml
api:
  probes:
    startupProbe:
      initialDelaySeconds: 30
      periodSeconds: 5
      failureThreshold: 120  # allows 600s for startup
```

---

## hume-orchestra-0 Not Ready

**Symptom:** `hume-orchestra-0` stays in `0/1 Running` or restarts.

**Diagnose:**

```bash
kubectl logs statefulset/hume-orchestra -n hume
kubectl describe pod hume-orchestra-0 -n hume
```

**Likely causes:**

- **PostgreSQL not ready:** `kubectl get pods -n hume | grep postgresql-orchestra`
- **PVC not bound:** `kubectl get pvc data-hume-orchestra-0 -n hume`
- **OOMKilled:** Check `kubectl describe pod hume-orchestra-0 -n hume` for `OOMKilled` in the last state. Orchestra needs at least 2Gi memory — set proper limits (see [High Availability](../production/high-availability.md)).

---

## Cannot Log In to Hume UI

**Symptom:** Browser shows `401 Unauthorized` or bounces between Hume and Keycloak in a redirect loop.

**Diagnose:**

```bash
# Is Keycloak in use?
kubectl get pods -n hume | grep keycloak

# Check browser console for network errors
# Look for failed requests to /api/v1/auth or Keycloak /auth endpoints
```

**Fix — native auth:**
Verify admin credentials in your values match what was set at first startup:

```yaml
api:
  admin:
    username: "admin@hume.k8s"
    password: "password"
```

If you changed credentials after first boot, reset the password in the Hume UI directly.

**Fix — Keycloak redirect loop:**
Both the API and Web must reference the same Keycloak URL, and it must be accessible from the browser (not just inside the cluster).

```yaml
api:
  env:
    - name: keycloak.auth-server-url
      value: "https://<keycloak-external-url>/auth"
    - name: keycloak.realm
      value: "<realm-name>"
    - name: keycloak.resource
      value: "hume-web"
web:
  env:
    - name: KEYCLOAK_URL
      value: "https://<keycloak-external-url>/auth"
    - name: KEYCLOAK_REALM
      value: "<realm-name>"
    - name: KEYCLOAK_CLIENT
      value: "hume-web"
```

Also verify in Keycloak that `https://hume-web.<baseDomain>/*` is listed as a valid redirect URI for the client.

---

## Media Uploads Fail

**Symptom:** File uploads in Hume UI fail or Media service returns errors.

**Diagnose:**

```bash
kubectl logs statefulset/hume-media -n hume
kubectl exec -it statefulset/hume-media -n hume -- env | grep -iE "s3|minio|upload|storage"
```

**Likely causes:**

- **S3 credentials missing or wrong:** Check `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars, or that the IRSA role annotation is correct on the service account.
- **Bucket does not exist:** Create the bucket and set a policy allowing `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`.
- **Wrong upload path:** `media.storage.s3.uploadPath` must be the full S3 URL (e.g., `s3://bucket-name/prefix/upload`).

**Fix:**

```bash
# Test S3 access from inside the media pod
kubectl exec -it statefulset/hume-media -n hume -- \
  aws s3 ls s3://<bucket-name>/ --region eu-west-1
```

---

## Orchestra Webhooks Not Triggering

**Symptom:** External systems posting to the Orchestra webhook URL receive no response or a connection error.

**Diagnose:**

```bash
kubectl get svc -n hume | grep webhook
# Expected: hume-orchestra-webhook-0   ClusterIP  ...  8101/TCP
```

**Fix:**

The webhook service exists per replica but has no ingress by default. Add an ingress pointing to it:

```yaml
# Additional ingress in your values or as a separate manifest
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hume-orchestra-webhook
  namespace: hume
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
    - host: orchestra-webhook.<baseDomain>
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: hume-orchestra-webhook-0
                port:
                  number: 8101
```

Verify connectivity from inside the cluster:

```bash
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n hume -- \
  curl -v http://hume-orchestra-webhook-0:8101/actuator/health
```

---

## Alerting Notifications Not Sent

**Symptom:** Alert rules trigger but no emails or webhook calls are received.

**Diagnose:**

```bash
kubectl logs deployment/hume-alerting-controller -n hume | tail -100
```

**Kafka connection errors:**

```bash
# Check Kafka is running
kubectl get pods -n hume | grep kafka

# List Kafka topics (from inside the cluster)
kubectl exec -it kafka-0 -n hume -- \
  kafka-topics.sh --bootstrap-server localhost:9092 --list
```

If topics are missing, check `kafka.topics.prefix` in alerting values — topic names must match what the chart creates.

**SMTP errors:**

```bash
# Test SMTP port reachability from inside the controller pod
kubectl exec -it deployment/hume-alerting-controller -n hume -- \
  nc -zv <smtp-host> <smtp-port>
```

Verify credentials in the controller values:

```yaml
hume-alerting:
  controller:
    mail_host: "smtp.example.com"
    mail_port: 587
    mail_username: "<username>"
    mail_password: "<password>"
```

---

## Maestro Returns 500 or No Response

**Symptom:** Maestro endpoint returns errors or the Hume AI chat feature doesn't respond.

**Diagnose:**

```bash
kubectl logs deployment/hume-maestro -n hume | tail -50
```

**Common causes:**

- `remoteApi.enabled: false` — Maestro requires the Remote API. Set `api.remoteApi.enabled: true`.
- Wrong LLM credentials — Check OpenAI key or Azure OpenAI endpoint/deployment name.
- Ollama not reachable — Verify `maestro.ollama.base-url` points to a running Ollama instance.

**Verify provider connectivity:**

```bash
kubectl exec -it deployment/hume-maestro -n hume -- \
  curl -v http://<ollama-host>:11434/api/tags
```

---

## helm upgrade Fails with "Immutable Field" Error

**Symptom:** `helm upgrade` reports `field is immutable` for Deployment or StatefulSet selectors.

**Cause:** This is the v2.27.0 label standardization change. Kubernetes does not allow changing `.spec.selector` on existing resources.

**Fix:** Delete the affected resources before upgrading (Helm will recreate them):

```bash
kubectl delete deployment hume-api hume-web hume-eventstore -n hume
kubectl delete statefulset hume-orchestra hume-media -n hume
# Then rerun:
helm upgrade hume oci://docker.graphaware.com/public/hume --version <new-version> -n hume -f values.yaml
```

See [Upgrade Guide](../installation/upgrade-guide.md) for full v2.27.0 migration steps.

---

## Diagnostic Commands Reference

```bash
# All Hume pods and their status
kubectl get pods -n hume

# Pod logs (current run)
kubectl logs <pod-name> -n hume

# Pod logs (previous crash)
kubectl logs <pod-name> -n hume --previous

# Describe a pod — events, resource pressure, init container status
kubectl describe pod <pod-name> -n hume

# Environment variables in a running pod
kubectl exec -it <pod-name> -n hume -- env | sort

# Persistent volume claims
kubectl get pvc -n hume
kubectl describe pvc <pvc-name> -n hume

# Services and endpoints
kubectl get svc -n hume
kubectl get endpoints -n hume

# Ingress rules
kubectl get ingress -n hume
kubectl describe ingress -n hume

# Run Helm's built-in tests
helm test hume -n hume

# Port-forward for direct access
kubectl port-forward service/hume-api 8080:8080 -n hume
kubectl port-forward service/hume-web 8081:8081 -n hume

# Resource consumption
kubectl top pods -n hume

# Force rolling restart
kubectl rollout restart deployment/hume-api -n hume

# Interactive shell in a pod
kubectl exec -it deployment/hume-api -n hume -- /bin/bash

# Generate a heap dump (Java services, PID is always 1)
kubectl exec -it hume-orchestra-0 -n hume -- \
  jcmd 1 GC.heap_dump /tmp/heapdump-$(date +%s).hprof

# Copy heap dump to local machine
kubectl cp hume/hume-orchestra-0:/tmp/heapdump-<timestamp>.hprof ./heapdump.hprof
```

---

## Next Steps

- [Upgrade Guide](../installation/upgrade-guide.md) — Version-specific migration steps
- [Monitoring](../production/monitoring.md) — Set up alerts to catch issues before they become incidents
