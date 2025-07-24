# Deploying DjangoBlog with Kubernetes

This document guides you through deploying the DjangoBlog application on a Kubernetes (K8s) cluster. We provide a complete set of `.yaml` configuration files in the `deploy/k8s` directory to deploy a full service stack, including the DjangoBlog application, Nginx, MySQL, Redis, and Elasticsearch.

## Architecture Overview

This deployment utilizes a microservices-based, cloud-native architecture:

- **Core Components**: Each core service (DjangoBlog, Nginx, MySQL, Redis, Elasticsearch) runs as a separate `Deployment`.
- **Configuration Management**: Nginx configurations and Django application environment variables are managed via `ConfigMap`. **Note: For sensitive information like passwords, using `Secret` is highly recommended.**
- **Service Discovery**: All services are exposed internally within the cluster as `ClusterIP` type `Service`, enabling communication via service names.
- **External Access**: An `Ingress` resource is used to route external HTTP traffic to the Nginx service, which acts as the single entry point for the entire blog application.
- **Data Persistence**: A `local-storage` solution based on node-local paths is used. This requires you to manually create storage directories on a specific K8s node and statically bind them using `PersistentVolume` (PV) and `PersistentVolumeClaim` (PVC).

## 1. Prerequisites

Before you begin, please ensure you have the following:

- A running Kubernetes cluster.
- The `kubectl` command-line tool configured to connect to your cluster.
- An [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/) installed and configured in your cluster.
- Filesystem access to one of the nodes in your cluster (defaulted to `master` in the configs) to create local storage directories.

## 2. Deployment Steps

### Step 1: Create a Namespace

We recommend deploying all DjangoBlog-related resources in a dedicated namespace for better management.

```bash
# Create a namespace named 'djangoblog'
kubectl create namespace djangoblog
```

### Step 2: Configure Persistent Storage

This setup uses Local Persistent Volumes. You need to create the data storage directories on a node within your cluster (the default is the `master` node in `pv.yaml`).

```bash
# Log in to your master node
ssh user@master-node

# Create the required storage directories
sudo mkdir -p /mnt/local-storage-db
sudo mkdir -p /mnt/local-storage-djangoblog
sudo mkdir -p /mnt/resource/
sudo mkdir -p /mnt/local-storage-elasticsearch

# Log out from the node
exit
```
**Note**: If you wish to store data on a different node or use different paths, you must modify the `nodeAffinity` and `local.path` settings in the `deploy/k8s/pv.yaml` file.

After creating the directories, apply the storage-related configurations:

```bash
# Apply the StorageClass
kubectl apply -f deploy/k8s/storageclass.yaml

# Apply the PersistentVolumes (PVs)
kubectl apply -f deploy/k8s/pv.yaml

# Apply the PersistentVolumeClaims (PVCs)
kubectl apply -f deploy/k8s/pvc.yaml
```

### Step 3: Configure the Application

Before deploying the application, you need to edit the `deploy/k8s/configmap.yaml` file to modify sensitive information and custom settings.

**It is strongly recommended to change the following fields:**
- `DJANGO_SECRET_KEY`: Change to a random, complex string.
- `DJANGO_MYSQL_PASSWORD` and `MYSQL_ROOT_PASSWORD`: Change to your own secure database password.

```bash
# Edit the ConfigMap file
vim deploy/k8s/configmap.yaml

# Apply the configuration
kubectl apply -f deploy/k8s/configmap.yaml
```

### Step 4: Deploy the Application Stack

Now, we can deploy all the core services.

```bash
# Deploy the Deployments (DjangoBlog, MySQL, Redis, Nginx, ES)
kubectl apply -f deploy/k8s/deployment.yaml

# Deploy the Services (to create internal endpoints for the Deployments)
kubectl apply -f deploy/k8s/service.yaml
```

The deployment may take some time. You can run the following command to check if all Pods are running successfully (STATUS should be `Running`):

```bash
kubectl get pods -n djangoblog -w
```

### Step 5: Expose the Application Externally

Finally, expose the Nginx service to external traffic by applying the `Ingress` rule.

```bash
# Apply the Ingress rule
kubectl apply -f deploy/k8s/gateway.yaml
```

Once deployed, you can access your blog via the external IP address of your Ingress Controller. Use the following command to find the address:

```bash
kubectl get ingress -n djangoblog
```

### Step 6: First-Time Initialization

Similar to the Docker deployment, you need to get a shell into the DjangoBlog application Pod to perform database initialization and create a superuser on the first run.

```bash
# First, get the name of a djangoblog pod
kubectl get pods -n djangoblog | grep djangoblog

# Exec into one of the Pods (replace [pod-name] with the name from the previous step)
kubectl exec -it [pod-name] -n djangoblog -- bash

# Inside the Pod, run the following commands:
# Create a superuser account (follow the prompts)
python manage.py createsuperuser

# (Optional) Create some test data
python manage.py create_testdata

# (Optional, if ES is enabled) Create the search index
python manage.py rebuild_index

# Exit the Pod
exit
```

Congratulations! You have successfully deployed DjangoBlog on your Kubernetes cluster. 