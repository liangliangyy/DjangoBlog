# 使用docker部署
![Docker Pulls](https://img.shields.io/docker/pulls/liangliangyy/djangoblog)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/liangliangyy/djangoblog?sort=date)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/liangliangyy/djangoblog)

使用docker部署支持如下两种方式：
## docker镜像方式
本项目已经支持了docker部署，如果你已经有了`mysql`，那么直接使用基础镜像即可，启动命令如下所示：
```shell
docker pull liangliangyy/djangoblog:latest
docker run -d  -p 8000:8000 -e DJANGO_MYSQL_HOST=mysqlhost -e DJANGO_MYSQL_PASSWORD=mysqlrootpassword -e DJANGO_MYSQL_USER=root -e DJANGO_MYSQL_DATABASE=djangoblog --name djangoblog liangliangyy/djangoblog:latest
```
启动完成后，访问 http://127.0.0.1:8000 
## 使用docker-compose
如果你没有mysql等基础服务，那么可以使用`docker-compose`来运行，
具体命令如下所示:
```shell
docker-compose build
docker-compose up -d
```
本方式生成的mysql数据文件在 `bin/datas/mysql` 文件夹。  
等启动完成后，访问 [http://127.0.0.1](http://127.0.0.1) 即可。
### 使用es
如果你期望使用es来作为后端的搜索引擎，那么可以使用如下命令来启动：
```shell
docker-compose -f docker-compose.yml -f docker-compose.es.yml build
docker-compose -f docker-compose.yml -f docker-compose.es.yml up -d
```
本方式生成的es数据文件在 `bin/datas/es` 文件夹。
## 配置说明:

本项目较多配置都基于环境变量，所有的环境变量如下所示:

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
| DJANGO_WEROBOT_TOKEN      | DJANGO_BLOG_CHANGE_ME  
|DJANGO_ELASTICSEARCH_HOST|

第一次启动之后，使用如下命令来创建超级用户:
```shell
docker exec -it djangoblog python /code/djangoblog/manage.py createsuperuser
```
