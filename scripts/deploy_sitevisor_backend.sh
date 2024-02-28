#!/bin/bash

# Exit script on error
set -e

# Create Kind cluster
if ! kind get clusters | grep -q '^kind$'; then
  kind create cluster
else
  echo "Kind cluster 'kind' already exists"
fi

# Variables
NAMESPACE="postgres-operator"
OPERATOR_VERSION="1.22.1"
SUPERUSER_SECRET_NAME="postgres-superuser-secret"
APP_USER_SECRET_NAME="sitevisor-user-secret"
CLUSTER_NAME="sitevisor-db-cluster"
PG_IMAGE="ghcr.io/cloudnative-pg/postgresql:16.2"
DATABASE_NAME="sitevisordb"
DATABASE_OWNER="sitevisoruser"
SUPERUSER_USERNAME="postgresadmin"
SUPERUSER_PASSWORD="supersecret"
APP_USERNAME="sitevisoruser"
APP_PASSWORD="secret"

# Create Namespace for PostgreSQL Operator
echo "Creating namespace ${NAMESPACE}..."
kubectl create namespace ${NAMESPACE} || echo "Namespace ${NAMESPACE} already exists"

# Deploy the CNP Operator
echo "Deploying CNP Operator version ${OPERATOR_VERSION}..."
kubectl apply -n cnpg-system -f https://github.com/cloudnative-pg/cloudnative-pg/releases/download/v${OPERATOR_VERSION}/cnpg-${OPERATOR_VERSION}.yaml

# Create Secrets
echo "Creating secret for PostgreSQL superuser..."
kubectl create secret generic ${SUPERUSER_SECRET_NAME} \
  --from-literal=username=${SUPERUSER_USERNAME} \
  --from-literal=password=${SUPERUSER_PASSWORD} \
  --namespace ${NAMESPACE} || echo "Secret ${SUPERUSER_SECRET_NAME} already exists or error occurred"

echo "Creating secret for application database user..."
kubectl create secret generic ${APP_USER_SECRET_NAME} \
  --from-literal=username=${APP_USERNAME} \
  --from-literal=password=${APP_PASSWORD} \
  --namespace ${NAMESPACE} || echo "Secret ${APP_USER_SECRET_NAME} already exists or error occurred"

# Rreadiness check for the CNP operator
echo "Checking CNP operator readiness..."
EXPECTED_READY_REPLICAS=1
ACTUAL_READY_REPLICAS=$(kubectl get deployment -n cnpg-system -l 'app.kubernetes.io/name=cloudnative-pg' -o jsonpath="{.items[0].status.readyReplicas}")

while [ "$ACTUAL_READY_REPLICAS" != "$EXPECTED_READY_REPLICAS" ]; do
  echo "Waiting for CNP operator to become ready..."
  sleep 5
  ACTUAL_READY_REPLICAS=$(kubectl get deployment -n cnpg-system -l 'app.kubernetes.io/name=cloudnative-pg' -o jsonpath="{.items[0].status.readyReplicas}")
done

echo "CNP operator is ready."

# Deploy PostgreSQL Cluster
cat <<EOF | kubectl apply -f -
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: ${CLUSTER_NAME}
  namespace: ${NAMESPACE}
spec:
  instances: 1
  imageName: ${PG_IMAGE}
  storage:
    size: 1Gi
  bootstrap:
    initdb:
      database: ${DATABASE_NAME}
      owner: ${DATABASE_OWNER}
      secret:
        name: ${APP_USER_SECRET_NAME}
EOF

echo "PostgreSQL deployment process completed."

# Build and load Sitevisor Backend Docker image
docker build -t sitevisor-backend:dev .
kind load docker-image sitevisor-backend:dev

# Apply Kubernetes resources
kubectl apply -f - <<EOF
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
EOF

kubectl apply -f - <<EOF
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
EOF

# Wait for the pod to be ready
echo "Waiting for sitevisor-backend pod to be ready..."
READY=0
while [ $READY -eq 0 ]; do
    POD_STATUS=$(kubectl get pods -l app=sitevisor-backend -o jsonpath="{.items[0].status.phase}")
    if [ "$POD_STATUS" == "Running" ]; then
        READY=1
        echo "Pod is now ready."
    else
        echo "Waiting for pod to enter the Running state, current status: $POD_STATUS"
        sleep 5
    fi
done

# Port-forward
echo "Setting up port-forwarding to access the service..."
kubectl port-forward service/sitevisor-backend-service 4000:8000 &
echo "Application should be accessible at http://localhost:4000"
