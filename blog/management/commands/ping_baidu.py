from django.core.management.base import BaseCommand

from djangoblog.spider_notify import SpiderNotify
from djangoblog.utils import get_current_site
from blog.models import Article, Tag, Category

site = get_current_site().domain


class Command(BaseCommand):
    help = 'notify baidu url'

    def add_arguments(self, parser):
        parser.add_argument(
            'data_type',
            type=str,
            choices=[
                'all',
                'article',
                'tag',
                'category'],
            help='article : all article,tag : all tag,category: all category,all: All of these')

    def get_full_url(self, path):
        url = "https://{site}{path}".format(site=site, path=path)
        return url

    def handle(self, *args, **options):
        type = options['data_type']
        self.stdout.write('start get %s' % type)

        urls = []
        if type == 'article' or type == 'all':
            for article in Article.objects.filter(status='p'):
                urls.append(article.get_full_url())
        if type == 'tag' or type == 'all':
            for tag in Tag.objects.all():
                url = tag.get_absolute_url()
                urls.append(self.get_full_url(url))
        if type == 'category' or type == 'all':
            for category in Category.objects.all():
                url = category.get_absolute_url()
                urls.append(self.get_full_url(url))

        self.stdout.write(
            self.style.SUCCESS(
                'start notify %d urls' %
                len(urls)))
        SpiderNotify.baidu_notify(urls)
        self.stdout.write(self.style.SUCCESS('finish notify'))
