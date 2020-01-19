#!/usr/bin/env python

from django.contrib.admin import AdminSite
from DjangoBlog.utils import get_current_site
from django.contrib.sites.admin import SiteAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.sites.models import Site
from DjangoBlog.logentryadmin import LogEntryAdmin
from blog.admin import *
from accounts.admin import *
from oauth.admin import *
from servermanager.admin import *
from comments.admin import *


class DjangoBlogAdminSite(AdminSite):
    site_header = 'Настройки блога'
    site_title = 'Админ блога'

    def __init__(self, name='admin'):
        super().__init__(name)

    def has_permission(self, request):
        return request.user.is_superuser

    # def get_urls(self):
    #     urls = super().get_urls()
    #     from django.urls import path
    #     from blog.views import refresh_memcache
    #
    #     my_urls = [
    #         path('refresh/', self.admin_view(refresh_memcache), name="refresh"),
    #     ]
    #     return urls + my_urls


admin_site = DjangoBlogAdminSite(name='admin')

admin_site.register(Article, ArticlelAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(Links, LinksAdmin)
admin_site.register(SideBar, SideBarAdmin)
admin_site.register(BlogSettings, BlogSettingsAdmin)

admin_site.register(commands, CommandsAdmin)
admin_site.register(EmailSendLog, EmailSendLogAdmin)

admin_site.register(BlogUser, BlogUserAdmin)

admin_site.register(Comment, CommentAdmin)

admin_site.register(OAuthUser, OAuthUserAdmin)
admin_site.register(OAuthConfig, OAuthConfigAdmin)

admin_site.register(Site, SiteAdmin)

admin_site.register(LogEntry, LogEntryAdmin)
