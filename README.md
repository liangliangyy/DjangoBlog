# DjangoBlog

🌍
*[English](/docs/README-en.md) ∙ [简体中文](README.md)*

基于`python3.8`和`Django3.0`的博客。   

[![Build Status](https://travis-ci.org/liangliangyy/DjangoBlog.svg?branch=master)](https://travis-ci.org/liangliangyy/DjangoBlog) [![codecov](https://codecov.io/gh/liangliangyy/DjangoBlog/branch/master/graph/badge.svg)](https://codecov.io/gh/liangliangyy/DjangoBlog) [![Requirements Status](https://requires.io/github/liangliangyy/DjangoBlog/requirements.svg?branch=master)](https://requires.io/github/liangliangyy/DjangoBlog/requirements/?branch=master)  [![license](https://img.shields.io/github/license/liangliangyy/djangoblog.svg)]()  

## 主要功能：
- 文章，页面，分类目录，标签的添加，删除，编辑等。文章及页面支持`Markdown`，支持代码高亮。
- 支持文章全文搜索。
- 完整的评论功能，包括发表回复评论，以及评论的邮件提醒，支持`Markdown`。
- 侧边栏功能，最新文章，最多阅读，标签云等。
- 支持Oauth登陆，现已有Google,GitHub,facebook,微博,QQ登录。
- 支持`Memcache`缓存，支持缓存自动刷新。
- 简单的SEO功能，新建文章等会自动通知Google和百度。
- 集成了简单的图床功能。
- 集成`django-compressor`，自动压缩`css`，`js`。
- 网站异常邮件提醒，若有未捕捉到的异常会自动发送提醒邮件。
- 集成了微信公众号功能，现在可以使用微信公众号来管理你的vps了。

## 安装
mysql客户端从`pymysql`修改成了`mysqlclient`，具体请参考 [pypi](https://pypi.org/project/mysqlclient/) 查看安装前的准备。

使用pip安装： `pip install -Ur requirements.txt`

如果你没有pip，使用如下方式安装：
- OS X / Linux 电脑，终端下执行: 

    ```
    curl http://peak.telecommunity.com/dist/ez_setup.py | python
    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
    ```

- Windows电脑：

    下载 http://peak.telecommunity.com/dist/ez_setup.py 和 https://raw.github.com/pypa/pip/master/contrib/get-pip.py 这两个文件，双击运行。 

### 配置
配置都是在 `setting.py` 中，部分配置迁移到了后台配置中。

很多 `setting` 配置我都是写在环境变量里面的.并没有提交到 `github` 中来.例如`SECRET_KEY`,`OAHUTH`,`mysql`以及邮件部分的配置等.你可以直接修改代码成你自己的,或者在环境变量里面加入对应的配置就可以了.

`test`目录中的文件都是为了`travis`自动化测试使用的.不用去关注.或者直接使用.这样就可以集成`travis`自动化测试了.

`bin`目录是在`linux`环境中使用`Nginx`+`Gunicorn`+`virtualenv`+`supervisor`来部署的脚本和`Nginx`配置文件.可以参考我的文章:

>[DjangoBlog部署教程](https://www.lylinux.net/article/2019/8/5/58.html)

有详细的部署介绍.


## 运行

 修改`DjangoBlog/setting.py` 修改数据库配置，如下所示：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangoblog',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'host',
        'PORT': 3306,
    }
}
```

### 创建数据库
mysql数据库中执行:
```sql
CREATE DATABASE `djangoblog` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
```

然后终端下执行:
```bash
./manage.py makemigrations
./manage.py migrate
```

**注意：** 在使用 `./manage.py` 之前需要确定你系统中的 `python` 命令是指向 `python 3.6` 及以上版本的。如果不是如此，请使用以下两种方式中的一种：

- 修改 `manage.py` 第一行 `#!/usr/bin/env python` 为 `#!/usr/bin/env python3`
- 直接使用 `python3 ./manage.py makemigrations`

### 创建超级用户

 终端下执行:
```bash
./manage.py createsuperuser
```

### 创建测试数据
终端下执行:
```bash
./manage.py create_testdata
```

### 收集静态文件
终端下执行:  
```bash
./manage.py collectstatic --noinput
./manage.py compress --force
```

### 开始运行：
执行： `./manage.py runserver`


浏览器打开: http://127.0.0.1:8000/  就可以看到效果了。
## 更多配置:
[更多配置介绍](/docs/config.md)
[集成elasticsearch](/docs/es.md)

## 问题相关

有任何问题欢迎提Issue,或者将问题描述发送至我邮箱 `liangliangyy#gmail.com`.我会尽快解答.推荐提交Issue方式.  

---
 ## 致大家🙋‍♀️🙋‍♂️
 如果本项目帮助到了你，请在[这里](https://github.com/liangliangyy/DjangoBlog/issues/214)留下你的网址，让更多的人看到。
您的回复将会是我继续更新维护下去的动力。 

## 捐赠
如果您觉得本项目对您有所帮助，欢迎您请我喝杯咖啡，您的支持是我最大的动力，您可以扫描下方二维码为我付款，谢谢。
### 支付宝：
<div>    
<img src="https://resource.lylinux.net/image/2017/12/16/IMG_0207.jpg" width="150" height="150" />
</div>  

### 微信：
<div>    
<img src="https://resource.lylinux.net/image/2017/12/16/IMG_0206.jpg" width="150" height="150" />
</div>


🙏🙏🙏
