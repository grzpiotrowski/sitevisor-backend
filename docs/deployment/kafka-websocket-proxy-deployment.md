# Kafka Websocket Proxy
This guide describes setting up [Kafka Websocket Proxy](https://kpmeen.gitlab.io/kafka-websocket-proxy/).
This proxy serves as a bridge between a Kafka cluster and WebSocket clients, enabling real-time data streaming from Kafka topics to WebSocket clients.

**Deploy the Kafka WebSocket Proxy:**

```bash
echo "
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-websocket-proxy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka-websocket-proxy
  template:
    metadata:
      labels:
        app: kafka-websocket-proxy
    spec:
      containers:
      - name: kafka-websocket-proxy
        image: kpmeen/kafka-websocket-proxy:1.2.0
        ports:
        - containerPort: 8078
        env:
          - name: WSPROXY_KAFKA_BOOTSTRAP_HOSTS
            value: 'kafka-sitevisor-cluster-kafka-bootstrap:9092'
" | kubectl apply -n kafka -f - 
```

**Expose the Kafka WebSocket Proxy as a Service:**

```bash
echo "
apiVersion: v1
kind: Service
metadata:
  name: kafka-websocket-proxy-service
spec:
  type: NodePort
  selector:
    app: kafka-websocket-proxy
  ports:
    - port: 8078
      targetPort: 8078
      protocol: TCP
" | kubectl apply -n kafka -f -
```

**Port Forwarding to access the Service locally:**
```bash
kubectl port-forward service/kafka-websocket-proxy-service 8078:8078 -n kafka
```

**Running a Kafka Producer for connection testing:**
Run a simple producer to send messages to a Kafka topic:
```bash
kubectl -n kafka run kafka-producer -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.1 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server kafka-sitevisor-cluster-kafka-bootstrap:9092 --topic my-topic
```

**WebSocket URL for connecting clients:**

This WebSocket URL is used by clients to connect to the Kafka WebSocket Proxy. Clients can subscribe to the Kafka topic `my-topic` through this WebSocket connection to receive real-time messages.
```
ws://localhost:8078/socket/out?clientId=console_consumer&topic=my-topic
```