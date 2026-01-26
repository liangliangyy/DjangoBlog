from django.urls import path
from .views import ArticleStatisticsView, UserStatisticsView, ActiveUserStatisticsView

app_name = 'blog_statistics'

urlpatterns = [
    path('articles/', ArticleStatisticsView.as_view(), name='article_statistics'),
    path('users/', UserStatisticsView.as_view(), name='user_statistics'),
    path('active-users/', ActiveUserStatisticsView.as_view(), name='active_user_statistics'),
]