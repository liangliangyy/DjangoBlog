# Create your views here.
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from djangoblog.base_views import AuthenticatedFormView
from accounts.models import BlogUser
from blog.models import Article
from .forms import CommentForm
from .models import Comment


class CommentPostView(AuthenticatedFormView):
    """
    评论提交视图（重构版）

    使用 AuthenticatedFormView 基类，自动提供：
    - 登录验证（未登录用户会被重定向）
    - CSRF 保护
    """
    form_class = CommentForm
    template_name = 'blog/article_detail.html'

    def get(self, request, *args, **kwargs):
        article_id = self.kwargs['article_id']
        article = get_object_or_404(Article, pk=article_id)
        url = article.get_absolute_url()
        return HttpResponseRedirect(url + "#comments")

    def form_invalid(self, form):
        article_id = self.kwargs['article_id']
        article = get_object_or_404(Article, pk=article_id)

        return self.render_to_response({
            'form': form,
            'article': article
        })

    def form_valid(self, form):
        """提交的数据验证合法后的逻辑"""
        user = self.request.user
        author = BlogUser.objects.get(pk=user.pk)
        article_id = self.kwargs['article_id']
        article = get_object_or_404(Article, pk=article_id)

        if article.comment_status == 'c' or article.status == 'c':
            raise ValidationError("该文章评论已关闭.")
        comment = form.save(False)
        comment.article = article
        from djangoblog.utils import get_blog_setting
        settings = get_blog_setting()
        if not settings.comment_need_review:
            comment.is_enable = True
        comment.author = author

        if form.cleaned_data['parent_comment_id']:
            parent_comment = Comment.objects.get(
                pk=form.cleaned_data['parent_comment_id'])
            comment.parent_comment = parent_comment

        comment.save(True)
        return HttpResponseRedirect(
            "%s#div-comment-%d" %
            (article.get_absolute_url(), comment.pk))
