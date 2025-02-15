# 2.26

- Added hume-media statefulset
- Added `extraConfigMaps` to hume-api for providing externally created configmaps to the api environment

# 2.25 

# 2.25.2

- Fixed an issue where the `app.kubernetes.io/component` label would be duplicated when metrics were enabled, this is now fixed by using a custom label `obs.hume.k8s.io/component` for referencing the service in service monitors.

## 2.25.0
- Added support for `volumes` in eventstore deployment

# 2.19.0-SNAPSHOT

- Added support for Prometheus service monitor
- Added support for zookeeper less Orchestra clustering
- Added support for overriding app version for all services in values.yml

# 2.18

- Moved `alerting.client.enabled` to `api-configmap`
- Support for `remote api initial key creation` and `initial key token` from existing secret
- Upgrade app version to 2.18.0
