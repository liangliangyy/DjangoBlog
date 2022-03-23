from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, NoReverseMatch
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import pgettext_lazy, gettext_lazy  as _

action_names = {
    ADDITION: pgettext_lazy('logentry_admin:action_type', 'Addition'),
    DELETION: pgettext_lazy('logentry_admin:action_type', 'Deletion'),
    CHANGE: pgettext_lazy('logentry_admin:action_type', 'Change'),
}


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    readonly_fields = ([f.name for f in LogEntry._meta.fields] +
                       ['object_link', 'action_description', 'user_link',
                        'get_change_message'])

    fieldsets = (
        (_('Metadata'), {
            'fields': (
                'action_time',
                'user_link',
                'action_description',
                'object_link',
            )
        }),
        (_('Details'), {
            'fields': (
                'get_change_message',
                'content_type',
                'object_id',
                'object_repr',
            )
        }),
    )

    list_filter = [
        'content_type'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display_links = [
        'action_time',
        'get_change_message',
    ]
    list_display = [
        'action_time',
        'user_link',
        'content_type',
        'object_link',
        'action_description',
        'get_change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return (
                       request.user.is_superuser or
                       request.user.has_perm('admin.change_logentry')
               ) and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        object_link = escape(obj.object_repr)
        content_type = obj.content_type

        if obj.action_flag != DELETION and content_type is not None:
            # try returning an actual link instead of object repr string
            try:
                url = reverse(
                    'admin:{}_{}_change'.format(content_type.app_label,
                                                content_type.model),
                    args=[obj.object_id]
                )
                object_link = '<a href="{}">{}</a>'.format(url, object_link)
            except NoReverseMatch:
                pass
        return mark_safe(object_link)

    object_link.admin_order_field = 'object_repr'
    object_link.short_description = _('object')

    def user_link(self, obj):
        content_type = ContentType.objects.get_for_model(type(obj.user))
        user_link = escape(force_str(obj.user))
        try:
            # try returning an actual link instead of object repr string
            url = reverse(
                'admin:{}_{}_change'.format(content_type.app_label,
                                            content_type.model),
                args=[obj.user.pk]
            )
            user_link = '<a href="{}">{}</a>'.format(url, user_link)
        except NoReverseMatch:
            pass
        return mark_safe(user_link)

    user_link.admin_order_field = 'user'
    user_link.short_description = _('user')

    def get_queryset(self, request):
        queryset = super(LogEntryAdmin, self).get_queryset(request)
        return queryset.prefetch_related('content_type')

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def action_description(self, obj):
        return action_names[obj.action_flag]

    action_description.short_description = _('action')

    def get_change_message(self, obj):
        return obj.get_change_message()

    get_change_message.short_description = _('change message')
