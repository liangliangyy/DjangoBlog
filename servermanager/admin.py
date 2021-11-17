from django.contrib import admin
# Register your models here.


class CommandsAdmin(admin.ModelAdmin):
    list_display = ('title', 'command', 'describe')


class EmailSendLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'emailto', 'send_result', 'created_time')
    readonly_fields = (
        'title',
        'emailto',
        'send_result',
        'created_time',
        'content')

    def has_add_permission(self, request):
        return False
