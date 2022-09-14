<!--- app-name: Hume -->

# Hume packaged by GraphAware

Hume is a 

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
$ kubectl create secret docker-registry graphaware-docker-creds --docker-server='docker.graphaware.com' --docker-username='<username>' --docker-password='<password>' --docker-email='<email>' -n helm
```
2, Add GraphAware Helm repository and install it:
```bash
$ helm repo add --username '<username>' --password '<password>' graphaware https://docker.graphaware.com/chartrepo/public

$ helm install my-release graphaware/hume --set baseDomain=<your-domain> -n hume
or
$ helm install my-release graphaware/hume -n hume -f values.yaml
```

These commands deploy a Hume application on the Kubernetes cluster in the default configuration.

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```bash
$ helm uninstall my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Ingress

xxx

## Parameters

### Global parameters
| Name                      | Description                                     | Value |
| ------------------------- | ----------------------------------------------- | ----- |
| `global.imageRegistry`    | Global Docker image registry                    | `""`  |
| `global.imagePullSecrets` | Global Docker registry secret names as an array | `[]`  |
| `global.storageClass`     | Global StorageClass for Persistent Volume(s)    | `""`  |

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
