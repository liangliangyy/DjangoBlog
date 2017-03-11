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
    list_display = ('id', 'title', 'author', 'created_time', 'views', 'status', 'type')
    list_display_links = ('id', 'title')
    list_filter = ('author', 'status', 'type', 'category', 'tags')
    filter_horizontal = ('tags',)
    exclude = ('slug', 'created_time')

    def save_model(self, request, obj, form, change):
        super(ArticlelAdmin, self).save_model(request, obj, form, change)
        from DjangoBlog.utils import cache
        cache.clear()


class TagAdmin(admin.ModelAdmin):
    exclude = ('slug',)


class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug',)


admin.site.register(Article, ArticlelAdmin)
# admin.site.register(BlogPage, ArticlelAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Links)
