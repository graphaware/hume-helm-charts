# Security

Harden your Hume deployment with proper secret management, access controls, and image provenance.

---

## Pod Security (Pre-Configured)

The chart ships with secure defaults. No action is needed for standard deployments:

| Setting | Value | Effect |
|---|---|---|
| `runAsNonRoot` | `true` | Containers run as UID 1001 |
| `fsGroup` | `2000` | Volume ownership group |
| `capabilities.drop` | `ALL` | All Linux capabilities dropped |

These are applied to every Hume pod. The values are in the `podSecurityContext` and `securityContext` chart keys if you need to override them.

---

## Image Pull Secret

Required before installing. Create once per namespace:

```bash
kubectl create secret docker-registry graphaware-docker-creds \
  --docker-server='docker.graphaware.com' \
  --docker-username='<username>' \
  --docker-password='<password>' \
  -n hume
```

The chart references this secret by default (`imagePullSecrets[0].name: graphaware-docker-creds`). If you rename it, update:

```yaml
imagePullSecrets:
  - name: <your-secret-name>
```

**Rotating credentials:** Delete and recreate the secret. Pods pick up the new secret automatically on their next image pull (or restart).

---

## Licence Secret

```bash
kubectl create secret generic hume-licence \
  --from-literal=hume.licence.key='<base64-licence-string>' \
  -n hume
```

If you do not create this secret, Hume will prompt you to upload the licence file on first login.

---

## Changing the Default Admin Password

The admin user (`admin@hume.k8s` / `password`) is created on first startup. Change it before deploying to any non-local environment:

```yaml
api:
  admin:
    username: "admin@example.com"
    password: "<strong-random-password>"
```

> **Production callout:** This is a one-time creation. If you change the password after first boot, update it directly in the Hume UI or API — the chart value is ignored for existing users.

---

## API Key Management

For machine-to-machine access (CI pipelines, integrations), use API keys rather than user credentials.

Enable the Remote API and create an initial key from an existing Kubernetes secret:

```bash
# Create the secret first
kubectl create secret generic hume-api-key-secret \
  --from-literal=token='<strong-random-token>' \
  -n hume
```

```yaml
api:
  remoteApi:
    enabled: true
    initialKey:
      create: true
      name: "ci-integration-key"
      roles: "ADMINISTRATOR"
      existingSecret: "hume-api-key-secret"
      existingSecretKey: "token"
```

Rotate by updating the secret value and restarting the API pod:

```bash
kubectl rollout restart deployment/hume-api -n hume
```

---

## Secrets Management: External Secrets Operator

Avoid storing credentials in values files. Use [External Secrets Operator](https://external-secrets.io/) to sync secrets from your cloud provider.

**AWS Secrets Manager example:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: hume-db-credentials
  namespace: hume
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: hume-db-credentials
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: hume-prod/db-credentials
        property: password
```

Reference the created secret in your values:

```yaml
customApiPostgresql:
  global:
    postgresql:
      auth:
        hostname: "<rds-endpoint>"
        database: "hume_prod"
        username: "hume"
      secretRef:
        existingSecret: "hume-db-credentials"
        passwordSecretKey: "password"
```

The same pattern works for Azure Key Vault and HashiCorp Vault — only the `secretStoreRef` and `remoteRef` fields differ.

---

## Air-Gapped / Custom Registry

When `docker.graphaware.com` is not reachable, mirror images to your internal registry and override the base repository:

```yaml
humeCoreBaseRepository: "registry.internal.example.com/hume-core/"
```

> Trailing slash is required.

For Alerting:

```yaml
hume-alerting:
  humeAlertingControllerBaseRepository: "registry.internal.example.com/hume-alerting/"
  humeAlertingOperatorBaseRepository: "registry.internal.example.com/hume-alerting/"
```

Also mirror the Bitnami dependency images (PostgreSQL, Kafka, Keycloak):

```yaml
postgresqlCore:
  image:
    registry: "registry.internal.example.com"
    repository: "mirror/bitnami/postgresql"
    tag: "15.1.0-debian-11-r12"
```

Repeat for `postgresqlOrchestra`, `postgresqlEventStore`, `postgresqlMedia`, and Kafka.

---

## Service Account and IRSA (AWS)

If Hume services need to access AWS resources (S3 for Media storage or backups), attach IAM roles via IRSA annotations:

```yaml
serviceAccount:
  create: true
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::<account-id>:role/hume-prod-role"
```

Create a separate service account for Alerting if it needs different S3 access:

```yaml
hume-alerting:
  serviceAccount:
    annotations:
      eks.amazonaws.com/role-arn: "arn:aws:iam::<account-id>:role/hume-alerting-role"
```

---

## Verify

```bash
# Check no passwords are exposed in running pod specs
kubectl get pod -n hume -o json | jq '.items[].spec.containers[].env[] | select(.value != null) | select(.name | test("password|secret|token"; "i"))'

# Verify service account exists and has correct annotations
kubectl get serviceaccount hume -n hume -o yaml

# Check pod is running as non-root
kubectl exec -it deployment/hume-api -n hume -- id
# Expected: uid=1001 gid=0(root) groups=0(root),2000

# Confirm image pull secret exists in the right namespace
kubectl get secret graphaware-docker-creds -n hume
```

---

## Next Steps

- [Monitoring](monitoring.md) — Set up metrics and alerting
- [Backup and Restore](backup-restore.md) — Protect your data
- [Troubleshooting](../operations/troubleshooting.md) — Diagnose access and startup issues
