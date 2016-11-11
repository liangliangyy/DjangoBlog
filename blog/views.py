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
from django.core.exceptions import ObjectDoesNotExist


class ArticleListView(ListView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'blog/index.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'article_list'

    # 页面类型，分类目录或标签列表等
    page_type = ''


class IndexView(ArticleListView):
    def get_queryset(self):
        article_list = Article.objects.filter(status='p')

        # for article in article_list:
        #     article.body = article.body[0:settings.ARTICLE_SUB_LENGTH]
        #     # article.body = markdown2.markdown(article.body)

        return article_list


class ArticleDetailView(DetailView):
    template_name = 'blog/articledetail.html'
    model = Article
    pk_url_kwarg = 'article_id'
    context_object_name = "article"

    def get_object(self):
        obj = super(ArticleDetailView, self).get_object()
        obj.viewed()
        # obj.body = markdown2.markdown(obj.body)
        return obj

    def get_context_data(self, **kwargs):
        articleid = int(self.kwargs['article_id'])

        def get_article(id):
            try:
                return Article.objects.get(pk=id)
            except ObjectDoesNotExist:
                return None

        next_article = get_article(articleid + 1)
        prev_article = get_article(articleid - 1)
        kwargs['next_article'] = next_article
        kwargs['prev_article'] = prev_article

        return super(ArticleDetailView, self).get_context_data(**kwargs)


class CategoryDetailView(ArticleListView):
    # template_name = 'index.html'
    # context_object_name = 'article_list'

    # pk_url_kwarg = 'article_name'
    page_type = "分类目录归档"

    def get_queryset(self):
        categoryname = self.kwargs['category_name']
        article_list = Article.objects.filter(category__name=categoryname, status='p')
        return article_list

    def get_context_data(self, **kwargs):
        categoryname = self.kwargs['category_name']

        kwargs['page_type'] = CategoryDetailView.page_type
        kwargs['tag_name'] = categoryname
        return super(CategoryDetailView, self).get_context_data(**kwargs)


class AuthorDetailView(ArticleListView):
    page_type = '作者文章归档'

    def get_queryset(self):
        author_name = self.kwargs['author_name']

        article_list = Article.objects.filter(author__username=author_name)
        return article_list

    def get_context_data(self, **kwargs):
        author_name = self.kwargs['author_name']
        kwargs['page_type'] = AuthorDetailView.page_type
        kwargs['tag_name'] = author_name
        return super(AuthorDetailView, self).get_context_data(**kwargs)


class TagListView(ListView):
    template_name = ''
    context_object_name = 'tag_list'

    def get_queryset(self):
        tags_list = []
        tags = Tag.objects.all()
        for t in tags:
            t.article_set.count()


class TagDetailView(ArticleListView):
    page_type = '分类标签归档'

    def get_queryset(self):
        tag_name = self.kwargs['tag_name']

        article_list = Article.objects.filter(tags__name=tag_name)
        return article_list

    def get_context_data(self, **kwargs):
        tag_name = self.kwargs['tag_name']
        kwargs['page_type'] = TagDetailView.page_type
        kwargs['tag_name'] = tag_name
        return super(TagDetailView, self).get_context_data(**kwargs)
