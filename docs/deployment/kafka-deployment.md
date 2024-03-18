# Creating an Apache Kafka cluster

## Prerequisites
- Added `127.0.0.1 sitevisor.local` ìn `/etc/hosts`

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

**Create the KafkaBridge resource:**
```bash
echo "
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaBridge
metadata:
  name: kafka-bridge
  namespace: kafka
spec:
  replicas: 1
  bootstrapServers: kafka-sitevisor-cluster-kafka-bootstrap:9092
  http:
    port: 8088
    cors:
      allowedMethods:
        - GET
        - POST
        - DELETE
        - ACCEPT
        - OPTIONS
      allowedOrigins:
        - 'http://localhost:5173'
  consumer:
    config:
      auto.offset.reset: earliest
  producer:
    config:
      delivery.timeout.ms: 300000
" | kubectl apply -f -
```

**Expose KafkaBridge Service:**
```bash
echo "
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kafka-bridge
  namespace: kafka
spec:
  rules:
  - host: sitevisor.local
    http:
      paths:
      - path: /topics
        pathType: Prefix
        backend:
          service:
            name: kafka-bridge-bridge-service
            port:
              number: 8088
  ingressClassName: nginx
" | kubectl apply -f -
```

**Create a test Kafka Topic:**
```bash
echo "
apiVersion: kafka.strimzi.io/v1beta1
kind: KafkaTopic
metadata:
  name: my-topic
  namespace: kafka
  labels:
    strimzi.io/cluster: 'kafka-sitevisor-cluster'
spec:
  partitions: 3
  replicas: 1
" | kubectl create -f -
```

**Curl a test message to Kafka:**
```bash
curl -X POST http://sitevisor.local:8080/topics/my-topic \
     -H "Content-Type: application/vnd.kafka.json.v2+json" \
     --data '{"records": [{"value": "Test message..."}]}'
```