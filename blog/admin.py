from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Article, Category, Tag, Links, SideBar, BlogSettings


class ScheduledPublishFilter(admin.SimpleListFilter):
    title = _('scheduled publish status')
    parameter_name = 'scheduled_status'

    def lookups(self, request, model_admin):
        return (
            ('scheduled', _('Scheduled')),
            ('past', _('Scheduled time passed')),
            ('not_scheduled', _('Not scheduled')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'scheduled':
            return queryset.filter(
                scheduled_publish_time__isnull=False,
                scheduled_publish_time__gt=now()
            )
        elif self.value() == 'past':
            return queryset.filter(
                scheduled_publish_time__isnull=False,
                scheduled_publish_time__lte=now()
            )
        elif self.value() == 'not_scheduled':
            return queryset.filter(scheduled_publish_time__isnull=True)
        return queryset


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
        'pub_time',
        'scheduled_publish_time',
        'scheduled_status_display',
        'views',
        'status',
        'type',
        'article_order')
    list_display_links = ('id', 'title')
    list_filter = ('status', 'type', 'category', ScheduledPublishFilter)
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
    fieldsets = (
        (None, {
            'fields': ('title', 'body', 'status', 'pub_time', 'scheduled_publish_time')
        }),
        (_('Classification'), {
            'fields': ('category', 'tags', 'type', 'article_order', 'author')
        }),
        (_('Other Settings'), {
            'fields': ('comment_status', 'show_toc', 'views')
        }),
    )

    def link_to_category(self, obj):
        info = (obj.category._meta.app_label, obj.category._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.category.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.category.name))

    link_to_category.short_description = _('category')

    def scheduled_status_display(self, obj):
        """显示定时发布状态"""
        if not obj.is_scheduled_publish():
            return format_html('<span style="color: #666;">{}</span>', _('Not scheduled'))
        if obj.is_past_scheduled_time():
            if obj.status == 'p':
                return format_html('<span style="color: #0a0;">{}</span>', _('Published'))
            else:
                return format_html('<span style="color: #a00;">{}</span>', _('Scheduled time passed'))
        return format_html(
            '<span style="color: #00a; font-weight: bold;">{}</span>',
            _('Scheduled')
        )

    scheduled_status_display.short_description = _('scheduled status')
    scheduled_status_display.admin_order_field = 'scheduled_publish_time'

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


class BlogSettingsAdmin(admin.ModelAdmin):
    """单例配置Admin - 直接跳转到编辑页面"""

    def has_add_permission(self, request):
        """如果已经存在配置，则禁止添加"""
        return not BlogSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """禁止删除配置"""
        return False

    def changelist_view(self, request, extra_context=None):
        """列表页直接跳转到编辑页面"""
        from django.http import HttpResponseRedirect
        obj = BlogSettings.objects.first()
        if obj:
            return HttpResponseRedirect(
                reverse('admin:blog_blogsettings_change', args=[obj.pk])
            )
        # 如果不存在配置，跳转到添加页面
        return HttpResponseRedirect(
            reverse('admin:blog_blogsettings_add')
        )

    def save_model(self, request, obj, form, change):
        """保存设置时清除缓存"""
        super().save_model(request, obj, form, change)
        # 确保缓存被清除
        from djangoblog.utils import cache
        cache.clear()
        self.message_user(request, '设置已保存，缓存已清除')
