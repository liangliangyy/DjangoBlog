# 使用 Docker 部署 DjangoBlog

![Docker Pulls](https://img.shields.io/docker/pulls/liangliangyy/djangoblog)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/liangliangyy/djangoblog?sort=date)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/liangliangyy/djangoblog)

本项目全面支持使用 Docker 进行容器化部署，为您提供了快速、一致且隔离的运行环境。我们推荐使用 `docker-compose` 来一键启动整个博客服务栈。

## 1. 环境准备

在开始之前，请确保您的系统中已经安装了以下软件：
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/) (对于 Docker Desktop 用户，它已内置)

## 2. 推荐方式：使用 `docker-compose` (一键部署)

这是最简单、最推荐的部署方式。它会自动为您创建并管理 Django 应用、MySQL 数据库，以及可选的 Elasticsearch 服务。

### 步骤 1: 启动基础服务

在项目根目录下，执行以下命令：

```bash
# 构建并以后台模式启动容器 (包含 Django 应用和 MySQL)
docker-compose up -d --build
```

`docker-compose` 会读取 `docker-compose.yml` 文件，自动拉取所需镜像、构建项目镜像，并启动所有服务。

- **访问您的博客**: 服务启动后，在浏览器中访问 `http://127.0.0.1` 即可看到博客首页。
- **数据持久化**: MySQL 的数据文件将存储在项目根目录下的 `data/mysql` 文件夹中，确保数据在容器重启后不丢失。

### 步骤 2: (可选) 启用 Elasticsearch 全文搜索

如果您希望使用 Elasticsearch 提供更强大的全文搜索功能，可以额外加载 `docker-compose.es.yml` 配置文件：

```bash
# 构建并以后台模式启动所有服务 (Django, MySQL, Elasticsearch)
docker-compose -f docker-compose.yml -f deploy/docker-compose/docker-compose.es.yml up -d --build
```
- **数据持久化**: Elasticsearch 的数据将存储在 `data/elasticsearch` 文件夹中。

### 步骤 3: 首次运行的初始化操作

当容器首次启动后，您需要进入容器来执行一些初始化命令。

```bash
# 进入 djangoblog 应用容器
docker-compose exec web bash

# 在容器内执行以下命令:
# 创建超级管理员账户 (请按照提示设置用户名、邮箱和密码)
python manage.py createsuperuser

# (可选) 创建一些测试数据
python manage.py create_testdata

# (可选，如果启用了 ES) 创建索引
python manage.py rebuild_index

# 退出容器
exit
```

## 3. 备选方式：使用独立的 Docker 镜像

如果您已经拥有一个正在运行的外部 MySQL 数据库，您也可以只运行 DjangoBlog 的应用镜像。

```bash
# 从 Docker Hub 拉取最新镜像
docker pull liangliangyy/djangoblog:latest

# 运行容器，并链接到您的外部数据库
docker run -d \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY='your-strong-secret-key' \
  -e DJANGO_MYSQL_HOST='your-mysql-host' \
  -e DJANGO_MYSQL_USER='your-mysql-user' \
  -e DJANGO_MYSQL_PASSWORD='your-mysql-password' \
  -e DJANGO_MYSQL_DATABASE='djangoblog' \
  --name djangoblog \
  liangliangyy/djangoblog:latest
```

- **访问您的博客**: 启动完成后，访问 `http://127.0.0.1:8000`。
- **创建管理员**: `docker exec -it djangoblog python manage.py createsuperuser`

## 4. 配置说明 (环境变量)

本项目的大部分配置都通过环境变量来管理。您可以在 `docker-compose.yml` 文件中修改它们，或者在使用 `docker run` 命令时通过 `-e` 参数传入。

| 环境变量名称            | 默认值/示例                                                              | 备注                                                                |
|-------------------------|--------------------------------------------------------------------------|---------------------------------------------------------------------|
| `DJANGO_SECRET_KEY`     | `your-strong-secret-key`                                                 | **请务必修改为一个随机且复杂的字符串！**                            |
| `DJANGO_DEBUG`          | `False`                                                                  | 是否开启 Django 的调试模式                                          |
| `DJANGO_MYSQL_HOST`     | `mysql`                                                                  | 数据库主机名                                                        |
| `DJANGO_MYSQL_PORT`     | `3306`                                                                   | 数据库端口                                                          |
| `DJANGO_MYSQL_DATABASE` | `djangoblog`                                                             | 数据库名称                                                          |
| `DJANGO_MYSQL_USER`     | `root`                                                                   | 数据库用户名                                                        |
| `DJANGO_MYSQL_PASSWORD` | `djangoblog_123`                                                         | 数据库密码                                                          |
| `DJANGO_REDIS_URL`      | `redis:6379/0`                                                           | Redis 连接地址 (用于缓存)                                           |
| `DJANGO_ELASTICSEARCH_HOST` | `elasticsearch:9200`                                                 | Elasticsearch 主机地址                                              |
| `DJANGO_EMAIL_HOST`     | `smtp.example.org`                                                       | 邮件服务器地址                                                      |
| `DJANGO_EMAIL_PORT`     | `465`                                                                    | 邮件服务器端口                                                      |
| `DJANGO_EMAIL_USER`     | `user@example.org`                                                       | 邮件账户                                                            |
| `DJANGO_EMAIL_PASSWORD` | `your-email-password`                                                    | 邮件密码                                                            |
| `DJANGO_EMAIL_USE_SSL`  | `True`                                                                   | 是否使用 SSL                                                        |
| `DJANGO_EMAIL_USE_TLS`  | `False`                                                                  | 是否使用 TLS                                                        |
| `DJANGO_ADMIN_EMAIL`    | `admin@example.org`                                                      | 接收异常报告的管理员邮箱                                            |
| `DJANGO_BAIDU_NOTIFY_URL` | `http://data.zz.baidu.com/...`                                         | [百度站长平台](https://ziyuan.baidu.com/linksubmit/index) 的推送接口 |

---

部署完成后，请务必检查并根据您的实际需求调整这些环境变量，特别是 `DJANGO_SECRET_KEY` 和数据库、邮件相关的配置。
