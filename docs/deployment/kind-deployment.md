# Deploying the backend in Kind

## Prerequisites
- Docker: Ensure **Docker** is installed on your system. You can download and install Docker from [Docker's official website](https://www.docker.com/get-started/).
- Kind: Install **kind** on your machine. Follow the installation instructions on the [kind website](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).


## Kind deployment
**Create the Kind cluster:**

Skip this step if you are deploying to already existing cluster
```bash
kind create cluster
```

**Build and Load the Docker Image into kind:**
```bash
docker build -t sitevisor-backend:dev .
```

**Load the Image into your kind Cluster:**
```bash
kind load docker-image sitevisor-backend:dev
```

**Create the deployment:**
```bash
echo "
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sitevisor-backend-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sitevisor-backend
  template:
    metadata:
      labels:
        app: sitevisor-backend
    spec:
      containers:
      - name: sitevisor-backend
        image: sitevisor-backend:dev
        ports:
        - containerPort: 8000
" | kubectl apply -f -
```

**Create a service to expose the application:**
```bash
echo "
apiVersion: v1
kind: Service
metadata:
  name: sitevisor-backend-service
spec:
  selector:
    app: sitevisor-backend
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: NodePort
" | kubectl apply -f -
```

**Set up port forwarding to access the service in Kind cluster:**
```bash
kubectl port-forward service/sitevisor-backend-service 4000:8000
```

**Access the application:**

Open your browser and go to http://localhost:4000.

**Cleanup**
```bash
kind delete cluster
```