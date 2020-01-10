#!/usr/bin/env python

from .models import Comment
from django import forms
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class CommentForm(ModelForm):
    url = forms.URLField(label='Сайт', required=False)
    email = forms.EmailField(label='Адрес электронной почты', required=True)
    name = forms.CharField(label='Полное имя', widget=forms.TextInput(attrs={'value': "", 'size': "30", 'maxlength': "245",
                                                                             'aria-required': 'true'}
                                                                      ))
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={'placeholder': 'Оставить комментарий (с поддержкой маркдауна)'}),
        }
