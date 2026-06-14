# Upgrading Hume

This page covers the safe upgrade procedure and version-specific notes for every release that includes breaking changes.

**Always read the version-specific notes for your target version before running any upgrade command.**

---

## General Upgrade Procedure

Follow these steps for every upgrade, then check the version-specific notes below for any additional actions.

**1. Read the version-specific notes for your target version** (see below).

**2. Pull the chart and inspect what changed:**

```bash
helm pull oci://docker.graphaware.com/public/hume --version <target-version> --untar
```

**3. Diff your existing values against the new defaults:**

```bash
diff my-values.yaml hume/values.yaml
```

Look for any new keys you need to set, and any keys that have been renamed or removed.

**4. Dry-run the upgrade:**

```bash
helm upgrade hume oci://docker.graphaware.com/public/hume \
  --version <target-version> \
  -n hume \
  -f my-values.yaml \
  --dry-run
```

Review the diff output. If it errors or shows unexpected changes, do not proceed.

**5. Run the upgrade:**

```bash
helm upgrade hume oci://docker.graphaware.com/public/hume \
  --version <target-version> \
  -n hume \
  -f my-values.yaml
```

**6. Watch the rollout:**

```bash
kubectl rollout status deployment/hume-api -n hume
kubectl rollout status statefulset/hume-orchestra -n hume
```

---

## Version-Specific Notes

---

### v3.0.0

- EventStore and Media are now enabled by default (`enabled: true`). If you were previously managing these services externally and passing `enabled: false` to suppress the embedded deployments, that explicit setting remains necessary — it will not be overridden by the new default.
- `api.media.enabled` and `api.media.uri` now default to `true` / `http://hume-media:8008`. If you were running without Media, add `api.media.enabled: false` to prevent the API from trying to connect to a service that isn't there.
- Review all values keys against the `hume/values.yaml` from the 3.0.0 chart. Run the diff step above.

---

### v2.27.0 — BREAKING

> **This version requires manual resource deletion before upgrading.**

Kubernetes/Helm label standardization changed the `.spec.selector` labels on all Deployments and StatefulSets. Helm cannot patch immutable selectors in-place — if you run `helm upgrade` directly, it will fail.

**You must delete the affected Deployments and StatefulSets first.** The Helm release itself is NOT deleted. PVCs and their data are NOT deleted.

```bash
# Delete all Deployments and StatefulSets in the hume namespace
kubectl delete deployment hume-api hume-web -n hume
kubectl delete statefulset hume-orchestra postgresql-core postgresql-orchestra -n hume

# If EventStore was enabled in your installation:
kubectl delete deployment hume-eventstore -n hume
kubectl delete statefulset postgresql-eventstore -n hume

# If Media was enabled:
kubectl delete statefulset hume-media postgresql-media -n hume

# Now run the upgrade — Helm recreates all resources with the new labels
helm upgrade hume oci://docker.graphaware.com/public/hume \
  --version 2.27.0 \
  -n hume \
  -f my-values.yaml
```

**Additional changes in v2.27.0:**

- Bitnami Docker images migrated to `docker.graphaware.com/mirror/bitnami/`. If you are running in an air-gapped environment, update your image mirror to source from the GraphAware registry rather than docker.io.

- Keycloak chart bumped to `14.4.0` and Keycloak image to `v21`. If you use Keycloak SSO (`keycloak.internal.enabled: true`), review any Keycloak-specific values for renamed keys before upgrading.

- Pod anti-affinity rules added for `hume-api`, `hume-orchestra`, and alerting services. No action required, but note that single-node clusters (e.g., minikube) may show pods in `Pending` if anti-affinity cannot be satisfied.

---

### v2.26.1 — BREAKING

The default values for `postgresqlEventstore.enabled` and `postgresqlMedia.enabled` changed from `true` to `false`.

If your existing installation relied on the previous implicit default of `true` for these databases but you did not have them explicitly set in your values file, the databases will be removed on upgrade.

Add these to your values file explicitly before upgrading:

```yaml
postgresqlEventStore:
  enabled: true

postgresqlMedia:
  enabled: true
```

---

### v2.26.0

- Media StatefulSet added. If upgrading from 2.25.x and you want to enable Media for the first time, ensure a StorageClass is available and set:

  ```yaml
  media:
    enabled: true
  postgresqlMedia:
    enabled: true
  ```

---

### v2.19.0

- Zookeeper-less Orchestra clustering introduced. If you were using a previous custom clustering configuration, update your Orchestra values to use the new cluster mode:

  ```yaml
  orchestra:
    cluster:
      enabled: true
    deployment:
      replicas: 3
  ```

  The old zookeeper-based approach is no longer supported.

---

## Rollback

If an upgrade fails or causes unexpected issues:

```bash
helm rollback hume -n hume
```

This reverts to the previous Helm release revision. Check `helm history hume -n hume` to see available revisions.

> Rolling back does not restore database schema migrations applied by the new version. If the upgrade ran database migrations, a rollback may require restoring from a database backup. Always take a database backup before upgrading production.

---

## Next Steps

- [Basic Installation](basic-installation.md) — Installation reference
- [Backup and Restore](../production/backup-restore.md) — Take a database backup before upgrading
- [Troubleshooting](../operations/troubleshooting.md) — What to do if the upgrade fails
