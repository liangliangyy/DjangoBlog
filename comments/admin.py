from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Comment, CommentReaction


def disable_commentstatus(modeladmin, request, queryset):
    queryset.update(is_enable=False)


def enable_commentstatus(modeladmin, request, queryset):
    queryset.update(is_enable=True)


disable_commentstatus.short_description = _('Disable comments')
enable_commentstatus.short_description = _('Enable comments')


class CommentAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        'id',
        'body',
        'link_to_userinfo',
        'link_to_article',
        'is_enable',
        'creation_time')
    list_display_links = ('id', 'body', 'is_enable')
    list_filter = ('is_enable',)
    exclude = ('creation_time', 'last_modify_time')
    actions = [disable_commentstatus, enable_commentstatus]
    raw_id_fields = ('author', 'article')
    search_fields = ('body',)

    def link_to_userinfo(self, obj):
        info = (obj.author._meta.app_label, obj.author._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(
            u'<a href="%s">%s</a>' %
            (link, obj.author.nickname if obj.author.nickname else obj.author.email))

    def link_to_article(self, obj):
        info = (obj.article._meta.app_label, obj.article._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.article.id,))
        return format_html(
            u'<a href="%s">%s</a>' % (link, obj.article.title))

    link_to_userinfo.short_description = _('User')
    link_to_article.short_description = _('Article')


class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reaction_type', 'link_to_comment', 'link_to_user', 'created_at')
    list_display_links = ('id', 'reaction_type')
    list_filter = ('reaction_type', 'created_at')
    raw_id_fields = ('comment', 'user')
    search_fields = ('comment__body', 'user__username')
    date_hierarchy = 'created_at'

    def link_to_comment(self, obj):
        info = (obj.comment._meta.app_label, obj.comment._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.comment.id,))
        return format_html(
            u'<a href="%s">Comment #%s</a>' % (link, obj.comment.id))

    def link_to_user(self, obj):
        info = (obj.user._meta.app_label, obj.user._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.user.id,))
        return format_html(
            u'<a href="%s">%s</a>' %
            (link, obj.user.nickname if obj.user.nickname else obj.user.username))

    link_to_comment.short_description = _('Comment')
    link_to_user.short_description = _('User')


admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentReaction, CommentReactionAdmin)
