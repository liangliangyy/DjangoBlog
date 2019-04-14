#!/usr/bin/env python
# encoding: utf-8
"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: elasticsearch_backend.py
@time: 2019-04-13 11:46
"""
import logging
import re
import json

from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.utils.datetime_safe import datetime
from django.utils.encoding import force_text

from elasticsearch_dsl import Q

from haystack.backends import BaseEngine, BaseSearchBackend, BaseSearchQuery, EmptyResults, log_query
from haystack.constants import DJANGO_CT, DJANGO_ID, ID
from haystack.exceptions import MissingDependency, SearchBackendError, SkipDocument
from haystack.inputs import Clean, Exact, PythonData, Raw
from haystack.models import SearchResult
from haystack.utils import log as logging
from haystack.utils import get_identifier, get_model_ct
from haystack.utils.app_loading import haystack_get_model
from django_elasticsearch_dsl.registries import registry

from blog.models import Article
from blog.documents import ArticleDocument

logger = logging.getLogger(__name__)

DATETIME_REGEX = re.compile(
    '^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.\d{3,6}Z?)?$')


class ElasticSearchBackend(BaseSearchBackend):

    def _get_models(self):
        models = registry.get_models()
        return set(models)

    def _create(self, models):
        for index in registry.get_indices(models):
            index.create()

    def _populate(self, models):
        for doc in registry.get_documents(models):
            qs = doc().get_queryset()
            doc().update(qs)

    def _delete(self, models):
        for index in registry.get_indices(models):
            index.delete(ignore=404)
        return True

    def _rebuild(self, models):
        if not self._delete(models):
            return

        self._create(models)
        self._populate(models)

    def update(self, index, iterable, commit=True):
        models = self._get_models()
        # self._rebuild(models)

    def remove(self, obj_or_string):
        models = self._get_models()
        self._delete(models)

    def clear(self, models=None, commit=True):
        self.remove(None)

    @log_query
    def search(self, query_string, **kwargs):
        logger.info('search query_string:' + query_string)

        start_offset = kwargs.get('start_offset')
        end_offset = kwargs.get('end_offset')

        q = Q('bool',
              must=[Q('match', body=query_string)],
              minimum_should_match="70%"
              )

        search = ArticleDocument.search() \
                     .query('bool', filter=[q]) \
                     .filter('term', status='p') \
                     .filter('term', type='a') \
                     .source(False)[start_offset: end_offset]

        results = search.execute()
        hits = results['hits'].total
        raw_results = []
        for raw_result in results['hits']['hits']:
            app_label = 'blog'
            model_name = 'Article'
            additional_fields = {}

            # if 'highlight' in raw_result:
            #     additional_fields['highlighted'] = raw_result['highlight'].get(content_field, '')

            result_class = SearchResult

            result = result_class(app_label, model_name, raw_result['_id'], raw_result['_score'],
                                  **additional_fields)
            raw_results.append(result)
        facets = {}
        spelling_suggestion = None
        return {
            'results': raw_results,
            'hits': hits,
            'facets': facets,
            'spelling_suggestion': spelling_suggestion,
        }

    def _from_python(self, value):
        """
        Converts Python values to a string for Whoosh.

        Code courtesy of pysolr.
        """
        if hasattr(value, 'strftime'):
            if not hasattr(value, 'hour'):
                value = datetime(value.year, value.month, value.day, 0, 0, 0)
        elif isinstance(value, bool):
            if value:
                value = 'true'
            else:
                value = 'false'
        elif isinstance(value, (list, tuple)):
            value = u','.join([force_text(v) for v in value])
        elif isinstance(value, (six.integer_types, float)):
            # Leave it alone.
            pass
        else:
            value = force_text(value)
        return value

    def _to_python(self, value):
        """
        Converts values from Whoosh to native Python values.

        A port of the same method in pysolr, as they deal with data the same way.
        """
        if value == 'true':
            return True
        elif value == 'false':
            return False

        if value and isinstance(value, six.string_types):
            possible_datetime = DATETIME_REGEX.search(value)

            if possible_datetime:
                date_values = possible_datetime.groupdict()

                for dk, dv in date_values.items():
                    date_values[dk] = int(dv)

                return datetime(date_values['year'], date_values['month'], date_values['day'], date_values['hour'],
                                date_values['minute'], date_values['second'])

        try:
            # Attempt to use json to load the values.
            converted_value = json.loads(value)

            # Try to handle most built-in types.
            if isinstance(converted_value, (list, tuple, set, dict, six.integer_types, float, complex)):
                return converted_value
        except:
            # If it fails (SyntaxError or its ilk) or we don't trust it,
            # continue on.
            pass

        return value


class ElasticSearchQuery(BaseSearchQuery):
    def _convert_datetime(self, date):
        if hasattr(date, 'hour'):
            return force_text(date.strftime('%Y%m%d%H%M%S'))
        else:
            return force_text(date.strftime('%Y%m%d000000'))

    def clean(self, query_fragment):
        """
        Provides a mechanism for sanitizing user input before presenting the
        value to the backend.

        Whoosh 1.X differs here in that you can no longer use a backslash
        to escape reserved characters. Instead, the whole word should be
        quoted.
        """
        words = query_fragment.split()
        cleaned_words = []

        for word in words:
            if word in self.backend.RESERVED_WORDS:
                word = word.replace(word, word.lower())

            for char in self.backend.RESERVED_CHARACTERS:
                if char in word:
                    word = "'%s'" % word
                    break

            cleaned_words.append(word)

        return ' '.join(cleaned_words)

    def build_query_fragment(self, field, filter_type, value):
        return value.query_string


class ElasticSearchEngine(BaseEngine):
    backend = ElasticSearchBackend
    query = ElasticSearchQuery
