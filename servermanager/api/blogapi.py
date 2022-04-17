from haystack.query import SearchQuerySet

from blog.models import Article, Category


class BlogApi():
    def __init__(self):
        self.searchqueryset = SearchQuerySet()
        self.searchqueryset.auto_query('')
        self.__max_takecount__ = 8

    def search_articles(self, query):
        sqs = self.searchqueryset.auto_query(query)
        sqs = sqs.load_all()
        return sqs[:self.__max_takecount__]

    def get_category_lists(self):
        return Category.objects.all()

    def get_category_articles(self, categoryname):
        articles = Article.objects.filter(category__name=categoryname)
        if articles:
            return articles[:self.__max_takecount__]
        return None

    def get_recent_articles(self):
        return Article.objects.all()[:self.__max_takecount__]
