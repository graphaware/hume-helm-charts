# Maestro

Maestro is Hume's optional AI integration layer, bridging the Hume UI to large language models to enable natural-language graph queries, AI-powered entity extraction, and conversational graph exploration.

---

## Prerequisites

Maestro requires the Remote API to be enabled:

```yaml
api:
  remoteApi:
    enabled: true
```

---

## Choose a Model Provider

Maestro supports three LLM providers. Select one and configure it as shown below.

### Ollama (Local, On-Cluster)

Use Ollama to run models locally without sending data to external APIs — ideal for air-gapped environments or data-sensitive deployments.

```yaml
maestro:
  enabled: true
  model:
    provider: ollama
  ollama:
    base-url: 'http://ollama:11434'   # URL of your Ollama service

api:
  remoteApi:
    enabled: true
```

> **Note:** Ollama is not included in the Hume Helm chart. You must deploy it separately. The [Ollama Helm chart](https://artifacthub.io/packages/helm/ollama-helm/ollama) is a common choice.

### OpenAI

```yaml
maestro:
  enabled: true
  model:
    provider: openai
  openai:
    apiKey:
      secretKeyName: 'openai-secret'   # name of the Kubernetes Secret
      secretKeyRef: 'api-key'          # key within that Secret

api:
  remoteApi:
    enabled: true
```

Create the secret holding your OpenAI API key:

```bash
kubectl create secret generic openai-secret \
  --from-literal=api-key='<your-openai-api-key>' \
  -n hume
```

### Azure OpenAI

```yaml
maestro:
  enabled: true
  model:
    provider: azure-openai
  azure-openai:
    deployment:
      name: 'gpt-4o'                              # your Azure OpenAI deployment name
    endpoint: 'https://<resource>.openai.azure.com/'
    apiKey:
      secretKeyName: 'azure-openai-secret'
      secretKeyRef: 'api-key'

api:
  remoteApi:
    enabled: true
```

Create the secret:

```bash
kubectl create secret generic azure-openai-secret \
  --from-literal=api-key='<your-azure-openai-api-key>' \
  -n hume
```

---

## Agent ConfigMap

Maestro uses a ConfigMap to define the AI agents available in the Hume UI. The `primaryConfigMapRef` value (default: `api-maestro-primary-configmap`) must point to a ConfigMap that exists in the same namespace.

Create a minimal agent ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-maestro-primary-configmap
  namespace: hume
data:
  agents.yaml: |
    agents:
      - id: "default"
        name: "Hume Assistant"
        uri: "http://hume-maestro:8090"
```

Apply it before installing or upgrading the chart:

```bash
kubectl apply -f maestro-agents-configmap.yaml
```

If you have a second, supplementary ConfigMap (for additional agents), reference it with:

```yaml
maestro:
  additionalConfigMapRef: 'my-extra-agents-configmap'
```

---

## Debug LLM Requests

To log every LLM request and response pair for troubleshooting — **disable in production**:

```yaml
maestro:
  log-llm-requests: 'true'
```

---

## Prometheus Metrics

```yaml
maestro:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      interval: 30s
      labels:
        release: kube-prometheus-stack
```

---

## Complete Example (OpenAI)

```yaml
maestro:
  enabled: true
  model:
    provider: openai
  openai:
    apiKey:
      secretKeyName: 'openai-secret'
      secretKeyRef: 'api-key'
  log-llm-requests: 'false'
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      labels:
        release: kube-prometheus-stack

api:
  remoteApi:
    enabled: true
```

---

## Verify It Works

Check that the Maestro pod is running:

```bash
kubectl get pods -n hume -l app.kubernetes.io/name=hume-maestro
```

Expected output:

```
NAME                           READY   STATUS    RESTARTS   AGE
hume-maestro-7d9c84b5f-lkp2q   1/1     Running   0          2m
```

Confirm startup:

```bash
kubectl logs -l app.kubernetes.io/name=hume-maestro -n hume | grep -i "started\|listening\|running"
```

---

## Next Steps

- [Alerting](alerting.md) — rule-based alert engine
- [Remote API / API Keys](../installation/basic-installation.md) — managing API key access
- [Monitoring](../production/monitoring.md) — Prometheus ServiceMonitor setup
