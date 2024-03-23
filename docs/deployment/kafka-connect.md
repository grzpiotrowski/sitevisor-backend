# Kafka Connect


Based on Srimzi docs: [Building a new container image with connector plugins automatically](https://strimzi.io/docs/operators/latest/full/deploying#creating-new-image-using-kafka-connect-build-str)

## Create Docker Hub Access Token:
Go to your Docker account -> My Account -> Security -> New Access Token
Copy the generated personal access token.

Now go to Repositories -> Create Repository

Create secret with credentials to access your docker repository from Kubernetes:
```bash
kubectl create secret docker-registry docker-secret --docker-server="https://index.docker.io/v1/" --docker-username=${DOCKERUSER} --docker-password=${DOCKERTOKEN} --namespace=kafka
```

## Kafka Connect
Create KafkaConnect:
```bash
echo "
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: kafka-connect-sitevisor
  namespace: kafka
  annotations:
    strimzi.io/use-connector-resources: 'true'
spec:
  version: 3.6.1
  replicas: 1
  bootstrapServers: kafka-sitevisor-cluster-kafka-bootstrap:9092
  config:
    group.id: kafka-connect-sitevisor
    config.storage.topic: kafka-connect-configs
    offset.storage.topic: kafka-connect-offsets
    status.storage.topic: kafka-connect-status
    key.converter: org.apache.kafka.connect.json.JsonConverter
    value.converter: org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable: false
    value.converter.schemas.enable: false
    config.storage.replication.factor: -1
    offset.storage.replication.factor: -1
    status.storage.replication.factor: -1
  build:
    output:
      type: docker
      image: grzpiotrowski/kafka-connect-sitevisor:latest
      pushSecret: docker-secret
    plugins:
      - name: debezium-debezium-connector-jdbc
        # https://debezium.io/documentation/reference/stable/connectors/jdbc.html
        artifacts:
          - type: tgz
            url: https://repo1.maven.org/maven2/io/debezium/debezium-connector-jdbc/2.5.3.Final/debezium-connector-jdbc-2.5.3.Final-plugin.tar.gz
" | kubectl apply -n kafka -f -
```


Create KafkaConnector Sink to store messages in PostgreSQL database:
```bash
echo "
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: postgres-sink-connector
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-connect-sitevisor
spec:
  class: io.debezium.connector.jdbc.JdbcSinkConnector
  config:
    tasks.max: 1
    connection.url: jdbc:postgresql://sitevisor-db-cluster-rw.postgres-operator:5432/
    connection.username: sitevisoruser
    connection.password: secret
    insert.mode: upsert
    delete.enabled: false
    primary.key.mode: record_key
    database.time_zone: UTC
    topics: my-topic3
    key.converter: org.apache.kafka.connect.json.JsonConverter
    value.converter: org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable: true
    value.converter.schemas.enable: true
" | kubectl apply -n kafka -f -
```