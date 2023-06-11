# DjangoBlog

🌍
*[English](/docs/README-en.md) ∙ [简体中文](README.md) ∙ [繁體中文](/docs/README-zh.md) *

基于 `python3.8` 和 `Django4.0` 的博客系统。

[![Django CI](https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml/badge.svg)](https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml) [![CodeQL](https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml) [![codecov](https://codecov.io/gh/liangliangyy/DjangoBlog/branch/master/graph/badge.svg)](https://codecov.io/gh/liangliangyy/DjangoBlog) [![license](https://img.shields.io/github/license/liangliangyy/djangoblog.svg)]()

## 主要功能：
- 文章、页面、分类目录、标签的添加、删除、编辑等功能。文章、评论及页面支持 `Markdown`，支持代码高亮。
- 支持文章全文搜索。
- 完整的评论功能，包括发表回复评论和评论的邮件提醒，支持 `Markdown`。
- 侧边栏功能：最新文章、最多阅读、标签云等。
- 支持 Oauth 登录，现已有 Google、GitHub、Facebook、微博、QQ 登录。
- 支持 `Redis` 缓存，并支持缓存自动刷新。
- 简单的 SEO 功能，新建文章等会自动通知 Google 和百度。
- 集成了简单的图床功能。
- 集成 `django-compressor`，自动压缩 `css`、`js`。
- 网站异常邮件提醒，若有未捕获到的异常会自动发送提醒邮件。
- 集成了微信公众号功能，现在可以使用微信公众号来管理你的 VPS 了。

## 安装
将 MySQL 客户端从 `pymysql` 修改为 `mysqlclient`，具体请参考 [pypi](https://pypi.org/project/mysqlclient/) 查看安装前的准备。

使用 pip 安装： `pip install -Ur requirements.txt`

如果你没有 pip，使用如下方式安装：
- OS X / Linux 电脑，终端下执行：

    ```
    curl http://peak.telecommunity.com/dist/ez_setup.py | python
    curl https://bootstrap.pypa.io/get-pip.py | python
    ```

- Windows 电脑：

    下载 http://peak.telecommunity.com/dist/ez_setup

.py 和 https://raw.github.com/pypa/pip/master/contrib/get-pip.py 这两个文件，双击运行。

## 运行

修改 `djangoblog/setting.py` 修改数据库配置，如下所示：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djang

oblog',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'host',
        'PORT': 3306,
    }
}
```

### 创建数据库
在 MySQL 数据库中执行：
```sql
CREATE DATABASE `djangoblog` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
```

然后在终端下执行：
```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户

在终端下执行：
```bash
python manage.py createsuperuser
```

### 创建测试数据
在终端下执行：
```bash
python manage.py create_testdata
```

### 收集静态文件
在终端下执行：
```bash
python manage.py collectstatic --noinput
python manage.py compress --force
```

### 开始运行：
执行： `python manage.py runserver`

在浏览器中打开：http://127.0.0.1:8000/，就可以看到博客效果了。

## 服务器部署

本地安装部署请参考 [DjangoBlog部署教程](https://www.lylinux.net/article/2019/8/5/58.html)，有详细的部署介绍。

本项目已经支持使用 Docker 来部署，如果你有 Docker 环境，那么可以使用 Docker 来部署，具体请参考：[docker部署](/docs/docker.md)

## 更多配置：
[更多配置介绍](/docs/config.md)  
[集成 Elasticsearch](/docs/es.md)

## 相关问题

如果你有任何问题，欢迎提出 Issue，或将问题描述发送到我的电子邮件 `liangliangyy#gmail.com`。我会尽快解答。推荐使用 Issue 方式。

---
## 致大家 🙋‍♀️🙋‍♂️
如果这个项目对你有所帮助，请在[这里](https://github.com/liangliangyy/DjangoBlog/issues/214)提交你的网址，让更多的人看到它。

你的回复将是我继续更新和维护这个项目的动力。

## 捐赠
如果你觉得这个项目对你有所帮助，欢迎你请我喝杯咖啡。你的支持是我最大的动力。你可以扫描下方二维码为我付款，谢谢。

### 支付宝：
<div>    
<img src="https://resource.lylinux.net/image/2017/12/16/IMG_0207.jpg" width="150" height="150" />
</div>  

### 微信：
<div>    
<img src="https://resource.lylinux.net/image/2017/12/16/IMG_0206.jpg" width="150" height="150" />
</div>

---

感谢 JetBrains
<div>    
<a href="https://www.jetbrains.com/?from=DjangoBlog"><img src="https://resource.lylinux.net/image/2020/07/01/logo.png" width="150" height="150"></a>
</div>