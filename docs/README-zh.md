# DjangoBlog

🌍
*[English](/docs/README-en.md) ∙ [簡體中文](README.md) ∙ [繁體中文](/docs/README-zh.md) *

基於 `python3.8` 和 `Django4.0` 的博客系統。

[![Django CI](https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml/badge.svg)](https://github.com/liangliangyy/DjangoBlog/actions/workflows/django.yml) [![CodeQL](https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/liangliangyy/DjangoBlog/actions/workflows/codeql-analysis.yml) [![codecov](https://codecov.io/gh/liangliangyy/DjangoBlog/branch/master/graph/badge.svg)](https://codecov.io/gh/liangliangyy/DjangoBlog) [![license](https://img.shields.io/github/license/liangliangyy/djangoblog.svg)]()

## 主要功能：
- 文章、頁面、分類目錄、標籤的添加、刪除、編輯等功能。文章、評論及頁面支援 `Markdown`，支援代碼高亮。
- 支援文章全文搜索。
- 完整的評論功能，包括發表回覆評論和評論的郵件提醒，支援 `Markdown`。
- 側邊欄功能：最新文章、最多閱讀、標籤雲等。
- 支援 Oauth 登錄，現已有 Google、GitHub、Facebook、微博、QQ 登錄。
- 支援 `Redis` 快取，並支援快取自動刷新。
- 簡單的 SEO 功能，新建文章等會自動通知 Google 和百度。
- 集成了簡單的圖床功能。
- 集成 `django-compressor`，自動壓縮 `css`、`js`。
- 網站異常郵件提醒，若有未捕獲到的異常會自動發送提醒郵件。
- 集成了微信公眾號功能，現在可以使用微信公眾號來管理你的 VPS 了。

## 安裝
將 MySQL 客戶端從 `pymysql` 修改為 `mysqlclient`，具體請參考 [pypi](https://pypi.org/project/mysqlclient/) 查看安裝前的準備。

使用 pip 安裝： `pip install -Ur requirements.txt`

如果你沒有 pip，使用如下方式安裝：
- OS X / Linux 電腦，終端下執行：

    ```
    curl http://peak.telecommunity.com/dist/ez_setup.py | python
    curl https://bootstrap.pypa.io/get-pip.py | python
    ```

- Windows 電腦：

    下載 http://peak.telecommunity.com/dist/ez_setup

.py 和 https://raw.github.com/pypa/pip/master/contrib/get-pip.py 這兩個文件，雙擊運行。

## 運行

修改 `djangoblog/setting.py` 修改數據庫配置，如下所示：

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

### 創建數據庫
在 MySQL 數據庫中執行：
```sql
CREATE DATABASE `djangoblog` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
```

然後在終端下執行：
```bash
python manage.py makemigrations
python manage.py migrate
```

### 創建超級用戶

在終端下執行：
```bash
python manage.py createsuperuser
```

### 創建測試數據
在終端下執行：
```bash
python manage.py create_testdata
```

### 收集靜態文件
在終端下執行：
```bash
python manage.py collectstatic --noinput
python manage.py compress --force
```

### 開始運行：
執行： `python manage.py runserver`

在瀏覽器中打開：http://127.0.0.1:8000/，就可以看到博客效果了。

## 伺服器部署

本地安裝部署請參考 [DjangoBlog部署教程](https://www.lylinux.net/article/2019/8/5/58.html)，有詳細的部署介紹。

本專案已經支援使用 Docker 來部署，如果你有 Docker 環境，那麼可以使用 Docker 來部署，具體請參考：[docker部署](/docs/docker.md)

## 更多配置：
[更多配置介紹](/docs/config.md)  
[集成 Elasticsearch](/docs/es.md)

## 相關問題

如果你有任何問題，歡迎提出 Issue，或將問題描述發送到我的電子郵件 `liangliangyy#gmail.com`。我會盡快解答。推薦使用 Issue 方式。

---
## 致大家 🙋‍♀️🙋‍♂️
如果這個專案對你有所幫助，請在[這裡](https://github.com/liangliangyy/DjangoBlog/issues/214)提交你的網址，讓更多的人看到它。

你的回覆將是我繼續更新和維護這個專案的動力。

## 捐贈
如果你覺得這個專案對你有所幫

助，歡迎你請我喝杯咖啡。你的支持是我最大的動力。你可以掃描下方二維碼為我付款，謝謝。

### 支付寶：
<div>    
<img src="https://resource.lylinux.net/image/2017/12/16/IMG_0207.jpg" width="150" height="150" />
</div>  

### 微信：
<div>    
<img src="https://resource.lylinux.net/image/2017/12/16/IMG_0206.jpg" width="150" height="150" />
</div>

---

感謝 JetBrains
<div>    
<a href="https://www.jetbrains.com/?from=DjangoBlog"><img src="https://resource.lylinux.net/image/2020/07/01/logo.png" width="150" height="150"></a>
</div>