from django.contrib import admin
# Register your models here.
from .models import Comment


def disable_commentstatus(modeladmin, request, queryset):
    queryset.update(is_enable=False)


def enable_commentstatus(modeladmin, request, queryset):
    queryset.update(is_enable=True)


disable_commentstatus.short_description = '禁用评论'
enable_commentstatus.short_description = '启用评论'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'body', 'author', 'is_enable', 'article', 'last_mod_time')
    list_display_links = ('id', 'body')
    list_filter = ('author', 'article', 'is_enable')
    exclude = ('created_time', 'last_mod_time')
    actions = [disable_commentstatus, enable_commentstatus]
