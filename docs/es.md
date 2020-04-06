# 集成Elasticsearch
如果你已经有了`Elasticsearch`环境，那么可以将搜索从`Whoosh`换成`Elasticsearch`，集成方式也很简单，
首先需要注意如下几点:
1. 你的`Elasticsearch`支持`ik`中文分词
2. 你的`Elasticsearch`版本>=7.3.0

接下来在`settings.py`做如下改动即可：
- 增加es链接，如下所示：
```python
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': '127.0.0.1:9200'
    },
}
```
- 修改`HAYSTACK`配置：
```python
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'DjangoBlog.elasticsearch_backend.ElasticSearchEngine',
    },
}
```
然后终端执行:
```shell script
./manage.py build_index
```
这将会在你的es中创建两个索引，分别是`blog`和`performance`，其中`blog`索引就是搜索所使用的，而`performance`会记录每个请求的响应时间，以供将来优化使用。