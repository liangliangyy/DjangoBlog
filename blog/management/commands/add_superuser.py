#!/usr/bin/env python
"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from accounts.models import BlogUser
from DjangoBlog.settings import DJANGO_SU_NAME, DJANGO_SU_EMAIL, DJANGO_SU_PASSWORD
import logging


class Command(BaseCommand):
    help = 'Creates a super user using environemnt variables'

    def handle(self, *args, **options):
        try:
            superuser = BlogUser.objects.get(is_superuser=True)
        except ObjectDoesNotExist as err:
            logging.error("Could not query a superuser: {0}".format(err))
            superuser = BlogUser.objects.create_superuser(username=DJANGO_SU_NAME, email=DJANGO_SU_EMAIL, password=DJANGO_SU_PASSWORD)
            superuser.save()
            logging.info("Superuser created")
