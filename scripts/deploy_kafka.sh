#!/bin/bash

# Exit script on error
set -e

HOSTNAME="sitevisor.local"

# Create kafka namespace
echo "Creating 'kafka' namespace..."
kubectl create namespace kafka || echo "'kafka' namespace already exists"

# Apply Strimzi install files
echo "Applying Strimzi install files..."
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Deploy Kafka cluster
echo "Deploying Kafka cluster..."
cat <<EOF | kubectl apply -n kafka -f -
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
EOF

# Deploy KafkaBridge
echo "Deploying Kafka Bridge..."
cat <<EOF | kubectl apply -n kafka -f -
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
  consumer:
    config:
      auto.offset.reset: earliest
  producer:
    config:
      delivery.timeout.ms: 300000
EOF

# Expose KafkaBridge Service
echo "Exposing Kafka Bridge Service..."
cat <<EOF | kubectl apply -n kafka -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kafka-bridge
  namespace: kafka
spec:
  rules:
  - host: ${HOSTNAME}
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
EOF

# Create a test Kafka Topic
echo "Creating a test Kafka Topic..."
cat <<EOF | kubectl create -n kafka -f -
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
EOF

# Send a test message to Kafka
echo "Sending a test message to Kafka..."
curl -X POST http://${HOSTNAME}:8080/topics/my-topic \
     -H "Content-Type: application/vnd.kafka.json.v2+json" \
     --data '{"records": [{"value": "Test message..."}]}'
     
echo "Kafka deployment and test completed."
