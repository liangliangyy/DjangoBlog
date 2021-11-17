from django.core.management.base import BaseCommand

from blog.documents import ElapsedTimeDocument, ArticleDocumentManager, ElaspedTimeDocumentManager, \
    ELASTICSEARCH_ENABLED


# TODO 参数化
class Command(BaseCommand):
    help = 'build search index'

    def handle(self, *args, **options):
        if ELASTICSEARCH_ENABLED:
            ElaspedTimeDocumentManager.build_index()
            manager = ElapsedTimeDocument()
            manager.init()
            manager = ArticleDocumentManager()
            manager.delete_index()
            manager.rebuild()
