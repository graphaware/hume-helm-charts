# 2.27.4

# 2.27.0

- [Breaking change] : Kubernetes/Helm labels standardization. This change requires manual deletion of all deployments and statefulsets because of `.spec.selector` labels change.
- [Breaking change]: Because of recent Bitnami [update](https://github.com/bitnami/charts/issues/35164) we have migrated all Bitnami 3rd party Docker images and Helm charts to our Docker registry.
- Added pod anti affinity for hume-api, hume-orchestra and hume-alerting services.
- Bumped Keycloak helm chart to `14.4.0` and Keycloak image version to `21`.
- Extended web deployment with options to add custom nginx headers. Below an example of values for `web.extraHeaders`.
    ```
    extraHeaders:
      - add_header X-Custom1 "custom header 1";
      - add_header X-Custom2 "custom header 2";
    ```

# 2.26.1

- [Breaking change] : The `postgresqlEventstore.enabled` value is now `false` by default, this prevents an orphan postgresql server to be deployed even if the eventstore service itself was disabled.
- [Breaking change] : The `postgresqlMedia.enabled` value is now `false` by default, this prevents an orphan postgresql server to be deployed even if the media service itself was disabled.
- Add Maestro deployment

# 2.26

- Added hume-media statefulset.
- Added `extraConfigMaps` to hume-api for providing externally created configmaps to the api environment.

# 2.25 

# 2.25.2

- Fixed an issue where the `app.kubernetes.io/component` label would be duplicated when metrics were enabled, this is now fixed by using a custom label `obs.hume.k8s.io/component` for referencing the service in service monitors.

## 2.25.0
- Added support for `volumes` in eventstore deployment.

# 2.19.0-SNAPSHOT

- Added support for Prometheus service monitor.
- Added support for zookeeper less Orchestra clustering.
- Added support for overriding app version for all services in values.yml.

# 2.18

- Moved `alerting.client.enabled` to `api-configmap`.
- Support for `remote api initial key creation` and `initial key token` from existing secret.
- Upgrade app version to 2.18.0.
