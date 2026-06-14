# Ingress

Configure how external traffic reaches Hume's Web UI and API.

---

## How Hostnames Are Composed

Set `baseDomain` in your values file and the chart creates ingress resources with the following hostnames:

| Service | Hostname |
|---|---|
| Hume Web UI | `hume-web.<baseDomain>` |
| Hume API | `hume-api.<baseDomain>` |
| Keycloak (if internal Keycloak enabled) | `hume-keycloak.<baseDomain>` |

```yaml
baseDomain: "example.com"
```

---

## Pattern 1: No Ingress (Port-Forward)

**Use for:** local development, quick evaluation, or when you have no ingress controller installed.

No ingress configuration is needed. Run two `kubectl port-forward` commands in separate terminals:

```bash
# Terminal 1 — Web UI
kubectl port-forward service/hume-web 8081:8081 -n hume

# Terminal 2 — API
kubectl port-forward service/hume-api 8080:8080 -n hume
```

Then open `http://localhost:8081` in your browser.

---

## Pattern 2: AWS Load Balancer Controller (ALB)

**Use for:** EKS clusters with the [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/) installed.

```yaml
baseDomain: "<your-domain>"

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: "internal"
    alb.ingress.kubernetes.io/group.name: "default-internal"
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}, {"HTTP":80}]'
    alb.ingress.kubernetes.io/actions.ssl-redirect: '{"Type": "redirect", "RedirectConfig": { "Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
    alb.ingress.kubernetes.io/load-balancer-attributes: "idle_timeout.timeout_seconds=300"
```

### Key annotation notes

**`scheme: internal` vs `internet-facing`**

- `internal`: ALB is only reachable within your VPC. Use this for internal tooling, developer portals, or when Hume sits behind a VPN or another proxy.
- `internet-facing`: ALB has a public IP. Use this only if Hume must be accessible from the public internet.

**`group.name`**

Groups multiple Ingress resources onto a single ALB. All Hume ingress resources (Web, API, Keycloak) that share the same `group.name` share one load balancer, saving cost. You can add other applications to the same group with the same annotation.

**`target-type: ip`**

Required for ALB to route directly to pod IPs. This is the correct mode when your nodes run in a VPC and your pods have routable IPs (typical in EKS with VPC CNI).

**TLS with ACM**

Add the ACM certificate annotation to terminate TLS at the ALB:

```yaml
ingress:
  annotations:
    # ... (all annotations above) ...
    alb.ingress.kubernetes.io/certificate-arn: "arn:aws:acm:<region>:<account-id>:certificate/<cert-id>"
```

---

## Pattern 3: Nginx Ingress Controller

**Use for:** most non-AWS environments, bare-metal clusters, GKE, AKS, or EKS with the Nginx controller instead of ALB.

```yaml
baseDomain: "<your-domain>"

ingress:
  enabled: true
  ingressClassName: nginx
  annotations: {}
```

### With TLS using an existing secret

If you already have a TLS secret (created manually or by cert-manager):

```yaml
baseDomain: "<your-domain>"

ingress:
  enabled: true
  ingressClassName: nginx
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  tls:
    - secretName: hume-tls-secret
      hosts:
        - "hume-web.<your-domain>"
        - "hume-api.<your-domain>"
```

### With cert-manager (automatic TLS)

```yaml
baseDomain: "<your-domain>"

ingress:
  enabled: true
  ingressClassName: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  tls:
    - secretName: hume-tls-secret
      hosts:
        - "hume-web.<your-domain>"
        - "hume-api.<your-domain>"
```

> **Production callout:** Always configure TLS. Sending Hume credentials or session tokens over plain HTTP is a security risk. If you use an internal CA, configure your ingress controller accordingly.

---

## Orchestra Webhooks

Orchestra exposes a webhook endpoint on port **8101** per replica. This port does **not** get an ingress resource automatically from the chart.

If you need external systems to trigger Orchestra workflows via webhooks, create your own Ingress resource pointing to the service for each replica:

```yaml
# Example: ingress for replica 0 webhook endpoint
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orchestra-webhook-0
  namespace: hume
  annotations:
    kubernetes.io/ingress.class: "alb"
    # (add your controller-specific annotations here)
spec:
  rules:
    - host: "orchestra-webhook.example.com"
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: hume-orchestra-webhook-0
                port:
                  number: 8101
```

In Orchestra cluster mode (multiple replicas), each replica has its own webhook service (`hume-orchestra-webhook-0`, `hume-orchestra-webhook-1`, etc.) and needs its own ingress or routing rule.

---

## Verify It Works

After applying your values and running `helm upgrade --install`, check that the ingress resources were created:

```bash
kubectl get ingress -n hume
```

Expected output (Nginx example):

```
NAME                  CLASS   HOSTS                        ADDRESS          PORTS     AGE
hume-api-ingress      nginx   hume-api.example.com         203.0.113.5      80, 443   2m
hume-web-ingress      nginx   hume-web.example.com         203.0.113.5      80, 443   2m
```

Then confirm the URL is reachable:

```bash
curl -I https://hume-web.<your-domain>/
# Expected: HTTP/2 200
```

---

## Next Steps

- [Authentication](authentication.md) — Configure user login and SSO
- [Basic Installation](../installation/basic-installation.md) — Full install walkthrough
