# Kafka Websocket Proxy
This guide describes setting up [Kafka Websocket Proxy](https://kpmeen.gitlab.io/kafka-websocket-proxy/).
This proxy serves as a bridge between a Kafka cluster and WebSocket clients, enabling real-time data streaming from Kafka topics to WebSocket clients.

## Prerequisites:
- Kafka Cluster deployed
- Added `127.0.0.1 sitevisor.local` ìn `/etc/hosts`

**Deploy the Kafka WebSocket Proxy:**

```bash
echo "
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-websocket-proxy
  namespace: kafka
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
" | kubectl apply -f - 
```

**Create a Serivce for the Kafka WebSocket Proxy:**
```bash
echo "
apiVersion: v1
kind: Service
metadata:
  name: kafka-websocket-proxy-service
  namespace: kafka
spec:
  type: ClusterIP
  selector:
    app: kafka-websocket-proxy
  ports:
    - port: 8078
      targetPort: 8078
      protocol: TCP
" | kubectl apply -f -
```

**Ingress for the Kafka WebSocket Proxy:**
```bash
echo "
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
 name: kafka-websocket
 namespace: kafka
 annotations:
  nginx.ingress.kubernetes.io/proxy-read-timeout: '3600'
  nginx.ingress.kubernetes.io/proxy-send-timeout: '3600'
  nginx.ingress.kubernetes.io/server-snippets: |
   location / {
    proxysetheader Upgrade $httpupgrade;
    proxyhttpversion 1.1;
    proxysetheader X-Forwarded-Host $httphost;
    proxysetheader X-Forwarded-Proto $scheme;
    proxysetheader X-Forwarded-For $remoteaddr;
    proxysetheader Host $host;
    proxysetheader Connection 'upgrade';
    proxycachebypass $httpupgrade;
    }
spec:
  rules:
  - host: sitevisor.local
    http:
      paths:
      - path: /socket
        pathType: Prefix
        backend:
          service:
            name: kafka-websocket-proxy-service
            port:
              number: 8078
  ingressClassName: nginx
" | kubectl apply -f -
```

**Test connection again and see if the data is received through the websocket:**
```bash
curl -X POST http://sitevisor.local:8080/topics/my-topic \
     -H "Content-Type: application/vnd.kafka.json.v2+json" \
     --data '{"records": [{"value": "Test message..."}]}'
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