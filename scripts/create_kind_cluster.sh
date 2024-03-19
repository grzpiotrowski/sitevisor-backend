#!/bin/bash

# Exit script on error
set -e

# Create Kind cluster
if ! kind get clusters | grep -q '^kind$'; then
kind create cluster --config=- <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  ipFamily: dual
nodes:
- role: control-plane
  image: kindest/node:v1.29.2
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: 'ingress-ready=true'
  extraPortMappings:
  - containerPort: 80
    hostPort: 8080
    listenAddress: 127.0.0.1
    protocol: TCP
  - containerPort: 443
    hostPort: 8443
    listenAddress: 127.0.0.1
    protocol: TCP
EOF
else
  echo "Kind cluster 'kind' already exists"
fi
