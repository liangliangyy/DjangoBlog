from django.contrib import admin

# Register your models here.
from .models import OAuthUser


class OAuthUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'nikename', 'type', 'picture', 'email',)
    list_display_links = ('id', 'nikename')
    list_filter = ('author', 'type',)


admin.site.register(OAuthUser, OAuthUserAdmin)
"""
author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', blank=True, null=True)
    openid = models.CharField(max_length=50)
    nikename = models.CharField(max_length=50, verbose_name='昵称')
    token = models.CharField(max_length=150)
    picture = models.CharField(max_length=350, blank=True, null=True)
    type = models.CharField(blank=False, null=False, max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True)
"""
