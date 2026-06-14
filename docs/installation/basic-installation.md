# Basic Installation

This page walks through installing Hume on a real Kubernetes cluster using a values file, with ingress and production-appropriate settings.

---

## Values File Strategy

For anything beyond a quick evaluation, manage your configuration in a `values.yaml` file rather than `--set` flags. This keeps your deployment reproducible and version-controllable.

**Single file (simple deployments):**

```
hume/
└── values.yaml
```

**Base + environment overlay (recommended for multiple environments):**

```
hume/
├── values-base.yaml          # shared settings
├── values-staging.yaml       # staging overrides
└── values-production.yaml    # production overrides
```

Install with overlays:

```bash
helm install hume oci://docker.graphaware.com/public/hume \
  --version 3.0.0 \
  -n hume \
  -f values-base.yaml \
  -f values-production.yaml
```

---

## Minimum Viable Values File

The following is a starting point for a real cluster deployment. Inline comments explain each choice.

```yaml
# values.yaml

# Domain used to construct ingress hostnames.
# Web UI will be at hume-web.<baseDomain>, API at hume-api.<baseDomain>
baseDomain: "hume.example.com"

# EventStore and Media are enabled by default.
# Change their credentials from the insecure defaults before going to production.
eventstore:
  password: "<eventstore-password>"

postgresqlEventStore:
  global:
    postgresql:
      auth:
        password: "<pg-eventstore-password>"

media:
  password: "<media-password>"
  storage:
    local:
      enabled: true                           # or use s3/minio for production

postgresqlMedia:
  enabled: true
  global:
    postgresql:
      auth:
        password: "<pg-media-password>"       # change from default

# Ingress — choose annotations for your ingress controller (see Ingress guide)
ingress:
  enabled: true
  ingressClassName: nginx

# Change the default admin credentials before first login
api:
  admin:
    username: "admin@yourcompany.com"
    password: "<strong-password>"

# Change embedded database passwords from their defaults
postgresqlCore:
  global:
    postgresql:
      auth:
        password: "<pg-core-password>"

postgresqlOrchestra:
  global:
    postgresql:
      auth:
        password: "<pg-orchestra-password>"
```

> **Production:** The embedded PostgreSQL instances above are single-pod StatefulSets with no high availability or automated backups. For production, replace them with an external managed database. See [Databases](../configuration/databases.md).

---

## Install

```bash
helm install hume oci://docker.graphaware.com/public/hume \
  --version 3.0.0 \
  -n hume \
  -f values.yaml
```

For CI/CD pipelines, use `helm upgrade --install` — it is idempotent (installs on first run, upgrades on subsequent runs):

```bash
helm upgrade --install hume oci://docker.graphaware.com/public/hume \
  --version 3.0.0 \
  -n hume \
  -f values.yaml
```

---

## Install a Specific Chart Version

```bash
helm upgrade --install hume oci://docker.graphaware.com/public/hume \
  --version 3.0.0 \
  -n hume \
  -f values.yaml
```

To inspect available versions before installing, pull the chart:

```bash
helm pull oci://docker.graphaware.com/public/hume --version 3.0.0 --untar
```

---

## Verify the Installation

**Check pods are running:**

```bash
kubectl get pods -n hume
```

All pods should be in `Running` state. Typical output for a full installation:

```
NAME                             READY   STATUS    RESTARTS   AGE
hume-api-6d9f8b7c4-xk2pv         1/1     Running   0          5m
hume-eventstore-84b9d5f6-tqwrn   1/1     Running   0          5m
hume-media-0                     1/1     Running   0          5m
hume-orchestra-0                 1/1     Running   0          5m
hume-web-5c8d7b9f4-zjvnq         1/1     Running   0          5m
postgresql-core-0                1/1     Running   0          5m
postgresql-eventstore-0          1/1     Running   0          5m
postgresql-media-0               1/1     Running   0          5m
postgresql-orchestra-0           1/1     Running   0          5m
```

**Run Helm's built-in test:**

```bash
helm test hume -n hume
```

**Check the post-install notes:**

```bash
helm status hume -n hume
```

If `ingress.enabled: true` and `baseDomain` is set, the notes show the URL where Hume is accessible.

---

## Air-Gapped / Custom Registry

If your cluster cannot reach `docker.graphaware.com` directly, copy the images to your own registry and override the base repository in your values file.

```yaml
# values.yaml
humeCoreBaseRepository: "your-registry.example.com/hume-core/"
```

> The trailing slash is required.

For the Alerting chart, override `humeAlertingBaseRepository` as well.

You will also need to mirror the Bitnami dependencies (PostgreSQL, Kafka, Keycloak) from `docker.graphaware.com/mirror/bitnami/` to your registry and update the `image.registry` fields in each sub-chart's values section.

---

## Uninstall

```bash
helm uninstall hume -n hume
```

> **PVCs are not deleted automatically.** Persistent Volume Claims for Orchestra, Media, and PostgreSQL StatefulSets remain after uninstall. Delete them manually if you want to remove all data:
>
> ```bash
> kubectl delete pvc -n hume --all
> ```

---

## Next Steps

- [Ingress](../configuration/ingress.md) — Expose Hume with AWS ALB or Nginx
- [Authentication](../configuration/authentication.md) — Native auth or Keycloak SSO
- [Databases](../configuration/databases.md) — Connect to external PostgreSQL
- [Upgrade Guide](upgrade-guide.md) — How to safely upgrade between versions
