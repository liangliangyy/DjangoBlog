from django.shortcuts import render

# Create your views here.
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.dates import YearArchiveView, MonthArchiveView
from blog.models import Article, Category, Tag
from django.conf import settings
import markdown
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


class ArticleListView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'

    def __init__(self):
        self.page_description = ''


class IndexView(ArticleListView):
    # template_name属性用于指定使用哪个模板进行渲染
    # template_name = 'index.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    # context_object_name = 'article_list'

    def get_queryset(self):
        article_list = Article.objects.filter(status='p')

        for article in article_list:
            article.body = article.body[0:settings.ARTICLE_SUB_LENGTH]
            # article.body = markdown2.markdown(article.body)

        return article_list

    def get_context_data(self, **kwargs):
        # 增加额外的数据，这里返回一个文章分类，以字典的形式
        kwargs['category_list'] = Category.objects.all().order_by('name')
        return super(IndexView, self).get_context_data(**kwargs)


class ArticleDetailView(DetailView):
    template_name = 'articledetail.html'
    model = Article
    pk_url_kwarg = 'article_id'
    context_object_name = "article"

    def get_object(self):
        obj = super(ArticleDetailView, self).get_object()
        # obj.body = markdown2.markdown(obj.body)
        return obj


class CategoryDetailView(ArticleListView):
    # template_name = 'index.html'
    # context_object_name = 'article_list'

    # pk_url_kwarg = 'article_name'

    def get_queryset(self):
        categoryname = self.kwargs['category_name']
        # print(categoryname)
        self.page_description = '分类目录归档: %s '
        article_list = Article.objects.filter(category__name=categoryname, status='p')
        return article_list


class AuthorDetailView(ArticleListView):
    def get_queryset(self):
        author_name = self.kwargs['author_name']

        self.page_description = '分类目录归档: %s ' % author_name
        article_list = Article.objects.filter(author__username=author_name)
        return article_list
