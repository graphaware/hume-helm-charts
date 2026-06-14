# Backup and Restore

Protect Hume's stateful data with scheduled PostgreSQL backups and PVC snapshots.

---

## What to Back Up

| Component | Data stored | Criticality |
|---|---|---|
| PostgreSQL (core) | Users, connections, graph configurations | High |
| PostgreSQL (orchestra) | Workflow definitions, job history, schedules | High |
| PostgreSQL (eventstore) | Immutable audit log | High (compliance) |
| PostgreSQL (media) | File metadata and references | High |
| PostgreSQL (alerting-controller) | Alert rules and execution history | Medium |
| PostgreSQL (alerting-operator) | Operator state | Medium |
| Orchestra PVCs (`/data`) | Plugin JARs, in-flight job state, scripts | Medium |
| Media PVCs | Actual files (local storage backend only) | High |
| Kubernetes Secrets | Image pull, licence, DB credentials | High |

If Media uses S3 or MinIO as its storage backend, the binary files are managed by the object store — enable versioning there. Media PVCs will then only contain metadata (already covered by the PostgreSQL backup).

---

## PostgreSQL Backup

### Scheduled CronJob (Recommended)

Deploy a CronJob per database that runs `pg_dump` and ships the output to S3. The example below uses the AWS CLI alongside `psql`:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hume-api-db-backup
  namespace: hume
spec:
  schedule: "45 3 * * *"          # daily at 3:45 AM
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      ttlSecondsAfterFinished: 3600
      template:
        spec:
          restartPolicy: Never
          serviceAccountName: hume-backup-sa   # needs s3:PutObject on the bucket
          containers:
            - name: pg-backup
              image: postgres:15-alpine
              env:
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: hume-db-credentials
                      key: password
                - name: BACKUP_BUCKET
                  value: "s3://<backup-bucket-name>"
                - name: AWS_DEFAULT_REGION
                  value: "eu-west-1"
              command:
                - /bin/sh
                - -c
                - |
                  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
                  pg_dump \
                    --host=<rds-endpoint> \
                    --port=5432 \
                    --username=hume \
                    --dbname=hume_prod \
                    --format=custom \
                  | aws s3 cp - \
                      ${BACKUP_BUCKET}/postgres/hume-api-${TIMESTAMP}.dump \
                      --sse AES256
```

Duplicate this CronJob for each database (`orchestra`, `eventstore`, `media`, etc.), adjusting `--dbname` and the S3 key prefix.

### Monitor Backup Jobs

Alert if a backup job has not completed successfully:

```bash
# Check recent job runs
kubectl get jobs -n hume | grep backup

# Check logs of the last backup run
kubectl logs -n hume -l job-name=hume-api-db-backup --tail=50
```

---

## Orchestra PVC Backup

Orchestra stores plugin JARs and custom scripts at `/data`. Back up before upgrades or when changing plugins:

```bash
# Pause Orchestra (optional, for consistency)
kubectl scale statefulset hume-orchestra --replicas=0 -n hume

# Copy the data out
kubectl cp hume/hume-orchestra-0:/data ./orchestra-backup-$(date +%Y%m%d)

# Restart Orchestra
kubectl scale statefulset hume-orchestra --replicas=1 -n hume
```

Or use a snapshot if your StorageClass supports it (e.g., AWS EBS):

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: orchestra-data-snapshot
  namespace: hume
spec:
  volumeSnapshotClassName: csi-aws-vsc
  source:
    persistentVolumeClaimName: data-hume-orchestra-0
```

---

## Kubernetes Secrets Backup

Export secrets to an encrypted store before cluster migrations or disaster recovery:

```bash
# Export all secrets (encrypt before storing)
kubectl get secrets -n hume -o yaml | \
  gpg --symmetric --cipher-algo AES256 \
  > hume-secrets-$(date +%Y%m%d).yaml.gpg
```

Do not commit unencrypted secret exports to version control.

---

## Restore Procedure

### PostgreSQL Restore

1. Scale down the affected service to stop writes:

   ```bash
   kubectl scale deployment hume-api --replicas=0 -n hume
   ```

2. Drop and recreate the target database (external PostgreSQL):

   ```bash
   psql -h <rds-endpoint> -U postgres -c \
     "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='hume_prod';"
   psql -h <rds-endpoint> -U postgres -c \
     "DROP DATABASE hume_prod; CREATE DATABASE hume_prod OWNER hume;"
   ```

3. Restore from the backup:

   ```bash
   aws s3 cp s3://<backup-bucket>/postgres/hume-api-<timestamp>.dump - | \
     pg_restore \
       --host=<rds-endpoint> \
       --port=5432 \
       --username=hume \
       --dbname=hume_prod \
       --no-owner \
       --no-acl
   ```

4. Scale the service back up:

   ```bash
   kubectl scale deployment hume-api --replicas=1 -n hume
   ```

5. Watch the rollout:

   ```bash
   kubectl rollout status deployment/hume-api -n hume
   ```

### Orchestra PVC Restore

```bash
# Scale down Orchestra
kubectl scale statefulset hume-orchestra --replicas=0 -n hume

# Copy the backup back in
kubectl cp ./orchestra-backup-<date> hume/hume-orchestra-0:/data

# Scale back up
kubectl scale statefulset hume-orchestra --replicas=1 -n hume
```

---

## Verify

```bash
# Confirm CronJobs are scheduled
kubectl get cronjob -n hume

# List recent backup objects in S3
aws s3 ls s3://<backup-bucket>/postgres/ --recursive | sort | tail -20

# Test restore to a staging namespace (monthly practice)
kubectl create namespace hume-restore-test
# Run restore steps above targeting the test namespace
```

Test restores monthly. A backup that has never been tested is not a backup.

---

## Next Steps

- [High Availability](high-availability.md) — Reduce the need for restores with resilient deployments
- [Troubleshooting](../operations/troubleshooting.md) — Diagnose issues after a restore
