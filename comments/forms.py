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
from django.contrib.auth import get_user_model

"""
class CommentForm(forms.Form):
    url = forms.URLField(label='网址', required=False)
    email = forms.EmailField(label='电子邮箱', required=False)
    name = forms.CharField(label='姓名')
    body = forms.CharField(widget=forms.Textarea, label='评论')
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)



class LoginCommentForm(ModelForm):
    url = forms.URLField(label='网址', required=False)
    email = forms.EmailField(label='电子邮箱', required=False, widget=forms.HiddenInput)
    name = forms.CharField(label='姓名', widget=forms.HiddenInput)
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    def __init__(self):
        pass
    class Meta:
        model = Comment
        fields = ['body']
"""


class CommentForm(ModelForm):
    url = forms.URLField(label='网址', required=False)
    email = forms.EmailField(label='电子邮箱', required=True)
    name = forms.CharField(label='姓名', widget=forms.TextInput(attrs=
                                                              {'value': "", 'size': "30", 'maxlength': "245",
                                                               'aria-required': 'true'}
                                                              ))
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    """
    if get_user_model().is_authenticated:
        email = forms.EmailField(label='电子邮箱', required=False, widget=forms.HiddenInput)
        name = forms.CharField(label='姓名', widget=forms.HiddenInput)
    """
    """
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CommentForm, self).__init__(*args, **kwargs)
        if self.user.is_authenticated:
            self.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })
    """

    class Meta:
        model = Comment
        fields = ['body']
