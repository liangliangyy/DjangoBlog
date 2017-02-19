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

    def save_model(self, request, obj, form, change):
        super(ArticlelAdmin, self).save_model(request, obj, form, change)
        from DjangoBlog.utils import cache
        cache.clear()


admin.site.register(Article, ArticlelAdmin)
# admin.site.register(BlogPage, ArticlelAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Links)
