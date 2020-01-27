#!/usr/bin/env python
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from DjangoBlog.settings import SITE_DOMAIN_NAME, SITE_ID
import logging


class Command(BaseCommand):
    help = 'Changes the default example.com to the one specified in environment variables'

    def handle(self, *args, **options):
        obj, created = Site.objects.get_or_create(
            pk=SITE_ID,
            defaults={
                "domain": SITE_DOMAIN_NAME,
                "name": SITE_DOMAIN_NAME
            }
        )
        if not created:
            obj.domain = SITE_DOMAIN_NAME
            obj.name = SITE_DOMAIN_NAME
            obj.save()
        logging.info("Site has been changed to %s" % SITE_DOMAIN_NAME)
