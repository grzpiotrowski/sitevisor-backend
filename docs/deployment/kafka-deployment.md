# Creating an Apache Kafka cluster

**Create a `kafka` namespace:**
```bash
kubectl create namespace kafka
```

**Apply the Strimzi install files:**
```bash
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
```

**Create a new Kafka custom resource:**
This sets up a small persistent Apache Kafka Cluster with one node for Apache Zookeeper and Apache Kafka:
```bash
echo "
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-sitevisor-cluster
spec:
  kafka:
    version: 3.6.1
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: '3.6'
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 25Gi
        deleteClaim: false
  zookeeper:
    replicas: 1
    storage:
      type: persistent-claim
      size: 25Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
" | kubectl apply -n kafka -f -
```

## Testing

Run a simple producer to send messages to a Kafka topic:
```bash
kubectl -n kafka run kafka-producer -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.1 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server kafka-sitevisor-cluster-kafka-bootstrap:9092 --topic my-topic
```

In another terminal run a cosumer to receive the messages from `my-topic` Kafka topic:
```bash
kubectl -n kafka run kafka-consumer -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.1 --rm=true --restart=Never -- bin/kafka-console-consumer.sh --bootstrap-server kafka-sitevisor-cluster-kafka-bootstrap:9092 --topic my-topic --from-beginning
```