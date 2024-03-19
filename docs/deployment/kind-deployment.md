# Deploying the SiteVisor Backend

## Prerequisites
- Docker: Ensure **Docker** is installed on your system. You can download and install Docker from [Docker's official website](https://www.docker.com/get-started/).
- Kind: Install **kind** on your machine. Follow the installation instructions on the [kind website](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).
- Added `127.0.0.1 sitevisor.local` ìn `/etc/hosts`

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
      initContainers:
      - name: apply-migrations
        image: sitevisor-backend:dev
        command: ['python', 'manage.py', 'migrate']
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
" | kubectl apply -f -
```

**Ingress for SiteVisor backend:**
```bash
echo "
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sitevisor-backend-ingress
spec:
  rules:
  - host: sitevisor.local
    http:
      paths:
      - pathType: Prefix
        path: /api
        backend:
          service:
            name: sitevisor-backend-service
            port:
              number: 8000
      - pathType: Prefix
        path: /static/rest_framework
        backend:
          service:
            name: sitevisor-backend-service
            port:
              number: 8000
  ingressClassName: nginx
" | kubectl apply -f -
```

**Access the application's backend API:**

Open your browser and go to http://sitevisor.local:8080/api/
