from django.contrib import admin

# Register your models here.
from .models import Article, Category, Tag, Links
from pagedown.widgets import AdminPagedownWidget
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class ArticleListFilter(admin.SimpleListFilter):
    title = _("作者")
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        authors = list(set(map(lambda x: x.author, Article.objects.all())))
        for author in authors:
            yield (author.id, _(author.username))

    def queryset(self, request, queryset):
        id = self.value()
        if id:
            return queryset.filter(author__id__exact=id)
        else:
            return queryset


class ArticleForm(forms.ModelForm):
    body = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = Article
        fields = '__all__'


class ArticlelAdmin(admin.ModelAdmin):
    form = ArticleForm
    list_display = ('id', 'title', 'author', 'created_time', 'views', 'status', 'type')
    list_display_links = ('id', 'title')
    list_filter = (ArticleListFilter, 'status', 'type', 'category', 'tags')
    filter_horizontal = ('tags',)
    exclude = ('slug', 'created_time', 'last_mod_time')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ArticlelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].queryset = get_user_model().objects.filter(is_superuser=True)
        return form

    def save_model(self, request, obj, form, change):
        super(ArticlelAdmin, self).save_model(request, obj, form, change)
        from DjangoBlog.utils import cache
        cache.clear()


class TagAdmin(admin.ModelAdmin):
    exclude = ('slug', 'last_mod_time', 'created_time')


class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug', 'last_mod_time', 'created_time')


class LinksAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')


admin.site.register(Article, ArticlelAdmin)
# admin.site.register(BlogPage, ArticlelAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Links, LinksAdmin)
