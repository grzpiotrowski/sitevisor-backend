# PostgreSQL deployment

**Create a Namespace for the PostgreSQL Operator:**
```bash
kubectl create namespace postgres-operator
```

**Deploy the CNP Operator:**
```bash
kubectl apply -n cnpg-system -f https://github.com/cloudnative-pg/cloudnative-pg/releases/download/v1.22.1/cnpg-1.22.1.yaml
```

**Create a Secret for the PostgreSQL Superuser:**
```bash
kubectl create secret generic postgres-superuser-secret --from-literal=username=postgresadmin --from-literal=password=supersecret --namespace postgres-operator
```

**Create a Secret for the Application Database User:**
```bash
kubectl create secret generic sitevisor-user-secret  --from-literal=username=sitevisoruser --from-literal=password=secret --namespace postgres-operator
```

**Deploy a PostgreSQL Cluster:**
```bash
echo "
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: sitevisor-db-cluster
  namespace: postgres-operator
spec:
  instances: 1
  imageName: ghcr.io/cloudnative-pg/postgresql:16.2
  storage:
    size: 1Gi
  bootstrap:
    initdb:
      database: sitevisordb
      owner: sitevisoruser
      secret:
        name: sitevisor-user-secret
" | kubectl apply -f -
```