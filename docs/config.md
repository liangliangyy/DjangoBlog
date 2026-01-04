# 主要功能配置介绍

## 缓存配置

缓存默认使用 `localmem`（本地内存缓存）。如果你有 Redis 环境，可以通过设置 `DJANGO_REDIS_URL` 环境变量来自动切换到 Redis 缓存。

### 使用 Redis 缓存

设置环境变量：
```bash
export DJANGO_REDIS_URL="127.0.0.1:6379/0"
```

或者在 `settings.py` 中直接修改缓存配置：
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
    }
}
```

参考代码：https://github.com/liangliangyy/DjangoBlog/blob/master/djangoblog/settings.py#L201-L215


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


## Django 版本配置说明

### Django 4.0+ CSRF 配置

Django 4.0 及以上版本需要配置 `CSRF_TRUSTED_ORIGINS`，否则可能会在登录时报 CSRF 错误。

在 `settings.py` 中配置您的域名：
```python
CSRF_TRUSTED_ORIGINS = [
    'http://example.com',
    'https://example.com',
    'http://www.example.com',
    'https://www.example.com',
]
```

**注意**：请将 `example.com` 替换为您的实际域名，包括协议（http/https）。

参考代码：https://github.com/liangliangyy/DjangoBlog/blob/master/djangoblog/settings.py#L41

### Django 5.2 说明

本项目目前使用 Django 5.2.9，已经过充分测试，运行稳定。如果从旧版本升级，请注意：
- 确保 Python 版本 >= 3.10
- 运行数据库迁移：`python manage.py migrate`
- 更新依赖：`pip install -r requirements.txt`

## 前端开发配置

### 技术栈

- **Alpine.js 3.13**: 轻量级响应式框架
- **Tailwind CSS 3.4**: 实用优先的 CSS 框架
- **HTMX 2.0**: HTML-over-the-wire 架构
- **Vite 5.4**: 现代化构建工具

### 开发模式

在开发前端代码时，可以使用 Vite 的热更新功能：

```bash
cd frontend
npm run dev
```

这将启动 Vite 开发服务器（默认端口 5173），修改前端代码后会自动重新构建和刷新浏览器。

### 生产构建

```bash
cd frontend
npm run build
```

构建产物将输出到 `blog/static/blog/dist/` 目录，包括：
- CSS 文件（经过 Tailwind JIT 编译和压缩）
- JavaScript 文件（经过代码分割和压缩）
- Vite manifest 文件（用于资源映射）

### 深色模式

项目内置深色模式功能：

- **自动切换**: 支持跟随系统主题自动切换
- **持久化**: 用户选择会保存到 localStorage
- **防闪烁**: 页面加载时无白屏闪烁
- **快捷键**: 支持 `Ctrl+Shift+D` / `Cmd+Shift+D` 快速切换

用户可以通过页面右上角的按钮手动切换主题。

### 配色方案

支持 8 种配色主题，可在 `djangoblog/settings.py` 中配置：

```python
# 在模板中设置
COLOR_SCHEME = 'purple'  # purple, blue, green, orange, pink, red, indigo, teal
```

配色方案通过 CSS 变量系统实现，修改后无需重新构建前端资源。

