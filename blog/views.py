from django.shortcuts import render

# Create your views here.
import os
import datetime
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.conf import settings
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from DjangoBlog.utils import cache, get_md5, get_blog_setting
from django.shortcuts import get_object_or_404
from blog.models import Article, Category, Tag, Links
from comments.forms import CommentForm
import logging

logger = logging.getLogger(__name__)


class ArticleListView(ListView):
    # template_name Property to specify which template to use for rendering
    template_name = 'blog/article_index.html'

    # context_object_name Attribute is used to name the context variable (use that name in the template)
    context_object_name = 'article_list'

    # Page type, catalog or tag list, etc.
    page_type = ''
    page = ''
    paginate_by = settings.PAGINATE_BY
    page_kwarg = 'page'
    link_type = 'l'

    def get_view_cache_key(self):
        return self.request.get['pages']

    @property
    def page_number(self):
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        return page

    def get_queryset_cache_key(self):
        """
        Subclass rewrite. Get cache key of queryset
        """
        raise NotImplementedError()

    def get_queryset_data(self):
        """
        Subclass override. Get queryset data
        """
        raise NotImplementedError()

    def get_queryset_from_cache(self, cache_key):
        '''
        Cache page data
        :param cache_key: Cache key
        :return:
        '''
        value = cache.get(cache_key)
        if value:
            # logger.debug('get view cache.key:{key}'.format(key=cache_key))
            return value
        else:
            article_list = self.get_queryset_data()
            cache.set(cache_key, article_list)
            # logger.debug('set view cache.key:{key}'.format(key=cache_key))
            return article_list

    def get_queryset(self):
        '''
        Override default to get data from cache
        :return:
        '''
        key = self.get_queryset_cache_key()
        value = self.get_queryset_from_cache(key)
        return value

    def get_context_data(self, **kwargs):
        kwargs['linktype'] = self.link_type
        kwargs['page'] = self.page
        return super(ArticleListView, self).get_context_data(**kwargs)


class IndexView(ArticleListView):
    '''
    Home
    '''

    def __init__(self):
        self.page = 'main'
    # Friendly Link Type
    link_type = 'i'


    def get_queryset_data(self):
        article_list = Article.objects.filter(type='a', status='p')
        return article_list

    def get_queryset_cache_key(self):
        cache_key = 'index_{page}'.format(page=self.page_number)
        return cache_key

    # def get_context_data(self, **kwargs):

        # return super(ArticleListView, self).get_context_data(**kwargs)


class ArticleDetailView(DetailView):
    '''
    Article details page
    '''

    def __init__(self):
        self.page = 'article_details'
    template_name = 'blog/article_detail.html'
    model = Article
    pk_url_kwarg = 'article_id'
    context_object_name = "article"

    def get_object(self, queryset=None):
        obj = super(ArticleDetailView, self).get_object()
        obj.viewed()
        self.object = obj
        return obj

    def get_context_data(self, **kwargs):
        articleid = int(self.kwargs[self.pk_url_kwarg])
        comment_form = CommentForm()
        user = self.request.user
        # If the user is already logged in, hide the email and username input boxes
        if user.is_authenticated and not user.is_anonymous and user.email and user.username:
            comment_form.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })
            comment_form.fields["email"].initial = user.email
            comment_form.fields["name"].initial = user.username

        article_comments = self.object.comment_list()

        kwargs['form'] = comment_form
        kwargs['article_comments'] = article_comments
        kwargs['comment_count'] = len(article_comments) if article_comments else 0

        kwargs['next_article'] = self.object.next_article
        kwargs['prev_article'] = self.object.prev_article

        return super(ArticleDetailView, self).get_context_data(**kwargs)


class CategoryDetailView(ArticleListView):
    '''
    Category list
    '''
    page_type = "Категория"

    def __init__(self):
        self.page = 'category_details'

    def get_queryset_data(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, slug=slug)

        categoryname = category.name
        self.categoryname = categoryname
        categorynames = list(map(lambda c: c.name, category.get_sub_categorys()))
        article_list = Article.objects.filter(category__name__in=categorynames, status='p')
        return article_list

    def get_queryset_cache_key(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, slug=slug)
        categoryname = category.name
        self.categoryname = categoryname
        cache_key = 'category_list_{categoryname}_{page}'.format(categoryname=categoryname, page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):

        categoryname = self.categoryname
        try:
            categoryname = categoryname.split('/')[-1]
        except:
            pass
        kwargs['page_type'] = CategoryDetailView.page_type
        kwargs['tag_name'] = categoryname
        return super(CategoryDetailView, self).get_context_data(**kwargs)


class AuthorDetailView(ArticleListView):
    '''
    Страница сведений об авторе
    '''

    page_type = 'Автор'

    def __init__(self):
        self.page = 'author_details'

    def get_queryset_cache_key(self):
        author_name = self.kwargs['author_name']
        cache_key = 'author_{author_name}_{page}'.format(author_name=author_name, page=self.page_number)
        return cache_key

    def get_queryset_data(self):
        author_name = self.kwargs['author_name']
        article_list = Article.objects.filter(author__username=author_name, type='a', status='p')
        return article_list

    def get_context_data(self, **kwargs):
        author_name = self.kwargs['author_name']
        kwargs['page_type'] = AuthorDetailView.page_type
        kwargs['tag_name'] = author_name
        return super(AuthorDetailView, self).get_context_data(**kwargs)


class TagDetailView(ArticleListView):
    '''
    Страница списка тегов
    '''
    page_type = 'Тег'

    def __init__(self):
        self.page = 'tag_details'

    def get_queryset_data(self):
        slug = self.kwargs['tag_name']
        tag = get_object_or_404(Tag, slug=slug)
        tag_name = tag.name
        self.name = tag_name
        article_list = Article.objects.filter(tags__name=tag_name, type='a', status='p')
        return article_list

    def get_queryset_cache_key(self):
        slug = self.kwargs['tag_name']
        tag = get_object_or_404(Tag, slug=slug)
        tag_name = tag.name
        self.name = tag_name
        cache_key = 'tag_{tag_name}_{page}'.format(tag_name=tag_name, page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):
        # tag_name = self.kwargs['tag_name']
        tag_name = self.name
        kwargs['page_type'] = TagDetailView.page_type
        kwargs['tag_name'] = tag_name
        return super(TagDetailView, self).get_context_data(**kwargs)


class ArchivesView(ArticleListView):
    '''
    Article Archive Page
    '''
    page_type = 'Публикация'
    paginate_by = None
    page_kwarg = None
    template_name = 'blog/article_archives.html'

    def __init__(self):
        self.page = 'archive'

    def get_queryset_data(self, **kwargs):
        return Article.objects.filter(status='p').all()

    def get_queryset_cache_key(self, **kwargs):
        cache_key = 'archives'
        return cache_key

    def get_context_data(self, **kwargs):
        kwargs['months_map'] = {1: 'январь', 2: 'февраль', 3: 'март',
                                4: 'апрель', 5: 'май', 6: 'июнь',
                                7: 'июль', 8: 'август', 9: 'сентябрь',
                                10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'}
        return super(ArchivesView, self).get_context_data(**kwargs)


class LinkListView(ListView):
    model = Links
    template_name = 'blog/links_list.html'

    def get_queryset(self):
        return Links.objects.filter(is_enable=True)


@csrf_exempt
def fileupload(request):
    """
    This method needs to write the caller to upload the picture.
    This method only provides the picture bed function.
    :param request:
    :return:
    """
    if request.method == 'POST':
        sign = request.GET.get('sign', None)
        if not sign:
            return HttpResponseForbidden()
        if not sign == get_md5(get_md5(settings.SECRET_KEY)):
            return HttpResponseForbidden()
        response = []
        for filename in request.FILES:
            timestr = datetime.datetime.now().strftime('%Y/%m/%d')
            imgextensions = ['jpg', 'png', 'jpeg', 'bmp']
            fname = u''.join(str(filename))
            isimage = len([i for i in imgextensions if fname.find(i) >= 0]) > 0
            blogsetting = get_blog_setting()

            basepath = r'{basedir}/{type}/{timestr}'.format(basedir=blogsetting.resource_path,
                                                            type='files' if not isimage else 'image', timestr=timestr)
            if settings.TESTING:
                basepath = settings.BASE_DIR + '/uploads'
            url = 'https://resource.mtuktarov.com/{type}/{timestr}/{filename}'.format(
                type='files' if not isimage else 'image', timestr=timestr, filename=filename)
            if not os.path.exists(basepath):
                os.makedirs(basepath)
            savepath = os.path.join(basepath, filename)
            with open(savepath, 'wb+') as wfile:
                for chunk in request.FILES[filename].chunks():
                    wfile.write(chunk)
            if isimage:
                from PIL import Image
                image = Image.open(savepath)
                image.save(savepath, quality=20, optimize=True)
            response.append(url)
        return HttpResponse(response)

    else:
        return HttpResponse("only for post")


@login_required
def refresh_memcache(request):
    try:
        if request.user.is_superuser:
            from DjangoBlog.utils import cache
            if cache and cache is not None:
                cache.clear()
                logger.info("cache has been cleared successfully")
            return HttpResponseRedirect('/')
        else:
            return HttpResponseForbidden()
    except Exception as e:
        logger.error(e)
        return HttpResponse(e)


def page_not_found_view(request, exception, template_name='blog/error_page.html'):
    if exception:
        logger.error(exception)
    url = request.get_full_path()
    return render(request, template_name,
                  {'message': 'соррян,' + url + ' мы такой страницы не нашли!', 'statuscode': '404'}, status=404)


def server_error_view(request, template_name='blog/error_page.html'):
    return render(request, template_name,
                  {'message': 'Соррян, что-то не отработало... Мы поглядим!', 'statuscode': '500'}, status=500)


def permission_denied_view(request, exception, template_name='blog/error_page.html'):
    if exception:
        logger.error(exception)
    return render(request, template_name,
                  {'message': 'Соррян, вам сюда нельзя!', 'statuscode': '403'}, status=403)
