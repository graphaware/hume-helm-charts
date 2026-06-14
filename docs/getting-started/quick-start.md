# Quick Start

This page gets Hume running on a local or test cluster using port-forwarding — no ingress or domain name required.

---

## Before You Begin

- A running Kubernetes cluster (minikube, kind, or any cluster with at least 8 GB of allocatable memory)
- Helm 3.2.0+
- A GraphAware account with access to `docker.graphaware.com`
- Your Hume licence key (optional at this stage — you can upload it via the UI on first login)

---

## Step 1: Log In to the Helm Registry

```bash
helm registry login -u '<username>' -p '<password>' docker.graphaware.com
```

---

## Step 2: Create the Namespace

```bash
kubectl create namespace hume
```

---

## Step 3: Create the Image Pull Secret

Pods need this to pull images from `docker.graphaware.com`. The name must match exactly.

```bash
kubectl create secret docker-registry graphaware-docker-creds \
  --docker-server='docker.graphaware.com' \
  --docker-username='<username>' \
  --docker-password='<password>' \
  -n hume
```

---

## Step 4: (Optional) Create the Licence Secret

If you have your licence key, pre-create the secret so Hume activates automatically on first start.

```bash
kubectl create secret generic hume-licence \
  --from-literal=hume.licence.key=<content-of-your-b64-file> \
  -n hume
```

If you skip this step, Hume will prompt you to upload the licence file on first login.

---

## Step 5: Install the Chart

```bash
helm install hume oci://docker.graphaware.com/public/hume \
  --version 3.0.0 \
  -n hume
```

For anything beyond this quick start, use a values file instead. See [Basic Installation](../installation/basic-installation.md).

---

## Step 6: Wait for Pods to Be Ready

```bash
kubectl get pods -n hume -w
```

All pods should reach `Running` status within a few minutes. You should see something like:

```
NAME                             READY   STATUS    RESTARTS   AGE
hume-api-6d9f8b7c4-xk2pv         1/1     Running   0          3m
hume-eventstore-84b9d5f6-tqwrn   1/1     Running   0          3m
hume-media-0                     1/1     Running   0          3m
hume-orchestra-0                 1/1     Running   0          3m
hume-web-5c8d7b9f4-zjvnq         1/1     Running   0          3m
postgresql-core-0                1/1     Running   0          3m
postgresql-eventstore-0          1/1     Running   0          3m
postgresql-media-0               1/1     Running   0          3m
postgresql-orchestra-0           1/1     Running   0          3m
```

The API pod may restart once while waiting for the database to be ready — this is expected.

---

## Step 7: Access the UI

Open two terminal windows.

**Terminal 1 — Web UI:**

```bash
kubectl port-forward service/hume-web 8081:8081 -n hume
```

**Terminal 2 — API:**

```bash
kubectl port-forward service/hume-api 8080:8080 -n hume
```

Both port-forwards must stay running. Open [http://localhost:8081](http://localhost:8081) in your browser.

Log in with the default credentials:

| Field | Value |
|---|---|
| Username | `admin@hume.k8s` |
| Password | `password` |

---

## Verify It Works

After logging in, navigate to **Settings → System** to confirm all services are connected. If the licence secret was not pre-created, you will see a prompt to upload your licence file here.

---

> **For evaluation only.** This setup uses the default admin credentials, embedded PostgreSQL databases with no replication, and no TLS. It is not suitable for production or any environment holding real data. Before going further, review the [Basic Installation](../installation/basic-installation.md) and [Databases](../configuration/databases.md) guides.

---

## Next Steps

- [Basic Installation](../installation/basic-installation.md) — Full cluster deployment with a values file, ingress, and production-ready settings
- [Ingress](../configuration/ingress.md) — Expose Hume over a real domain with AWS ALB or Nginx
- [Authentication](../configuration/authentication.md) — Configure SSO with Keycloak or keep native auth
- [Databases](../configuration/databases.md) — Switch from embedded PostgreSQL to an external managed database
