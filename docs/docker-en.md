# Deploying DjangoBlog with Docker

![Docker Pulls](https://img.shields.io/docker/pulls/liangliangyy/djangoblog)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/liangliangyy/djangoblog?sort=date)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/liangliangyy/djangoblog)

This project fully supports containerized deployment using Docker, providing you with a fast, consistent, and isolated runtime environment. We recommend using `docker-compose` to launch the entire blog service stack with a single command.

## 1. Prerequisites

Before you begin, please ensure you have the following software installed on your system:
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/) (Included with Docker Desktop for Mac and Windows)

## 2. Recommended Method: Using `docker-compose` (One-Click Deployment)

This is the simplest and most recommended way to deploy. It automatically creates and manages the Django application, a MySQL database, and an optional Elasticsearch service for you.

### Step 1: Start the Basic Services

From the project's root directory, run the following command:

```bash
# Build and start the containers in detached mode (includes Django app and MySQL)
docker-compose up -d --build
```

`docker-compose` will read the `docker-compose.yml` file, pull the necessary images, build the project image, and start all services.

- **Access Your Blog**: Once the services are up, you can access the blog by navigating to `http://127.0.0.1` in your browser.
- **Data Persistence**: MySQL data files will be stored in the `data/mysql` directory within the project root, ensuring that your data persists across container restarts.

### Step 2: (Optional) Enable Elasticsearch for Full-Text Search

If you want to use Elasticsearch for more powerful full-text search capabilities, you can include the `docker-compose.es.yml` configuration file:

```bash
# Build and start all services in detached mode (Django, MySQL, Elasticsearch)
docker-compose -f docker-compose.yml -f deploy/docker-compose/docker-compose.es.yml up -d --build
```
- **Data Persistence**: Elasticsearch data will be stored in the `data/elasticsearch` directory.

### Step 3: First-Time Initialization

After the containers start for the first time, you'll need to execute some initialization commands inside the application container.

```bash
# Get a shell inside the djangoblog application container (named 'web')
docker-compose exec web bash

# Inside the container, run the following commands:
# Create a superuser account (follow the prompts to set username, email, and password)
python manage.py createsuperuser

# (Optional) Create some test data
python manage.py create_testdata

# (Optional, if ES is enabled) Create the search index
python manage.py rebuild_index

# Exit the container
exit
```

## 3. Alternative Method: Using the Standalone Docker Image

If you already have an external MySQL database running, you can run the DjangoBlog application image by itself.

```bash
# Pull the latest image from Docker Hub
docker pull liangliangyy/djangoblog:latest

# Run the container and connect it to your external database
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

- **Access Your Blog**: After startup, visit `http://127.0.0.1:8000`.
- **Create Superuser**: `docker exec -it djangoblog python manage.py createsuperuser`

## 4. Configuration (Environment Variables)

Most of the project's configuration is managed through environment variables. You can modify them in the `docker-compose.yml` file or pass them using the `-e` flag with the `docker run` command.

| Environment Variable      | Default/Example Value                                                    | Notes                                                               |
|---------------------------|--------------------------------------------------------------------------|---------------------------------------------------------------------|
| `DJANGO_SECRET_KEY`       | `your-strong-secret-key`                                                 | **Must be changed to a random, complex string!**                    |
| `DJANGO_DEBUG`            | `False`                                                                  | Toggles Django's debug mode.                                        |
| `DJANGO_MYSQL_HOST`       | `mysql`                                                                  | Database hostname.                                                  |
| `DJANGO_MYSQL_PORT`       | `3306`                                                                   | Database port.                                                      |
| `DJANGO_MYSQL_DATABASE`   | `djangoblog`                                                             | Database name.                                                      |
| `DJANGO_MYSQL_USER`       | `root`                                                                   | Database username.                                                  |
| `DJANGO_MYSQL_PASSWORD`   | `djangoblog_123`                                                         | Database password.                                                  |
| `DJANGO_REDIS_URL`        | `redis:6379/0`                                                           | Redis connection URL (for caching).                                 |
| `DJANGO_ELASTICSEARCH_HOST`| `elasticsearch:9200`                                                 | Elasticsearch host address.                                         |
| `DJANGO_EMAIL_HOST`       | `smtp.example.org`                                                       | Email server address.                                               |
| `DJANGO_EMAIL_PORT`       | `465`                                                                    | Email server port.                                                  |
| `DJANGO_EMAIL_USER`       | `user@example.org`                                                       | Email account username.                                             |
| `DJANGO_EMAIL_PASSWORD`   | `your-email-password`                                                    | Email account password.                                             |
| `DJANGO_EMAIL_USE_SSL`    | `True`                                                                   | Whether to use SSL.                                                 |
| `DJANGO_EMAIL_USE_TLS`    | `False`                                                                  | Whether to use TLS.                                                 |
| `DJANGO_ADMIN_EMAIL`      | `admin@example.org`                                                      | Admin email for receiving error reports.                            |
| `DJANGO_BAIDU_NOTIFY_URL` | `http://data.zz.baidu.com/...`                                         | Push API from [Baidu Webmaster Tools](https://ziyuan.baidu.com/linksubmit/index). |

---

After deployment, please review and adjust these environment variables according to your needs, especially `DJANGO_SECRET_KEY` and the database and email settings. 