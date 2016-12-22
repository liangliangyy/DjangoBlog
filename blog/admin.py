from django.contrib import admin

# Register your models here.
from .models import Article, Category, Tag, Links
from pagedown.widgets import AdminPagedownWidget
from django import forms


class ArticleForm(forms.ModelForm):
    body = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = Article
        fields = '__all__'


class ArticlelAdmin(admin.ModelAdmin):
    form = ArticleForm


admin.site.register(Article, ArticlelAdmin)
#admin.site.register(BlogPage, ArticlelAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Links)
