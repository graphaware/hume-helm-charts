<!--- app-name: Hume -->

# Hume packaged by GraphAware

Hume is an enterprise-level graph analytics solution that is easy to set up, maintain, and use. Hume helps organisations gain a competitive advantage by leveraging the power of graphs.

[Overview of Hume](https://www.graphaware.com/products/hume/)

Trademarks: This software listing is packaged by GraphAware. The respective trademarks mentioned in the offering are owned by the respective companies, and use of them does not imply any affiliation or endorsement.

## Introduction

GraphAware charts for Helm are carefully engineered, actively maintained and are the quickest and easiest way to deploy containers on a Kubernetes cluster that are ready to handle production workloads.

This chart bootstraps a [Hume](https://github.com/graphaware/hume-helm-charts) deployment on a [Kubernetes](https://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Customer account in https://docker.graphaware.com/ in order to download both Helm chart and docker images
- A Hume licence key

## Installing the Chart

### Prepare the release

1. Create a new namespace dedicated for Hume, assuming `hume` will be the namespace name
```bash
kubectl create namespace hume
```

2. Create the `docker-registry` secret with your GraphAware docker registry credentials
```bash
kubectl create secret docker-registry graphaware-docker-creds --docker-server='docker.graphaware.com' --docker-username='<username>' --docker-password='<password>' -n hume
```

3. Optionally, create the `hume-licence` secret with your Hume licence key (.b64 file content)
```bash
kubectl create secret generic --from-literal=hume.licence.key=<licence-b64-string> -n hume
```

> **NOTE**
> Providing the `hume-licence` secret will install the licence automatically. If not provided you will be prompt to upload the licence file when logging in to Hume for the first time.

4. Add the GraphAware OCI Helm repository to your local repository
```bash
helm registry login -u  '<username>' docker.graphaware.com
helm pull oci://docker.graphaware.com/public/hume --version 2.21.0
```

### Install the Helm chart

Assuming `hume` is the namespace name and `my-release` is the helm release name.

```bash
$ helm install my-release oci://docker.graphaware.com/public/hume --version 2.21.0
or
$ helm install my-release oci://docker.graphaware.com/public/hume --version 2.21.0 -n hume -f values.yaml
```
> **NOTE**  
> These commands deploy a Hume application on the Kubernetes cluster in the default configuration. It means that the Hume application will not be exposed to the Internet. If you want to access it via Ingress below we will provide a few examples.

### Verify the installation

1. Check the pods are ready
```bash
kubectl get pods -n hume
NAME                       READY   STATUS    RESTARTS        AGE
dev-release-0              1/1     Running   0               8m24s
hume-api-897bbccb7-6g6vk   1/1     Running   1 (8m13s ago)   8m24s
hume-orchestra-0           1/1     Running   0               8m24s
hume-web-8d7d855fc-kwhvv   1/1     Running   0               8m24s
postgresql-core-0          1/1     Running   0               8m24s
```

2. Check the services look OK

```bash
kubectl get svc -n hume
NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                                        AGE
dev-release          ClusterIP      10.99.0.111     <none>        7687/TCP,7474/TCP,7473/TCP                     9m29s
dev-release-admin    ClusterIP      10.100.142.91   <none>        6362/TCP,7687/TCP,7474/TCP,7473/TCP            9m29s
dev-release-neo4j    LoadBalancer   10.106.141.47   localhost     7474:31776/TCP,7473:31964/TCP,7687:30353/TCP   9m29s
hume-api             NodePort       10.97.248.25    <none>        8080:32081/TCP                                 9m29s
hume-orchestra       ClusterIP      10.98.32.28     <none>        8100/TCP                                       9m29s
hume-web             ClusterIP      10.104.105.20   <none>        8081/TCP                                       9m29s
postgresql-core      ClusterIP      10.106.90.201   <none>        5432/TCP                                       9m29s
postgresql-core-hl   ClusterIP      None            <none>        5432/TCP                                       9m29s
```

3. Use `port-forwarding` to get access to the Hume user interface

From one terminal run the following command : 
```bash
kubectl port-forward service/hume-web 8081:8081 -n hume
```

From another terminal run the following command : 
```bash
kubectl port-forward service/hume-api 8080:8080 -n hume
```

In a web browser, open the Hume user interface at http://localhost:8081.

Use the default username/password `admin@hume.k8s / password` to log in to Hume.

## Ingress

In order to deploy Ingress resource we have to define `baseDomain` parameter and annotations per your Ingress Controller.

**[AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.4/)**

Example of `values.yaml`:
```bash
baseDomain: "<your-domain>"
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: "internal"
    alb.ingress.kubernetes.io/group.name: "default-internal"
    alb.ingress.kubernetes.io/target-type: "ip"
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}, {"HTTP":80}]'
    alb.ingress.kubernetes.io/actions.ssl-redirect: '{"Type": "redirect", "RedirectConfig": { "Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
```

**[Nginx Ingresss Controller](https://kubernetes.github.io/ingress-nginx/)**

Example of `values.yaml`:
```bash
baseDomain: "<your-domain>"
ingress:
  enabled: true
  ingressClassName: nginx
  annotations:
```
## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```bash
$ helm uninstall my-release -n hume
```
The command removes all the Kubernetes components associated with the chart and deletes the release.
## Parameters

| Name                      | Description                                                                         | Value                             |
| ------------------------- | ----------------------------------------------------------------------------------- | --------------------------------- |
| `baseDomain`              | Domain name (for example graphaware.com)                                            | `""`                              |
| `imagePullSecrets`        | Docker registry secret name                                                         | `graphaware-docker-creds`         |
| `autoscaling`             | Enable autoscaling for Hume                                                         | `"false"`                         |
| `deploymentStrategy`      | Kubernetes Deployment Strategy Type                                                 | `"RollingUpdate"`                 |
| `nameOverride`            | String to partially override hume.fullname                                          | `""`                              |
| `fullnameOverride`        | String to fully override hume.fullname                                              | `"hume"`                          |
| `ingress.enabled`         | Enables ingress                                                                     | `"false"`                         |
| `autoscaling`             | Enable autoscaling for Hume                                                         | `"false"`                         |
| `keycloak.enabled`        | Enable Keycloak                                                                     | `"false"`                         |
| `serviceAccount.create`   | Enable ServiceAccount                                                               | `"true"`                          |

## Using your own Docker registry

When you need to use your own Docker registry, for example in air gapped environments you will need to copy the images from our Docker registry to yours.

Additionally you need to adapt the chart to change the coordinates of the Docker images, to do so you can 
override the following values : 

| Chart | value | default | override |
| --- | --- | --- | --- |
| hume-core | `humeCoreBaseRepository` | `docker.graphaware.com/hume-core/` | `your-docker-domain.example/` |
| hume-alerting | `humeAlertingBaseRepository` | `docker.graphaware.com/hume-alerting/` | `your-docker-domain.example/` |

**Don't forget the trailing slash at the end of the repository name**

## Overriding container environment variables

The chart comes with default sensible environment variables. Those variables can be overriden for each service in their respective `env` section.

For eg, to use a secret for the API postgres database password, you can provide the secret name like this 

```yaml
# values.yml
api:
  env:
    - name: spring.datasource.password
      valueFrom:
        secretKeyRef:
          key: db-password
          name: api-postgres-db-password
```

## Deployment with all the persistence outside of Kubernetes

It is not uncommon to have a PostgreSQL server and Neo4j server outside of Kubernetes. It's then necessary to disable all persistence dependencies and override the defaults for connections to those, Keycloak is often installed outside of the chart as well.

See [`deployment-scenarios/external-persistence/values.yaml`](./deployment-scenarios/external-persistence/values.yml) for an example configuration.

## Install specific versions

You can install a specific version of the chart by specifying the chart version 

```bash
helm install my-release graphaware/hume -f values.yml --version 2.16.8
```

## Initial API Key creation

Hume can be configured to have an initial api key created when the application starts the first time.

```yaml
api:
  remoteApi:
    enabled: true
    initialKey:
      create: true
      name: my-initial-key
      token: my-insecure-token
      roles: ADMINISTRATOR
```

Optionally, you can use an existing secret for the token

```yaml
api:
  remoteApi:
    enabled: true
      initialyKey:
        create: true
        name: my-initial-key
        roles: ADMINISTRATOR
        existingSecret: hume-api-key-secret # name of the secret to use
        existingSecretKey: secret # optional, defaults to "token"
```


## License

Copyright &copy; 2022 GraphAware

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
