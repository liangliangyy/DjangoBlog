# 搜索引擎配置说明

## 概述

DjangoBlog 支持两种搜索引擎：
- **Whoosh** - 纯 Python 实现，开箱即用（默认）
- **Elasticsearch** - 高性能分布式搜索引擎（推荐生产环境）

配置优先级：**环境变量 > 手动配置 > 默认 Whoosh**

## 快速开始

### 使用 Whoosh（默认）

无需配置，直接使用：

```bash
python manage.py rebuild_index
python manage.py runserver
```

索引存储在 `whoosh_index/` 目录。

### 使用 Elasticsearch（开发环境）

1. **启动 ES 服务：**
```bash
# Docker 方式
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.6.1

# 或直接运行 ES
./bin/elasticsearch
```

2. **编辑 `djangoblog/settings.py`：**

取消以下配置的注释：

```python
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://127.0.0.1:9200',
        'verify_certs': False,

        # 如果启用了安全特性，添加认证信息
        # 'username': 'elastic',
        # 'password': 'your_password',
    },
}
```

3. **重建索引：**
```bash
python manage.py rebuild_index
```

### 使用 Elasticsearch（生产环境）

通过环境变量配置，无需修改代码：

```bash
# 基本配置
export DJANGO_ELASTICSEARCH_HOST=https://es.example.com:9200
export ELASTICSEARCH_VERIFY_CERTS=True

# 用户名密码认证
export ELASTICSEARCH_USERNAME=elastic
export ELASTICSEARCH_PASSWORD=your_password

# 启动应用
python manage.py runserver
```

## 配置详解

### 开发环境手动配置

编辑 `djangoblog/settings.py`，在搜索引擎配置部分添加：

```python
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://127.0.0.1:9200',
        'verify_certs': False,

        # === 选择一种认证方式 ===

        # 方式1: 无认证（开发环境）
        # 不需要额外配置

        # 方式2: 用户名密码认证
        'username': 'elastic',
        'password': 'changeme',

        # 方式3: API Key 认证
        # 'api_key': 'your_api_key',

        # 方式4: 证书认证
        # 'ca_certs': '/path/to/ca.crt',
        # 'client_cert': '/path/to/client.crt',
        # 'client_key': '/path/to/client.key',
    },
}
```

### 生产环境环境变量

| 环境变量 | 说明 | 必需 | 示例 |
|---------|------|------|------|
| `DJANGO_ELASTICSEARCH_HOST` | ES 主机地址 | ✅ | `https://es.example.com:9200` |
| `ELASTICSEARCH_VERIFY_CERTS` | 验证 SSL 证书 | ❌ | `True` / `False` |
| `ELASTICSEARCH_USERNAME` | 用户名 | ❌ | `elastic` |
| `ELASTICSEARCH_PASSWORD` | 密码 | ❌ | `your_password` |
| `ELASTICSEARCH_API_KEY` | API Key | ❌ | `your_api_key` |
| `ELASTICSEARCH_CA_CERTS` | CA 证书路径 | ❌ | `/etc/ssl/certs/ca.crt` |
| `ELASTICSEARCH_CLIENT_CERT` | 客户端证书 | ❌ | `/etc/ssl/certs/client.crt` |
| `ELASTICSEARCH_CLIENT_KEY` | 客户端私钥 | ❌ | `/etc/ssl/private/client.key` |

### Docker Compose 示例

```yaml
version: '3.8'

services:
  web:
    build: .
    environment:
      - DJANGO_ELASTICSEARCH_HOST=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=${ES_PASSWORD}
    depends_on:
      - elasticsearch

  elasticsearch:
    image: elasticsearch:8.6.1
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=${ES_PASSWORD}
    ports:
      - "9200:9200"
```

### Kubernetes 示例

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: djangoblog-es-config
data:
  DJANGO_ELASTICSEARCH_HOST: "http://elasticsearch-service:9200"
  ELASTICSEARCH_VERIFY_CERTS: "false"

---
apiVersion: v1
kind: Secret
metadata:
  name: djangoblog-es-secret
type: Opaque
stringData:
  ELASTICSEARCH_USERNAME: elastic
  ELASTICSEARCH_PASSWORD: your_password_here

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: djangoblog
spec:
  template:
    spec:
      containers:
      - name: web
        envFrom:
        - configMapRef:
            name: djangoblog-es-config
        - secretRef:
            name: djangoblog-es-secret
```

## 切换搜索引擎

### 从 Whoosh 切换到 Elasticsearch

1. 配置 ES（见上文）
2. 重建索引：
```bash
python manage.py rebuild_index
```

### 从 Elasticsearch 切换回 Whoosh

1. 注释掉 `ELASTICSEARCH_DSL` 配置
2. 或删除 `DJANGO_ELASTICSEARCH_HOST` 环境变量
3. 重建索引：
```bash
python manage.py rebuild_index
```

## 维护命令

```bash
# 重建索引（清空后重建）
python manage.py rebuild_index

# 更新索引（增量更新）
python manage.py update_index

# 清空索引
python manage.py clear_index

# 仅针对 ES：手动构建索引
python manage.py build_index
```

## 性能对比

| 特性 | Whoosh | Elasticsearch |
|------|--------|--------------|
| 安装难度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 性能 | 中等（适合小型博客） | 极高（适合大规模） |
| 中文分词 | ✅ jieba | ✅ ik_analyzer |
| 分布式 | ❌ | ✅ |
| 实时性 | 一般 | 近实时 |
| 资源占用 | 低 | 较高 |

## 故障排查

### 问题：索引不更新

**解决：**
```bash
# 检查 Haystack 信号处理器
python manage.py shell
>>> from django.conf import settings
>>> print(settings.HAYSTACK_SIGNAL_PROCESSOR)

# 应该输出：haystack.signals.RealtimeSignalProcessor
```

### 问题：搜索无结果

**解决：**
```bash
# 重建索引
python manage.py rebuild_index --noinput

# 检查索引文档数量
python manage.py shell
>>> from haystack.query import SearchQuerySet
>>> print(SearchQuerySet().count())
```

### 问题：ES 连接失败

**解决：**
1. 确认 ES 正在运行：`curl http://localhost:9200`
2. 检查防火墙设置
3. 验证认证信息是否正确

## 更多信息

- [Elasticsearch 配置详解](./elasticsearch-config.md)
- [Haystack 官方文档](https://django-haystack.readthedocs.io/)
- [Whoosh 文档](https://whoosh.readthedocs.io/)
