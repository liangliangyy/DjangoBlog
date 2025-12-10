from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect

# Register your models here.
from .models import Article, Category, Tag, Links, SideBar, BlogSettings, ArticleVersion


class ArticleForm(forms.ModelForm):
    # body = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = Article
        fields = '__all__'


def makr_article_publish(modeladmin, request, queryset):
    queryset.update(status='p')


def draft_article(modeladmin, request, queryset):
    queryset.update(status='d')


def close_article_commentstatus(modeladmin, request, queryset):
    queryset.update(comment_status='c')


def open_article_commentstatus(modeladmin, request, queryset):
    queryset.update(comment_status='o')


makr_article_publish.short_description = _('Publish selected articles')
draft_article.short_description = _('Draft selected articles')
close_article_commentstatus.short_description = _('Close article comments')
open_article_commentstatus.short_description = _('Open article comments')


class ArticlelAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('body', 'title')
    form = ArticleForm
    list_display = (
        'id',
        'title',
        'author',
        'link_to_category',
        'creation_time',
        'views',
        'status',
        'type',
        'article_order',
        'view_versions')
    list_display_links = ('id', 'title')
    list_filter = ('status', 'type', 'category')
    date_hierarchy = 'creation_time'
    filter_horizontal = ('tags',)
    exclude = ('creation_time', 'last_modify_time')
    view_on_site = True
    actions = [
        makr_article_publish,
        draft_article,
        close_article_commentstatus,
        open_article_commentstatus]
    raw_id_fields = ('author', 'category',)

    def link_to_category(self, obj):
        info = (obj.category._meta.app_label, obj.category._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.category.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.category.name))

    link_to_category.short_description = _('category')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ArticlelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].queryset = get_user_model(
        ).objects.filter(is_superuser=True)
        return form

    def save_model(self, request, obj, form, change):
        super(ArticlelAdmin, self).save_model(request, obj, form, change)

    def get_view_on_site_url(self, obj=None):
        if obj:
            url = obj.get_full_url()
            return url
        else:
            from djangoblog.utils import get_current_site
            site = get_current_site().domain
            return site
            
    def view_versions(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:blog_articleversion_changelist') + f'?article__id__exact={obj.id}',
            _('View Versions')
    )
    
    view_versions.short_description = _('Versions')


class TagAdmin(admin.ModelAdmin):
    exclude = ('slug', 'last_mod_time', 'creation_time')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'index')
    exclude = ('slug', 'last_mod_time', 'creation_time')


class LinksAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'creation_time')


class SideBarAdmin(admin.ModelAdmin):
    list_display = ('name', 'content', 'is_enable', 'sequence')
    exclude = ('last_mod_time', 'creation_time')


def compare_article_versions(modeladmin, request, queryset):
    # 需要选择两个版本进行对比
    if len(queryset) != 2:
        modeladmin.message_user(request, _('Please select exactly two versions to compare.'), level='error')
        return
    
    versions = list(queryset)
    return HttpResponseRedirect(f"/blog/compare-versions?v1={versions[0].id}&v2={versions[1].id}")


def restore_article_version(modeladmin, request, queryset):
    # 只能恢复一个版本
    if len(queryset) != 1:
        modeladmin.message_user(request, _('Please select exactly one version to restore.'), level='error')
        return
    
    version = queryset.first()
    article = version.article
    
    # 恢复版本内容到文章
    article.title = version.title
    article.body = version.body
    article.save()
    
    modeladmin.message_user(request, _(f'Successfully restored to version {version.version_number}'))


compare_article_versions.short_description = _('Compare selected versions')


restore_article_version.short_description = _('Restore selected version')


class ArticleVersionAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('title', 'body')
    list_display = (
        'id',
        'article_title',
        'version_number',
        'editor',
        'creation_time',
        'comment'
    )
    list_display_links = ('id', 'version_number')
    list_filter = ('editor', 'creation_time')
    date_hierarchy = 'creation_time'
    readonly_fields = ('article', 'version_number', 'title', 'body', 'editor', 'creation_time', 'comment')
    actions = [compare_article_versions, restore_article_version]
    
    def article_title(self, obj):
        info = (obj.article._meta.app_label, obj.article._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.article.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.article.title))
    
    article_title.short_description = _('Article Title')
    
    def has_add_permission(self, request):
        # 禁止手动添加版本，版本只能自动创建
        return False
    
    def has_change_permission(self, request, obj=None):
        # 禁止修改版本记录
        return False


class BlogSettingsAdmin(admin.ModelAdmin):
    pass


# BlogSettings已经在admin_site中注册了
