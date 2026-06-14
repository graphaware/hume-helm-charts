# Storage

Configure persistent volumes for Orchestra's workflow state, PostgreSQL data, and the Media service's file storage backend.

---

## Orchestra Persistent Volume

Orchestra is a StatefulSet that persists its workflow state to a PersistentVolumeClaim mounted at `/data`.

The default volume size is **1Gi**, which is insufficient for most real workloads. Size it according to the volume and complexity of workflows you expect to run.

```yaml
orchestra:
  persistence:
    enabled: true
    mountPath: "/data"
    size: 50Gi                    # Increase from the 1Gi default
    storageClassName: gp3         # Use your cloud/cluster's fast SSD class
    accessModes:
      - ReadWriteOnce
```

### StorageClass recommendations

| Environment | Recommended StorageClass |
|---|---|
| AWS EKS | `gp3` (better price/performance than `gp2`) |
| GCP GKE | `premium-rwo` |
| Azure AKS | `managed-premium` |
| On-premises | Consult your CSI driver documentation |

> **Warning:** Resizing a PVC requires the StorageClass to have `allowVolumeExpansion: true`. Even then, Orchestra's StatefulSet pod must be deleted and restarted to pick up the new size. Plan your initial size generously — expanding later involves downtime.

---

## PostgreSQL Persistence

Each embedded Bitnami PostgreSQL StatefulSet also uses a PVC. The Bitnami chart defaults to 8Gi per instance, which is a starting point but typically too small for production use.

Configure storage per database instance:

```yaml
postgresqlCore:
  primary:
    persistence:
      size: 20Gi
      storageClassName: gp3

postgresqlOrchestra:
  primary:
    persistence:
      size: 50Gi
      storageClassName: gp3

postgresqlEventStore:
  primary:
    persistence:
      size: 50Gi
      storageClassName: gp3

postgresqlMedia:
  primary:
    persistence:
      size: 20Gi
      storageClassName: gp3
```

Size guidance:
- **Core (API)**: 20Gi is typically sufficient for user/config data
- **Orchestra**: Scale with workflow execution history volume; 50–100Gi for active deployments
- **EventStore**: Scale with audit event volume; 50–100Gi for high-throughput environments
- **Media**: Metadata only (actual files go to the Media storage backend); 20Gi is usually enough

> If you use external PostgreSQL, these values have no effect. See [Databases](databases.md).

---

## Media File Storage Backends

The Media service stores binary files (images, documents, attachments). Choose one backend. Only one can be active at a time.

### Option 1: Local Filesystem

**Use for:** single-node development only.

```yaml
media:
  storage:
    local:
      enabled: true
      uploadPath: "/data/upload"
      readyPath: "/data/ready"
```

The paths refer to locations inside the Media pod's filesystem. Use a PVC if you want persistence across pod restarts:

```yaml
media:
  volumes:
    - name: media-data
      persistentVolumeClaim:
        claimName: media-storage-pvc
  volumeMounts:
    - name: media-data
      mountPath: /data
```

> **Warning:** Local filesystem storage is tied to a single pod and node. It is not compatible with multi-replica deployments and files are lost if the PVC is deleted. Do not use this in any environment where file durability is required.

### Option 2: Amazon S3

**Use for:** AWS environments or any S3-compatible storage.

```yaml
media:
  storage:
    s3:
      enabled: true
      uploadPath: "s3://<bucket-name>/upload"
      readyPath: "s3://<bucket-name>/ready"
```

**Authentication — Option A: IRSA (recommended for EKS)**

Use an IAM role attached to the pod's ServiceAccount. No credentials in values.

```yaml
serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::<account-id>:role/hume-media-role"

media:
  storage:
    s3:
      enabled: true
      uploadPath: "s3://<bucket-name>/upload"
      readyPath: "s3://<bucket-name>/ready"
  env:
    - name: AWS_REGION
      value: eu-west-1
```

Minimum IAM policy for the role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
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

**Authentication — Option B: Access key (not recommended for production)**

```yaml
media:
  env:
    - name: AWS_ACCESS_KEY_ID
      valueFrom:
        secretKeyRef:
          name: hume-media-s3-credentials
          key: access-key-id
    - name: AWS_SECRET_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: hume-media-s3-credentials
          key: secret-access-key
    - name: AWS_REGION
      value: eu-west-1
```

Create the secret:

```bash
kubectl create secret generic hume-media-s3-credentials \
  --from-literal=access-key-id='<access-key-id>' \
  --from-literal=secret-access-key='<secret-access-key>' \
  -n hume
```

### Option 3: MinIO

**Use for:** on-premises deployments, air-gapped environments, or any Kubernetes cluster without cloud object storage.

```yaml
media:
  storage:
    minio:
      enabled: true
      uploadPath: "minio://<minio-host>:9000/<bucket>/upload"
      readyPath: "minio://<minio-host>:9000/<bucket>/ready"
      accessKey: "<minio-access-key>"
      accessSecret: "<minio-secret-key>"
```

To avoid putting credentials in your values file, inject them via environment variables:

```yaml
media:
  storage:
    minio:
      enabled: true
      uploadPath: "minio://<minio-host>:9000/<bucket>/upload"
      readyPath: "minio://<minio-host>:9000/<bucket>/ready"
  env:
    - name: STORAGE_MINIO_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: hume-media-minio-credentials
          key: access-key
    - name: STORAGE_MINIO_ACCESS_SECRET
      valueFrom:
        secretKeyRef:
          name: hume-media-minio-credentials
          key: access-secret
```

---

## Media File Limits

```yaml
media:
  storage:
    file:
      max_size: "200MB"          # Maximum file size per upload
      initial_status: "READY"    # Status assigned to files immediately on upload
```

Increase `max_size` if users need to upload large files (videos, large datasets). The value accepts standard size suffixes: `MB`, `GB`.

---

## Verify It Works

**Orchestra PVC:**

```bash
kubectl get pvc -n hume | grep orchestra
# Expected: a PVC named hume-orchestra-0 or similar, STATUS=Bound
```

**Media storage:**

Upload a file through the Hume UI or API and confirm it appears in your storage backend (S3 bucket, MinIO console, or local path). Then check the Media pod logs:

```bash
kubectl logs statefulset/hume-media -n hume | grep -i "upload\|storage\|s3\|minio"
```

---

## Next Steps

- [Media](media.md) — Full Media service configuration including database and API keys
- [High Availability](../production/high-availability.md) — Orchestra clustering and PVC considerations
- [Backup & Restore](../production/backup-restore.md) — Back up Orchestra and PostgreSQL volumes
