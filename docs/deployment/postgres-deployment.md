# PostgreSQL deployment

This section provides steps required to deploy the CloudNativePG operator which manages PostgreSQL workloads on Kubernetes cluster.

## Prerequisites
- Running Kind cluster

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

## Inspecting the database

Create a new Pod which will act as a debug access point:
```bash
echo "
apiVersion: v1
kind: Pod
metadata:
  name: postgres-debug-pod
  namespace: postgres-operator
spec:
  containers:
  - name: debug-container
    image: postgres:16.2
    command: ['sleep', 'infinity']
  restartPolicy: Always
" | kubectl apply -f -
```

Check if the Pod is ready:
```bash
kubectl get pod/postgres-debug-pod -n postgres-operator
```

Access the container:
```bash
kubectl exec -it postgres-debug-pod -n postgres-operator -- /bin/bash
```

Connect to PostgreSQL database with `psql`. Use the password set when deploying PostgreSQL cluster.
```bash
psql -U sitevisoruser -d sitevisordb -h sitevisor-db-cluster-rw.postgres-operator
```

Inspect the database:
```bash
\dt
```

This should give you a list of tables:
```
                         List of relations
 Schema |               Name               | Type  |     Owner
--------+----------------------------------+-------+---------------
 public | auth_group                       | table | sitevisoruser
 public | auth_group_permissions           | table | sitevisoruser
 public | auth_permission                  | table | sitevisoruser
 public | auth_user                        | table | sitevisoruser
 public | auth_user_groups                 | table | sitevisoruser
 public | auth_user_user_permissions       | table | sitevisoruser
 public | authtoken_token                  | table | sitevisoruser
 public | django_admin_log                 | table | sitevisoruser
 public | django_content_type              | table | sitevisoruser
 public | django_migrations                | table | sitevisoruser
 public | django_session                   | table | sitevisoruser
 public | sitevisorapi_point               | table | sitevisoruser
 public | sitevisorapi_project             | table | sitevisoruser
 public | sitevisorapi_room                | table | sitevisoruser
 public | sitevisorapi_sensor              | table | sitevisoruser
 public | sitevisorapi_sensortype          | table | sitevisoruser
 public | token_blacklist_blacklistedtoken | table | sitevisoruser
 public | token_blacklist_outstandingtoken | table | sitevisoruser
```

Inspect a table with:
```
TABLE sitevisorapi_room;
```

`exit` from the pod and delete it when no longer needed:
```bash
kubectl delete pod/postgres-debug-pod -n postgres-operator
```