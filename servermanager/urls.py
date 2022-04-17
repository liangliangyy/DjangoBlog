from django.urls import path
from werobot.contrib.django import make_view

from .robot import robot

app_name = "servermanager"
urlpatterns = [
    path(r'robot', make_view(robot)),

]
