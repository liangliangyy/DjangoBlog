from django import forms
from django.forms import ModelForm

from .models import Comment


class CommentForm(ModelForm):
    parent_comment_id = forms.IntegerField(
        widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['body']
