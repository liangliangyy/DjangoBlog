# DjangoBlog

<p align="center">
  <a href="https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml"><img src="https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml/badge.svg" alt="Django CI"></a>
  <a href="https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml"><img src="https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml/badge.svg" alt="CodeQL"></a>
  <a href="https://codecov.io/gh/liangliangyy/DjangoBlog"><img src="https://codecov.io/gh/liangliangyy/DjangoBlog/branch/master/graph/badge.svg" alt="codecov"></a>
  <a href="https://github.com/liangliangyy/DjangoBlog/blob/master/LICENSE"><img src="https://img.shields.io/github/license/liangliangyy/djangoblog.svg" alt="license"></a>
</p>

<p align="center">
  <b>A powerful, elegant, and modern blog system.</b>
  <br>
  <b>English</b> • <a href="/README.md">简体中文</a>
</p>

---

DjangoBlog is a high-performance blog platform built with Python 3.10 and Django 4.0. It not only provides all the core functionalities of a traditional blog but also features a flexible plugin system, allowing you to easily extend and customize your website. Whether you are a personal blogger, a tech enthusiast, or a content creator, DjangoBlog aims to provide a stable, efficient, and easy-to-maintain environment for writing and publishing.

## ✨ Features

- **Powerful Content Management**: Full support for managing articles, standalone pages, categories, and tags. Comes with a powerful built-in Markdown editor with syntax highlighting.
- **Full-Text Search**: Integrated search engine for fast and accurate content searching.
- **Interactive Comment System**: Supports replies, email notifications, and Markdown formatting in comments.
- **Flexible Sidebar**: Customizable modules for displaying recent articles, most viewed posts, tag cloud, and more.
- **Social Login**: Built-in OAuth support, with integrations for Google, GitHub, Facebook, Weibo, QQ, and other major platforms.
- **High-Performance Caching**: Native support for Redis caching with an automatic refresh mechanism to ensure high-speed website responses.
- **SEO Friendly**: Basic SEO features are included, with automatic notifications to Google and Baidu upon new content publication.
- **Extensible Plugin System**: Extend blog functionalities by creating standalone plugins, ensuring decoupled and maintainable code. We have already implemented features like view counting and SEO optimization through plugins!
- **Integrated Image Hosting**: A simple, built-in image hosting feature for easy uploads and management.
- **Automated Frontend**: Integrated with `django-compressor` to automatically compress and optimize CSS and JavaScript files.
- **Robust Operations**: Built-in email notifications for website exceptions and management capabilities through a WeChat Official Account.

## 🛠️ Tech Stack

- **Backend**: Python 3.10, Django 4.0
- **Database**: MySQL, SQLite (configurable)
- **Cache**: Redis
- **Frontend**: HTML5, CSS3, JavaScript
- **Search**: Whoosh, Elasticsearch (configurable)
- **Editor**: Markdown (mdeditor)

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have Python 3.10+ and MySQL/MariaDB installed on your system.

### 2. Clone & Installation

```bash
# Clone the project to your local machine
git clone https://github.com/liangliangyy/DjangoBlog.git
cd DjangoBlog

# Install dependencies
pip install -r requirements.txt
```

### 3. Project Configuration

- **Database**:
  Open `djangoblog/settings.py`, locate the `DATABASES` section, and update it with your MySQL connection details.

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
  Create the database in MySQL:
  ```sql
  CREATE DATABASE `djangoblog` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

- **More Configurations**:
  For advanced settings such as email, OAuth, caching, and more, please refer to our [Detailed Configuration Guide](/docs/config-en.md).

### 4. Database Initialization

```bash
python manage.py makemigrations
python manage.py migrate

# Create a superuser account
python manage.py createsuperuser
```

### 5. Running the Project

```bash
# (Optional) Generate some test data
python manage.py create_testdata

# (Optional) Collect and compress static files
python manage.py collectstatic --noinput
python manage.py compress --force

# Start the development server
python manage.py runserver
```

Now, open your browser and navigate to `http://127.0.0.1:8000/`. You should see the DjangoBlog homepage!

## Deployment

- **Traditional Deployment**: A detailed guide for server deployment is available here: [Deployment Tutorial](https://www.lylinux.net/article/2019/8/5/58.html) (in Chinese).
- **Docker Deployment**: This project fully supports Docker. If you are familiar with containerization, please refer to the [Docker Deployment Guide](/docs/docker-en.md) for a quick start.
- **Kubernetes Deployment**: We also provide a complete [Kubernetes Deployment Guide](/docs/k8s-en.md) to help you go cloud-native easily.

## 🧩 Plugin System

The plugin system is a core feature of DjangoBlog. It allows you to add new functionalities to your blog without modifying the core codebase by writing standalone plugins.

- **How it Works**: Plugins operate by registering callback functions to predefined "hooks". For instance, when an article is rendered, the `after_article_body_get` hook is triggered, and all functions registered to this hook are executed.
- **Existing Plugins**: Features like `view_count` and `seo_optimizer` are implemented through this plugin system.
- **Develop Your Own Plugin**: Simply create a new folder under the `plugins` directory and write your `plugin.py`. We welcome you to explore and contribute your creative ideas to the DjangoBlog community!

## 🤝 Contributing

We warmly welcome contributions of any kind! If you have great ideas or have found a bug, please feel free to open an issue or submit a pull request.

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).

---

## ❤️ Support & Sponsorship

If you find this project helpful and wish to support its continued maintenance and development, please consider buying me a coffee! Your support is my greatest motivation.

<p align="center">
  <img src="/docs/imgs/alipay.jpg" width="150" alt="Alipay Sponsorship">
  <img src="/docs/imgs/wechat.jpg" width="150" alt="WeChat Sponsorship">
</p>
<p align="center">
  <i>(Left) Alipay / (Right) WeChat</i>
</p>

## 🙏 Acknowledgements

A special thanks to **JetBrains** for providing a free open-source license for this project.

<p align="center">
  <a href="https://www.jetbrains.com/?from=DjangoBlog">
    <img src="/docs/imgs/pycharm_logo.png" width="150" alt="JetBrains Logo">
  </a>
</p>

---
> If this project has helped you, please leave your website URL [here](https://github.com/liangliangyy/DjangoBlog/issues/214) to let more people see it. Your feedback is the driving force for my continued updates and maintenance.
