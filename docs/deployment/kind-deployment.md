# Deploying the SiteVisor Backend

## Prerequisites
- Running Kind cluster
- PostgreSQL database deployed
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


## Tips
For testing the Django backend, you can expose postgreSQL with:
```bash
kubectl port-forward svc/sitevisor-db-cluster-rw 5432:5432 -n postgres-operator
```

and then use `POSTGRES_HOST=localhost` in the `.env` file of Django backend. This removes the need to rebuild and load Docker container into Kind cluster while developing.

Then run the Django app with:

```bash
python manage.py runserver
```

### Tests

To run tests set the env variable `DJANGO_ENV='dev'`. This uses local SQLite database.
Then run:
```bash
python manage.py test -v 2
```