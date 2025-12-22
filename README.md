# DjangoBlog

<p align="center">
  <a href="https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml"><img src="https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml/badge.svg" alt="Django CI"></a>
  <a href="https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml"><img src="https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml/badge.svg" alt="CodeQL"></a>
  <a href="https://codecov.io/gh/liangliangyy/DjangoBlog"><img src="https://codecov.io/gh/liangliangyy/DjangoBlog/branch/master/graph/badge.svg" alt="codecov"></a>
  <a href="https://github.com/liangliangyy/DjangoBlog/blob/master/LICENSE"><img src="https://img.shields.io/github/license/liangliangyy/djangoblog.svg" alt="license"></a>
</p>

<p align="center">
  <b>一款功能强大、设计优雅的现代化博客系统</b>
  <br>
  <a href="/docs/README-en.md">English</a> • <b>简体中文</b>
</p>

---

DjangoBlog 是一款基于 Python 3.10+ 和 Django 5.2 构建的高性能博客平台。它不仅提供了传统博客的所有核心功能，还通过一个灵活的插件系统，让您可以轻松扩展和定制您的网站。无论您是个人博主、技术爱好者还是内容创作者，DjangoBlog 都旨在为您提供一个稳定、高效且易于维护的写作和发布环境。

## ✨ 特性亮点

- **强大的内容管理**: 支持文章、独立页面、分类和标签的完整管理。内置强大的 Markdown 编辑器，支持代码语法高亮。
- **全文搜索**: 集成搜索引擎，提供快速、精准的文章内容搜索。
- **互动评论系统**: 支持回复、邮件提醒等功能，评论内容同样支持 Markdown。
- **灵活的侧边栏**: 可自定义展示最新文章、最多阅读、标签云等模块。
- **社交化登录**: 内置 OAuth 支持，已集成 Google, GitHub, Facebook, 微博, QQ 等主流平台。
- **黑夜模式**: 支持浅色/深色主题自动切换，可跟随系统设置，提供舒适的阅读体验。
- **高性能缓存**: 原生支持 Redis 缓存，并提供自动刷新机制，确保网站高速响应。
- **SEO 友好**: 具备基础 SEO 功能，新内容发布后可自动通知 Google 和百度。
- **便捷的插件系统**: 通过创建独立的插件来扩展博客功能，代码解耦，易于维护。已内置 8 个实用插件，包括浏览计数、SEO 优化、文章推荐、图片懒加载等功能！
- **集成图床**: 内置简单的图床功能，方便图片上传和管理。
- **自动化前端**: 集成 `django-compressor`，自动压缩和优化 CSS 及 JavaScript 文件。
- **健壮的运维**: 内置网站异常邮件提醒和微信公众号管理功能。

## 🛠️ 技术栈

- **后端**: Python 3.10+, Django 5.2
- **数据库**: MySQL, SQLite (可配置)
- **缓存**: Redis, LocalMem (可配置)
- **前端**: HTML5, CSS3, JavaScript
- **搜索**: Whoosh, Elasticsearch (可配置)
- **编辑器**: Markdown (mdeditor)

## 🚀 快速开始

### 1. 环境准备

确保您的系统中已安装 Python 3.10+ 和 MySQL/MariaDB。

### 2. 克隆与安装

```bash
# 克隆项目到本地
git clone https://github.com/liangliangyy/DjangoBlog.git
cd DjangoBlog

# 安装依赖
pip install -r requirements.txt
```

### 3. 项目配置

- **数据库**:
  打开 `djangoblog/settings.py` 文件，找到 `DATABASES` 配置项，修改为您的 MySQL 连接信息。

  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'djangoblog',
          'USER': 'root',
          'PASSWORD': 'your_password',
          'HOST': '127.0.0.1',
          'PORT': 3306,
      }
  }
  ```
  在 MySQL 中创建数据库:
  ```sql
  CREATE DATABASE `djangoblog` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

- **更多配置**:
  关于邮件发送、OAuth 登录、缓存等更多高级配置，请参阅我们的 [详细配置文档](/docs/config.md)。

### 4. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate

# 创建一个超级管理员账户
python manage.py createsuperuser
```

### 5. 运行项目

```bash
# (可选) 生成一些测试数据
python manage.py create_testdata

# (可选) 收集和压缩静态文件
python manage.py collectstatic --noinput
python manage.py compress --force

# 启动开发服务器
python manage.py runserver
```

现在，在您的浏览器中访问 `http://127.0.0.1:8000/`，您应该能看到 DjangoBlog 的首页了！

## 部署

- **传统部署**: 我们为您准备了非常详细的 [服务器部署教程](https://www.lylinux.net/article/2019/8/5/58.html)。
- **Docker 部署**: 项目已全面支持 Docker。如果您熟悉容器化技术，请参考 [Docker 部署文档](/docs/docker.md) 来快速启动。
- **Kubernetes 部署**: 我们也提供了完整的 [Kubernetes 部署指南](/docs/k8s.md)，助您轻松上云。

## 🧩 插件系统

插件系统是 DjangoBlog 的核心特色之一。它允许您在不修改核心代码的情况下，通过编写独立的插件来为您的博客添加新功能。

- **工作原理**: 插件通过在预定义的"钩子"上注册回调函数来工作。例如，当一篇文章被渲染时，`after_article_body_get` 钩子会被触发，所有注册到此钩子的函数都会被执行。

- **现有插件**: 项目已内置以下实用插件
  - `view_count` - 文章浏览计数统计
  - `seo_optimizer` - SEO 优化增强
  - `article_copyright` - 文章版权声明
  - `article_recommendation` - 智能文章推荐
  - `external_links` - 外部链接处理
  - `image_lazy_loading` - 图片懒加载优化
  - `reading_time` - 文章阅读时间估算
  - `dark_mode` - 黑夜模式主题切换

- **开发您自己的插件**: 只需在 `plugins` 目录下创建一个新的文件夹，并编写您的 `plugin.py`。欢迎探索并为 DjangoBlog 社区贡献您的创意！

## 🤝 贡献指南

我们热烈欢迎任何形式的贡献！如果您有好的想法或发现了 Bug，请随时提交 Issue 或 Pull Request。

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## ❤️ 支持与赞助

如果您觉得这个项目对您有帮助，并且希望支持我继续维护和开发新功能，欢迎请我喝杯咖啡！您的每一份支持都是我前进的最大动力。

<p align="center">
  <img src="/docs/imgs/alipay.jpg" width="150" alt="支付宝赞助">
  <img src="/docs/imgs/wechat.jpg" width="150" alt="微信赞助">
</p>
<p align="center">
  <i>(左) 支付宝 / (右) 微信</i>
</p>

## 🙏 鸣谢

特别感谢 **JetBrains** 为本项目提供的免费开源许可证。

<p align="center">
  <a href="https://www.jetbrains.com/?from=DjangoBlog">
    <img src="/docs/imgs/pycharm_logo.png" width="150" alt="JetBrains Logo">
  </a>
</p>

---
> 如果本项目帮助到了你，请在[这里](https://github.com/liangliangyy/DjangoBlog/issues/214)留下你的网址，让更多的人看到。您的回复将会是我继续更新维护下去的动力。
