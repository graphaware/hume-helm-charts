# Media Configuration

Hume Media is a required service that stores binary files — images, documents, and other attachments — linked to graph entities, enabling rich media integration throughout the Hume UI.

Media and its PostgreSQL database are enabled by default. The API connects to the Media service automatically at `http://hume-media:8008`.

The only required configuration step is choosing a storage backend for your files.

---

## Choose a Storage Backend

One storage backend must be enabled. Media supports three options:

### Local Filesystem

Simple setup for development or single-node deployments. Files are stored in a PersistentVolume on the Media StatefulSet.

```yaml
media:
  enabled: true
  storage:
    local:
      enabled: true
      uploadPath: "/data/upload"
      readyPath: "/data/ready"
```

> **Not suitable for multi-replica deployments** — the PVC is `ReadWriteOnce` by default, meaning only one pod can mount it at a time.

### Amazon S3

Recommended for production on AWS:

```yaml
media:
  enabled: true
  storage:
    s3:
      enabled: true
      uploadPath: "s3://<bucket-name>/upload"
      readyPath: "s3://<bucket-name>/ready"
```

AWS credentials must be provided via the pod's service account (IAM role for service accounts is the recommended approach on EKS) or via environment variables:

```yaml
media:
  env:
    - name: AWS_ACCESS_KEY_ID
      valueFrom:
        secretKeyRef:
          name: aws-media-credentials
          key: access-key-id
    - name: AWS_SECRET_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: aws-media-credentials
          key: secret-access-key
    - name: AWS_REGION
      value: "<aws-region>"
```

Minimum IAM policy required:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::<bucket-name>",
        "arn:aws:s3:::<bucket-name>/*"
      ]
    }
  ]
}
```

### MinIO

Works in any Kubernetes environment — useful when you cannot use a cloud object storage service:

```yaml
media:
  enabled: true
  storage:
    minio:
      enabled: true
      uploadPath: "<minio-bucket>/upload"
      readyPath: "<minio-bucket>/ready"
      accessKey: "<minio-access-key>"
      accessSecret: "<minio-secret-key>"
```

---

## Change Default Credentials

The default credentials (`hume` / `megaSecretPwd`) and API key (`hms_api_key`) must be changed in production:

```yaml
media:
  username: hume
  password: "<strong-password>"
  security:
    apiKey: "<your-api-key>"
    native:
      jwt:
        signingKey: "<random-256-bit-key>"
```

Generate a secure JWT signing key:

```bash
openssl rand -hex 32
```

> **Production callout:** The default API key `hms_api_key` and password `megaSecretPwd` are publicly documented. Change both before any networked deployment.

---

## Configure Maximum File Size

The default maximum upload size is 200MB. To change it:

```yaml
media:
  storage:
    file:
      max_size: "500MB"
```

---

## Use External PostgreSQL

```yaml
media:
  enabled: true

# Disable the embedded PostgreSQL
postgresqlMedia:
  enabled: false

# Provide external connection details
customMediaPostgresql:
  global:
    postgresql:
      auth:
        database: "media"
        hostname: "<db-host>"
        username: "<db-username>"
        servicePort: 5432
      secretRef:
        existingSecret: "media-db-credentials"
        passwordSecretKey: "password"
```

Create the credentials secret:

```bash
kubectl create secret generic media-db-credentials \
  --from-literal=password='<db-password>' \
  -n hume
```

---

## Resource Configuration

Media is resource-intensive. The default requests are `500m` CPU and `2048Mi` memory:

```yaml
media:
  resources:
    requests:
      cpu: "500m"
      memory: "2048Mi"
    limits:
      cpu: "1000m"
      memory: "4096Mi"
```

---

## Prometheus Metrics

```yaml
media:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      interval: 30s
      labels:
        release: kube-prometheus-stack
```

---

## Complete Example

A typical production-ready Media configuration using S3:

```yaml
media:
  enabled: true
  password: "<strong-password>"
  security:
    apiKey: "<your-api-key>"
    native:
      jwt:
        signingKey: "<random-256-bit-key>"
  storage:
    s3:
      enabled: true
      uploadPath: "s3://<bucket-name>/upload"
      readyPath: "s3://<bucket-name>/ready"
    file:
      max_size: "500MB"
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

postgresqlMedia:
  enabled: false

customMediaPostgresql:
  global:
    postgresql:
      auth:
        database: "media"
        hostname: "<db-host>"
        username: "<db-username>"
        servicePort: 5432
      secretRef:
        existingSecret: "media-db-credentials"
        passwordSecretKey: "password"

api:
  media:
    enabled: true
    uri: http://hume-media:8008
```

---

## Verify It Works

Check that the Media pod started:

```bash
kubectl get pods -n hume -l app.kubernetes.io/name=hume-media
```

Expected output:

```
NAME              READY   STATUS    RESTARTS   AGE
hume-media-0      1/1     Running   0          3m
```

Confirm the service is running:

```bash
kubectl logs hume-media-0 -n hume | grep -i "started\|listening\|running"
```

---

## Next Steps

- [Storage](storage.md) — PVC sizing and storage class configuration for Media and Orchestra
- [Databases](databases.md) — using external PostgreSQL for all services
- [Monitoring](../production/monitoring.md) — Prometheus ServiceMonitor setup
