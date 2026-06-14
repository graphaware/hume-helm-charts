# Authentication

Configure how users log in to Hume — native user management, internal Keycloak SSO, or an existing Keycloak server.

---

## Choosing an Authentication Mode

| Mode | Best for | Trade-offs |
|---|---|---|
| **Native** | Dev, small internal teams | No SSO; user management is per-Hume |
| **Internal Keycloak** | Teams wanting SSO without an existing IdP | Simple to enable; not HA |
| **External Keycloak** | Organizations with an existing Keycloak or OIDC provider | Most robust; requires Keycloak setup outside the chart |

---

## Mode 1: Native Authentication (Default)

Hume ships with its own user management system. No external identity provider is needed.

The default admin account is created automatically:

| | |
|---|---|
| **Username** | `admin@hume.k8s` |
| **Password** | `password` |

> **Security callout:** Change the default admin password before exposing Hume to any network. The default password is publicly documented and must not be used in production.

To set custom admin credentials at install time:

```yaml
api:
  admin:
    auto_create: true
    username: admin@example.com
    password: "<strong-random-password>"
```

Native mode requires no additional values — this is the out-of-the-box behavior.

---

## Mode 2: Internal Keycloak

The chart includes a Bitnami Keycloak sub-chart that you can enable to get SSO without managing a separate Keycloak installation.

```yaml
keycloak:
  useKeycloak:
    enabled: true
  internal:
    enabled: true
  realm: "hume"
  client: "hume-web"
```

With ingress enabled, Keycloak is available at `hume-keycloak.<baseDomain>`. Without ingress, access it via port-forward:

```bash
kubectl port-forward service/hume-keycloak 8180:8180 -n hume
# Then open http://localhost:8180
```

> **Production callout:** The bundled Keycloak runs as a single pod with no replication. For production SSO, use an externally managed Keycloak instance (Mode 3).

---

## Mode 3: External Keycloak

Point Hume at an existing Keycloak server. Both the API and the Web UI need to know where Keycloak is.

```yaml
keycloak:
  useKeycloak:
    enabled: true
  internal:
    enabled: false
  customKeycloak:
    customKeycloakEndpoint: "https://identity.example.com/auth"
  realm: "hume"
  client: "hume-web"

api:
  env:
    - name: "keycloak.enabled"
      value: "true"
    - name: "keycloak.realm"
      value: "hume"
    - name: "keycloak.resource"
      value: "hume-web"
    - name: "keycloak.auth-server-url"
      value: "https://identity.example.com/auth"

web:
  env:
    - name: "KEYCLOAK_ENABLED"
      value: "true"
    - name: "KEYCLOAK_URL"
      value: "https://identity.example.com/auth"
    - name: "KEYCLOAK_REALM"
      value: "hume"
    - name: "KEYCLOAK_CLIENT"
      value: "hume-web"
```

### Keycloak realm and client requirements

Before installing with external Keycloak, configure your Keycloak server:

1. **Create a realm** named to match your `keycloak.realm` value (e.g., `hume`).
2. **Create a client** named to match your `keycloak.client` value (e.g., `hume-web`).
3. Configure the client's **Valid Redirect URIs** to include:
   - `https://hume-web.<your-domain>/*`
   - `https://hume-api.<your-domain>/*`
4. Set **Web Origins** to `+` (or the explicit Hume domain) to allow CORS.
5. Enable **Standard Flow** (Authorization Code) on the client.

---

## API Key Authentication

For programmatic access, CI pipelines, or integrations, Hume supports API key authentication independent of the identity mode above.

Enable the remote API:

```yaml
api:
  remoteApi:
    enabled: true
```

### Creating an initial API key at install time

Useful for automation that needs an API key from first boot:

```yaml
api:
  remoteApi:
    enabled: true
  media:
    initialKey:
      create: true
      name: "automation-key"
      token: "<strong-random-token>"
      roles: "ADMINISTRATOR"
```

> Use `roles: "ADMINISTRATOR"` only for trusted automation. For read-only integrations, use `"USER"`.

### Using an existing Kubernetes secret for the token

Avoid putting the token in plain text in your values file by referencing an existing secret:

```yaml
api:
  remoteApi:
    enabled: true
  media:
    initialKey:
      create: true
      name: "automation-key"
      roles: "ADMINISTRATOR"
      existingSecret: "hume-api-key-secret"
      existingSecretKey: "token"          # optional, defaults to "token"
```

Create the secret before installing:

```bash
kubectl create secret generic hume-api-key-secret \
  --from-literal=token='<strong-random-token>' \
  -n hume
```

---

## Verify It Works

**Native auth:**

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST https://hume-api.<your-domain>/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@hume.k8s","password":"<your-password>"}'
# Expected: 200
```

**Keycloak:**

After install, open `https://hume-web.<your-domain>` — you should be redirected to the Keycloak login page.

**API key:**

```bash
curl -s -o /dev/null -w "%{http_code}" \
  https://hume-api.<your-domain>/api/status \
  -H "X-API-Key: <your-token>"
# Expected: 200
```

---

## Next Steps

- [Ingress](ingress.md) — Expose Hume externally before testing SSO redirects
- [Databases](databases.md) — Configure PostgreSQL for the API
- [Security](../production/security.md) — Secrets management and pod security
