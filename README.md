<!--- app-name: Hume -->

# Hume — Helm Chart by GraphAware

[Hume](https://www.graphaware.com/products/hume/) is an enterprise graph analytics platform that lets teams build, explore, and operationalize graph-based intelligence on top of Neo4j.

This repository contains the official Helm charts for deploying Hume on Kubernetes.

---

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- A GraphAware account with access to `docker.graphaware.com`
- A Hume licence key

> Neo4j is **not** included in the chart. You must provision it separately.

---

## Quick Install

**1. Log in to the Helm registry**

```bash
helm registry login -u '<username>' -p '<password>' docker.graphaware.com
```

**2. Create a namespace and image pull secret**

```bash
kubectl create namespace hume

kubectl create secret docker-registry graphaware-docker-creds \
  --docker-server='docker.graphaware.com' \
  --docker-username='<username>' \
  --docker-password='<password>' \
  -n hume
```

**3. (Optional) Pre-load your licence key**

```bash
kubectl create secret generic hume-licence \
  --from-literal=hume.licence.key=<content-of-your-b64-file> \
  -n hume
```

If omitted, Hume will prompt you to upload the licence on first login.

**4. Install**

```bash
helm install hume oci://docker.graphaware.com/public/hume --version 3.0.0 -n hume
```

**5. Access the UI (local / no ingress)**

```bash
kubectl port-forward service/hume-web 8081:8081 -n hume &
kubectl port-forward service/hume-api 8080:8080 -n hume &
```

Open [http://localhost:8081](http://localhost:8081) and log in with `admin@hume.k8s` / `password`.

> **Change the default admin credentials before exposing Hume externally.**

---

## Documentation

The full documentation lives in [`docs/`](./docs/index.md).

| I want to… | Go to |
|---|---|
| Understand what gets deployed | [Architecture Overview](docs/getting-started/architecture.md) |
| Deploy to a real cluster with ingress | [Basic Installation](docs/installation/basic-installation.md) |
| Configure AWS ALB or Nginx ingress | [Ingress](docs/configuration/ingress.md) |
| Connect to an external PostgreSQL | [Databases](docs/configuration/databases.md) |
| Set up SSO with Keycloak | [Authentication](docs/configuration/authentication.md) |
| Enable LLM integration | [Maestro](docs/optional-services/maestro.md) |
| Enable alerting | [Alerting](docs/optional-services/alerting.md) |
| Upgrade from a previous version | [Upgrade Guide](docs/installation/upgrade-guide.md) |
| Set up monitoring with Prometheus | [Monitoring](docs/production/monitoring.md) |
| Diagnose a broken deployment | [Troubleshooting](docs/operations/troubleshooting.md) |
| See all configuration parameters | [Values Reference](docs/reference/values-hume-helm.md) |

---

## Charts

| Chart | Description |
|---|---|
| `hume-helm` | Core platform: Web, API, Orchestra, EventStore, Media, Maestro |
| `hume-alerting` | Alerting engine: Controller, Operator, Kafka (separately licensed) |

```bash
# Install a specific version
helm install hume oci://docker.graphaware.com/public/hume --version 3.0.0 -n hume -f values.yaml

# Upgrade
helm upgrade hume oci://docker.graphaware.com/public/hume --version 3.0.0 -n hume -f values.yaml

# Uninstall (PVCs are retained)
helm uninstall hume -n hume
```

---

## Deployment Scenarios

The [`deployment-scenarios/`](./deployment-scenarios/) directory contains ready-to-use values files for common setups:

| Scenario | Description |
|---|---|
| `external-persistence/` | External PostgreSQL and Keycloak |
| `hume-sso-keycloak/` | SSO with internal Keycloak |
| `orchestra-cluster/` | Orchestra in cluster mode with Prometheus monitoring |
| `maestro/` | Maestro with OpenAI |
| `initial-api-key/` | Pre-configured API key for automation |

---

## License

Copyright &copy; 2022 GraphAware

Licensed under the Apache License, Version 2.0. See [LICENSE](http://www.apache.org/licenses/LICENSE-2.0) for details.
