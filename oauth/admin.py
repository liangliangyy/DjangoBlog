from django.contrib import admin

# Register your models here.
from .models import OAuthUser


class OAuthUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'nikename', 'type', 'picture', 'email',)
    list_display_links = ('id', 'nikename')
    list_filter = ('author', 'type',)


admin.site.register(OAuthUser, OAuthUserAdmin)
