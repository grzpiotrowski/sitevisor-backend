# Creating Kind Cluster
kind is a tool for running local Kubernetes clusters using Docker.

**Create the Kind cluster:**
```bash
echo "
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
" | kind create cluster --config=-
```

**NGINX Ingress Controller:**

The manifests below contain kind specific patches to forward the hostPorts to the ingress controller:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```