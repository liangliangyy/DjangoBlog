# 主要功能配置介绍:

## 缓存：
缓存默认使用`localmem`缓存，如果你有`redis`环境，可以设置`DJANGO_REDIS_URL`环境变量，则会自动使用该redis来作为缓存，或者你也可以直接修改如下代码来使用。
https://github.com/liangliangyy/DjangoBlog/blob/ffcb2c3711de805f2067dd3c1c57449cd24d84ee/djangoblog/settings.py#L185-L199


## oauth登录:

现在已经支持QQ，微博，Google，GitHub，Facebook登录，需要在其对应的开放平台申请oauth登录权限，然后在  
**后台->Oauth** 配置中新增配置，填写对应的`appkey`和`appsecret`以及回调地址。  
### 回调地址示例：
qq：http://你的域名/oauth/authorize?type=qq  
微博：http://你的域名/oauth/authorize?type=weibo  
type对应在`oauthmanager`中的type字段。

## owntracks：
owntracks是一个位置追踪软件，可以定时的将你的坐标提交到你的服务器上，现在简单的支持owntracks功能，需要安装owntracks的app，然后将api地址设置为:
`你的域名/owntracks/logtracks`就可以了。然后访问`你的域名/owntracks/show_dates`就可以看到有经纬度记录的日期，点击之后就可以看到运动轨迹了。地图是使用高德地图绘制。

## 邮件功能：
同样，将`settings.py`中的`ADMINS = [('liangliang', 'liangliangyy@gmail.com')]`配置为你自己的错误接收邮箱，另外修改:
```python
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = os.environ.get('DJANGO_EMAIL_USER')
```
为你自己的邮箱配置。

## 微信公众号
集成了简单的微信公众号功能，在微信后台将token地址设置为:`你的域名/robot` 即可，默认token为`lylinux`，当然你可以修改为你自己的，在`servermanager/robot.py`中。
然后在**后台->Servermanager->命令**中新增命令，这样就可以使用微信公众号来管理了。  
## 网站配置介绍  
在**后台->BLOG->网站配置**中,可以新增网站配置，比如关键字，描述等，以及谷歌广告，网站统计代码及备案号等等。  
其中的*静态文件保存地址*是保存oauth用户登录的头像路径，填写绝对路径，默认是代码目录。
## 代码高亮
如果你发现你文章的代码没有高亮，请这样书写代码块:  

![](https://resource.lylinux.net/image/codelang.png)  


也就是说，需要在代码块开始位置加入这段代码对应的语言。

## update
如果你发现执行数据库迁移的时候出现如下报错：
```python
django.db.migrations.exceptions.MigrationSchemaMissing: Unable to create the django_migrations table ((1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '(6) NOT NULL)' at line 1"))
```
可能是因为你的mysql版本低于5.6，需要升级mysql版本>=5.6即可。


django 4.0登录可能会报错CSRF，需要配置下`settings.py`中的`CSRF_TRUSTED_ORIGINS`

https://github.com/liangliangyy/DjangoBlog/blob/master/djangoblog/settings.py#L39

