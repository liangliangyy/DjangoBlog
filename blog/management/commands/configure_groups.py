#!/usr/bin/env python
"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import ContentType
from accounts.models import BlogUser
import logging

GROUPS = ['new_users', 'devops', 'developers', 'qa', 'operators', 'product']
MODELS = ['logentry', 'permission', 'group', 'contenttype', 'session', 'site', 'blogsettings', 'links', 'sidebar', 'tag', 'category', 'article', 'bloguser', 'comment', 'commands', 'emailsendlog', 'comment']


class Command(BaseCommand):
    help = 'Creates read only default permission groups for users'

    def handle(self, *args, **options):
        for group in GROUPS:
            new_group, created = Group.objects.get_or_create(name=group)
            for model in MODELS:
                if group == 'devops':
                    permissions = ['add', 'change', 'delete', 'view']
                else:
                    permissions = ['view', ]
                for permission in permissions:
                    content_type = ContentType.objects.get(model=model)
                    codename = "%s_%s" % (permission, model)
                    name = 'Can {} {}'.format(permission, model)
                    logging.info("Creating permission for group %s; app %s; model: %s" % (group, content_type.app_label, codename))
                    try:
                        model_add_perm = Permission.objects.get(codename=codename, content_type=content_type)
                    except Permission.DoesNotExist:
                        logging.warning("Permission not found with name '{}'.".format(name))
                        continue

                    new_group.permissions.add(model_add_perm)
                    new_group.save()
                    logging.info("Created default group and permissions.")

        try:
            superuser = BlogUser.objects.get(is_superuser=True)
            my_group = Group.objects.get(name='devops')
            my_group.user_set.add(superuser)
            logging.info("Superuser has been added to devops group")
        except ObjectDoesNotExist as err:
            logging.error("Could not query a devops group: {0}".format(err))
