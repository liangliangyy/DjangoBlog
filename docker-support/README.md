# Docker 支持

## 使用 docker-compose 快速搭建开发环境（MySQL / Memcached）

我们提供了 `dev-environment-setup.yml` 用于快速搭建开发环境。

```shell script
docker-compose -f ./docker-support/dev-environment-setup.yml up
```

运行这条命令后，可以快速搭建起以下环境：

- MySQL 5.7 - 端口 `3306`，用户名 `root`，密码 `djangoblog_123`，自动以 UTF8MB4 编码创建 `djangoblog` 数据库
- Memcached - 端口 `11211`

## 构建镜像

```shell script
docker build -f .\docker-support\Dockerfile -t <你的 Docker Hub 用户名>/django_blog:latest .
```

## 运行自定义指令（例如数据库迁移）

```shell script
docker run -it --rm <你的 Docker Hub 用户名>/django_blog:latest <指令>
```

例如：

```shell script
docker run -it --rm -e DJANGO_MYSQL_HOST=192.168.231.50 django_blog/django_blog:latest makemigrations
docker run -it --rm -e DJANGO_MYSQL_HOST=192.168.231.50 django_blog/django_blog:latest migrate
docker run -it --rm -e DJANGO_MYSQL_HOST=192.168.231.50 django_blog/django_blog:latest createsuperuser
```

## 环境变量清单

| 环境变量名称              | 默认值                                                                     | 备注                                                                                           |
|---------------------------|----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| DJANGO_DEBUG              | False                                                                      |                                                                                                |
| DJANGO_SECRET_KEY         | DJANGO_BLOG_CHANGE_ME                                                      | 请务必修改，建议[随机生成](https://www.random.org/passwords/?num=5&len=24&format=html&rnd=new) |
| DJANGO_MYSQL_DATABASE     | djangoblog                                                                 |                                                                                                |
| DJANGO_MYSQL_USER         | root                                                                       |                                                                                                |
| DJANGO_MYSQL_PASSWORD     | djangoblog_123                                                             |                                                                                                |
| DJANGO_MYSQL_HOST         | 127.0.0.1                                                                  |                                                                                                |
| DJANGO_MYSQL_PORT         | 3306                                                                       |                                                                                                |
| DJANGO_MEMCACHED_ENABLE   | True                                                                       |                                                                                                |
| DJANGO_MEMCACHED_LOCATION | 127.0.0.1:11211                                                            |                                                                                                |
| DJANGO_BAIDU_NOTIFY_URL   | http://data.zz.baidu.com/urls?site=https://www.example.org&token=CHANGE_ME | 请在[百度站长平台](https://ziyuan.baidu.com/linksubmit/index)获取接口地址                      |
| DJANGO_EMAIL_TLS          | False                                                                      |                                                                                                |
| DJANGO_EMAIL_SSL          | True                                                                       |                                                                                                |
| DJANGO_EMAIL_HOST         | smtp.example.org                                                           |                                                                                                |
| DJANGO_EMAIL_PORT         | 465                                                                        |                                                                                                |
| DJANGO_EMAIL_USER         | SMTP_USER_CHANGE_ME                                                        |                                                                                                |
| DJANGO_EMAIL_PASSWORD     | SMTP_PASSWORD_CHANGE_ME                                                    |                                                                                                |
| DJANGO_ADMIN_EMAIL        | admin@example.org                                                          |                                                                                                |
| DJANGO_WEROBOT_TOKEN      | DJANGO_BLOG_CHANGE_ME                                                      | 请使用自己的微信公众号通信令牌（Token）                                                        |