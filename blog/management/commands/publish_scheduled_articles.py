import logging

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from blog.models import Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _('Automatically publish articles whose scheduled publish time has passed')

    def handle(self, *args, **options):
        current_time = now()
        
        articles_to_publish = Article.objects.filter(
            status='d',
            scheduled_publish_time__isnull=False,
            scheduled_publish_time__lte=current_time
        )
        
        count = 0
        for article in articles_to_publish:
            article.status = 'p'
            article.pub_time = article.scheduled_publish_time
            article.save()
            count += 1
            logger.info(f'Published scheduled article: {article.title} (ID: {article.id})')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Published: {article.title} (ID: {article.id})'
                )
            )
        
        if count == 0:
            self.stdout.write(
                self.style.WARNING(_('No scheduled articles to publish at this time'))
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(_(f'Successfully published {count} scheduled article(s)'))
            )
        
        return count
