#DjangoBlog

基于`python3.5`和`Django1.10`的博客。

## 安装
使用pip安装：  
`pip install -r requirements.txt`

如果你没有pip，使用如下方式安装：    
OS X / Linux 电脑，终端下执行:  

    curl http://peak.telecommunity.com/dist/ez_setup.py | python
    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
    
windows电脑：  
 下载 http://peak.telecommunity.com/dist/ez_setup.py 和 https://raw.github.com/pypa/pip/master/contrib/get-pip.py 这两个文件，双击运行。
 
 ## 运行
 
 修改`DjangoBlog/setting.py` 修改数据库配置，如下所示：
   
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
      
 ### 创建数据库
 
 终端下执行:  
 
    ./manage.py makemigrations
    ./manage.py migrate  
 ### 开始运行：
 执行：  
 `./manage.py runserver`
 
 浏览器打开:http://127.0.0.1:8000/就可以看到效果了。
 