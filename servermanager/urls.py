from django.urls import path, re_path
from werobot.contrib.django import make_view

from .robot import robot
from .views import statistics_view

app_name = "servermanager"
urlpatterns = [
    path('statistics/', statistics_view, name='statistics'),
    path('robot/', make_view(robot)),

]
