from django.urls import path

from . import views

app_name = "comments"
urlpatterns = [
    path(
        'article/<int:article_id>/postcomment',
        views.CommentPostView.as_view(),
        name='postcomment'),
]
