from django.shortcuts import render

# Create your views here.
from .models import Comment
from blog.models import Article
from .forms import CommentForm
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django import forms


class CommentPostView(FormView):
    form_class = CommentForm
    template_name = 'blog/article_detail.html'

    def get(self, request, *args, **kwargs):
        article_id = self.kwargs['article_id']

        article = Article.objects.get(pk=article_id)
        url = article.get_absolute_url()
        return HttpResponseRedirect(url + "#comments")

    def form_invalid(self, form):
        article_id = self.kwargs['article_id']
        article = Article.objects.get(pk=article_id)
        u = self.request.user

        if self.request.user.is_authenticated:
            form.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })
            user = self.request.user
            form.fields["email"].initial = user.email
            form.fields["name"].initial = user.username

        return self.render_to_response({
            'form': form,
            'article': article
        })

    def form_valid(self, form):
        """The logic after the submitted data is verified"""
        user = self.request.user

        article_id = self.kwargs['article_id']
        article = Article.objects.get(pk=article_id)
        if not self.request.user.is_authenticated:
            email = form.cleaned_data['email']
            username = form.cleaned_data['name']

            user = get_user_model().objects.get_or_create(username=username, email=email)[0]
            # auth.login(self.request, user)
        comment = form.save(False)
        comment.article = article

        comment.author = user

        if form.cleaned_data['parent_comment_id']:
            parent_comment = Comment.objects.get(pk=form.cleaned_data['parent_comment_id'])
            comment.parent_comment = parent_comment

        comment.save(True)
        return HttpResponseRedirect("%s#div-comment-%d" % (article.get_absolute_url(), comment.pk))
