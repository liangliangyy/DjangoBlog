# 使用 Kubernetes 部署 DjangoBlog

本文档将指导您如何在 Kubernetes (K8s) 集群上部署 DjangoBlog 应用。我们提供了一套完整的 `.yaml` 配置文件，位于 `deploy/k8s` 目录下，用于部署一个包含 DjangoBlog 应用、Nginx、MySQL、Redis 和 Elasticsearch 的完整服务栈。

## 架构概览

本次部署采用的是微服务化的云原生架构：

- **核心组件**: 每个核心服务 (DjangoBlog, Nginx, MySQL, Redis, Elasticsearch) 都将作为独立的 `Deployment` 运行。
- **配置管理**: Nginx 的配置文件和 Django 应用的环境变量通过 `ConfigMap` 进行管理。**注意：敏感信息（如密码）建议使用 `Secret` 进行管理。**
- **服务发现**: 所有服务都通过 `ClusterIP` 类型的 `Service` 在集群内部暴露，并通过服务名相互通信。
- **外部访问**: 使用 `Ingress` 资源将外部的 HTTP 流量路由到 Nginx 服务，作为整个博客应用的统一入口。
- **数据持久化**: 采用基于节点本地路径的 `local-storage` 方案。这需要您在指定的 K8s 节点上手动创建存储目录，并通过 `PersistentVolume` (PV) 和 `PersistentVolumeClaim` (PVC) 进行静态绑定。

## 1. 环境准备

在开始之前，请确保您已具备以下环境：

- 一个正在运行的 Kubernetes 集群。
- `kubectl` 命令行工具已配置并能够连接到您的集群。
- 集群中已安装并配置好 [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/)。
- 对集群中的一个节点（默认为 `master`）拥有文件系统访问权限，用于创建本地存储目录。

## 2. 部署步骤

### 步骤 1: 创建命名空间

我们建议将 DjangoBlog 相关的所有资源都部署在一个独立的命名空间中，便于管理。

```bash
# 创建一个名为 djangoblog 的命名空间
kubectl create namespace djangoblog
```

### 步骤 2: 配置持久化存储

此方案使用本地持久卷 (Local Persistent Volume)。您需要在集群的一个节点上（在 `pv.yaml` 文件中默认为 `master` 节点）创建用于数据存储的目录。

```bash
# 登录到您的 master 节点
ssh user@master-node

# 创建所需的存储目录
sudo mkdir -p /mnt/local-storage-db
sudo mkdir -p /mnt/local-storage-djangoblog
sudo mkdir -p /mnt/resource/
sudo mkdir -p /mnt/local-storage-elasticsearch

# 退出节点
exit
```
**注意**: 如果您希望将数据存储在其他节点或使用不同的路径，请务必修改 `deploy/k8s/pv.yaml` 文件中 `nodeAffinity` 和 `local.path` 的配置。

创建目录后，应用存储相关的配置文件：

```bash
# 应用 StorageClass
kubectl apply -f deploy/k8s/storageclass.yaml

# 应用 PersistentVolume (PV)
kubectl apply -f deploy/k8s/pv.yaml

# 应用 PersistentVolumeClaim (PVC)
kubectl apply -f deploy/k8s/pvc.yaml
```

### 步骤 3: 配置应用

在部署应用之前，您需要编辑 `deploy/k8s/configmap.yaml` 文件，修改其中的敏感信息和个性化配置。

**强烈建议修改以下字段：**
- `DJANGO_SECRET_KEY`: 修改为一个随机且复杂的字符串。
- `DJANGO_MYSQL_PASSWORD` 和 `MYSQL_ROOT_PASSWORD`: 修改为您自己的数据库密码。

```bash
# 编辑 ConfigMap 文件
vim deploy/k8s/configmap.yaml

# 应用配置
kubectl apply -f deploy/k8s/configmap.yaml
```

### 步骤 4: 部署应用服务栈

现在，我们可以部署所有的核心服务了。

```bash
# 部署 Deployments (DjangoBlog, MySQL, Redis, Nginx, ES)
kubectl apply -f deploy/k8s/deployment.yaml

# 部署 Services (为 Deployments 创建内部访问端点)
kubectl apply -f deploy/k8s/service.yaml
```

部署需要一些时间，您可以运行以下命令检查所有 Pod 是否都已成功运行 (STATUS 为 `Running`)：

```bash
kubectl get pods -n djangoblog -w
```

### 步骤 5: 暴露应用到外部

最后，通过应用 `Ingress` 规则来将外部流量引导至我们的 Nginx 服务。

```bash
# 应用 Ingress 规则
kubectl apply -f deploy/k8s/gateway.yaml
```

部署完成后，您可以通过 Ingress Controller 的外部 IP 地址来访问您的博客。执行以下命令获取地址：

```bash
kubectl get ingress -n djangoblog
```

### 步骤 6: 首次运行的初始化操作

与 Docker 部署类似，首次运行时，您需要进入 DjangoBlog 应用的 Pod 来执行数据库初始化和创建管理员账户。

```bash
# 首先，获取 djangoblog pod 的名称
kubectl get pods -n djangoblog | grep djangoblog

# 进入其中一个 Pod (将 [pod-name] 替换为上一步获取到的名称)
kubectl exec -it [pod-name] -n djangoblog -- bash

# 在 Pod 内部执行以下命令:
# 创建超级管理员账户 (请按照提示操作)
python manage.py createsuperuser

# (可选) 创建测试数据
python manage.py create_testdata

# (可选，如果启用了 ES) 创建索引
python manage.py rebuild_index

# 退出 Pod
exit
```

至此，您已成功在 Kubernetes 集群上完成了 DjangoBlog 的部署！ 