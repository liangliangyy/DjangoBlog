#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: forms.py
@time: 2016/11/12 下午2:45
"""
from .models import Comment
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

"""
class CommentForm(forms.Form):
    url = forms.URLField(label='网址', required=False)
    email = forms.EmailField(label='电子邮箱', required=False)
    name = forms.CharField(label='姓名')
    body = forms.CharField(widget=forms.Textarea, label='评论')
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
"""


class CommentForm(ModelForm):
    url = forms.URLField(label='网址', required=False)
    if User.is_authenticated:
        email = forms.EmailField(label='电子邮箱', required=False, widget=forms.HiddenInput)
        name = forms.CharField(label='姓名', widget=forms.HiddenInput)
    else:
        email = forms.EmailField(label='电子邮箱', required=False)
        name = forms.CharField(label='姓名')
    # body = forms.CharField(widget=forms.Textarea, label='评论')
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['body']

