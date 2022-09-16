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

## Installing the Chart

To install the chart with the release name `my-release`:

1, Create Docker secret in order to pull Docker images from private registry:
```bash
$ kubectl create namespace hume
$ kubectl create secret docker-registry graphaware-docker-creds --docker-server='docker.graphaware.com' --docker-username='<username>' --docker-password='<password>' --docker-email='<email>' -n hume
```
2, Add GraphAware Helm repository and install it:
```bash
$ helm repo add --username '<username>' --password '<password>' graphaware https://docker.graphaware.com/chartrepo/public

$ helm install my-release graphaware/hume -n hume
or
$ helm install my-release graphaware/hume -n hume -f values.yaml
```
> **_NOTE:_**  These commands deploy a Hume application on the Kubernetes cluster in the default configuration. It means that the Hume application will not be exposed to the Internet. If you want to access it via Ingress below we will provide a few examples.

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
Footer
© 2022 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
