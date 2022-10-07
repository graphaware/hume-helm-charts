# Hume Alerting Chart



## Installing the Chart



### **Add the graphware helm repository**

``` helm repo add --username <username> --password <password> <repo name> https://docker.graphaware.com/chartrepo/public ```

### **Add required secrets** 
The following secrets must be defined in the target namespace prior to the installation of the helm alerting chart.

**graphaware-docker-creds**
```shell
kubectl create secret docker-registry graphaware-docker-creds --docker-server=<your-registry-server> --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email> -n <namspace>
```
**kafka-alerting-controller**
```
kubectl create secret generic kafka-alerting-controller \
--from-literal=org.apache.kafka.common.security.plain.PlainLoginModule REQUIRED username='<username>' password='<password>'; -n <namespace>
```
**kafka-alerting-operator**
```
kubectl create secret generic kafka-alerting-operator \
--from-literal=spring.kafka.properties.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule REQUIRED username='<username>' password='<password>'; -n <namespace>
```
**postgresql-alerting-controller**
``` 
    kubectl create secret generic postgresql-alerting-controller \
	--from-literal=POSTGRES-PASSWORD=<password> -n <namespace>
```
**postgresql-alerting-operator**	
``` 
    kubectl create secret generic postgresql-alerting-operator \
	--from-literal=POSTGRES-PASSWORD=<password> -n <namespace>
```


### **Required Parameters**
The following tables lists the configurable parameters of the Hume alerting chart and their default values.

```markdown
| Parameter 	                     | Description 	     | Default 	| 
|-----------	                     |-------------	     |---------	|
| kafka.host 	                     |  Kafka hostname   |    nil  	|
```


### **Install**
```
helm install --ca-file <ca file> --cert-file <cert file> --key-file <key file>  --username=<username> --password=<password> --version <chart version> <repo name>/hume-alerting --set kafka.host=<kafka hostname>
