from django.shortcuts import render

# Create your views here.
from django.views.generic.list import ListView
from blog.models import Article, Category, Tag
import markdown2


class IndexView(ListView):

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'blog/index.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'article_list'

    def get_queryset(self):
        article_list = Article.objects.filter(status='p')
        for article in article_list:
            article.body = markdown2.markdown(article.body)
        return article_list

    def get_context_data(self, **kwargs):
        # 增加额外的数据，这里返回一个文章分类，以字典的形式
        kwargs['category_list'] = Category.objects.all().order_by('name')
        return super(IndexView, self).get_context_data(**kwargs)
