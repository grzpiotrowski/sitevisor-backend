#!/bin/bash

# Exit script on error
set -e

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
      containers:
      - name: sitevisor-backend
        image: sitevisor-backend:dev
        ports:
        - containerPort: 8000
EOF