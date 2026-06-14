# Prerequisites

This page lists everything you need to have in place before installing the Hume Helm chart.

---

## Tools

| Tool | Minimum version |
|---|---|
| Kubernetes | 1.19 |
| Helm | 3.2.0 |

Verify your versions:

```bash
helm version --short
kubectl version --client --short
```

Verify your cluster is reachable:

```bash
kubectl cluster-info
```

---

## GraphAware Account and Registry Access

Both the Helm chart and all Docker images are pulled from GraphAware's OCI registry at `docker.graphaware.com`. You need a GraphAware account to access it.

If you don't have an account, contact [GraphAware](https://graphaware.com/contact/) to arrange access.

Verify you can log in:

```bash
helm registry login -u '<username>' -p '<password>' docker.graphaware.com
```

You will also need to create an image pull secret in Kubernetes so that pods can pull images at runtime. Do this after creating your namespace:

```bash
kubectl create namespace hume

kubectl create secret docker-registry graphaware-docker-creds \
  --docker-server='docker.graphaware.com' \
  --docker-username='<username>' \
  --docker-password='<password>' \
  -n hume
```

> The secret must be named exactly `graphaware-docker-creds`. That name is the default in `values.yaml` under `imagePullSecrets`. If you use a different name, set `imagePullSecrets[0].name` in your values file to match.

---

## Hume Licence Key

Hume requires a licence key. GraphAware provides this as a base64-encoded string, typically in a `.b64` file.

Create the licence secret:

```bash
kubectl create secret generic hume-licence \
  --from-literal=hume.licence.key=<content-of-your-b64-file> \
  -n hume
```

> If you omit this secret, Hume will start without a licence and prompt you to upload one on first login. For automated or production deployments, pre-creating the secret is strongly recommended.

Contact your GraphAware account team if you have not yet received a licence key.

---

## Neo4j

Hume connects to Neo4j but **does not deploy it**. You must provision a Neo4j instance separately and have its Bolt endpoint (port 7687) reachable from within your Kubernetes cluster.

The [Neo4j Helm chart](https://helm.neo4j.com/) is the recommended way to run Neo4j on Kubernetes. You will configure the Neo4j connection inside the API after installation via the Hume UI.

---

## What the Chart Does NOT Provide

The following must exist before or alongside a Hume installation:

| Requirement | What to use |
|---|---|
| Neo4j | [Neo4j Helm chart](https://helm.neo4j.com/) or managed service |
| Load balancer / Ingress Controller | AWS ALB, Nginx, Traefik, etc. |
| TLS certificates | cert-manager, AWS ACM, or manual secrets |

---

## Verify Prerequisites

Run through this checklist before proceeding:

```bash
# Helm 3.2.0 or higher
helm version --short

# Cluster is accessible
kubectl cluster-info

# Correct namespace exists
kubectl get namespace hume

# Image pull secret is present
kubectl get secret graphaware-docker-creds -n hume

# Licence secret is present (optional but recommended)
kubectl get secret hume-licence -n hume

# Registry login works
helm registry login -u '<username>' docker.graphaware.com
```

---

## Next Steps

- [Quick Start](quick-start.md) — Install and access Hume in under 10 minutes
- [Basic Installation](../installation/basic-installation.md) — Full installation walkthrough for a real cluster
