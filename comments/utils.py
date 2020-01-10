#!/usr/bin/env python

from DjangoBlog.utils import send_email
from DjangoBlog.utils import get_current_site
import logging

logger = logging.getLogger(__name__)


def send_comment_email(comment):
  site = get_current_site().domain
  subject = 'Спасибо за ваш комментарий'
  article_url = "https://{site}{path}".format(site=site, path=comment.article.get_absolute_url())
  html_content = """
                   <p>Комментарий доступен по ссылке:</p>
                   <a href="%s" rel="bookmark">%s</a>
                   <br />
                   Если ссылка выше не открывается，то копируй руками:
                   %s
                   """ % (article_url, comment.article.title, article_url)
  tomail = comment.author.email
  send_email([tomail], subject, html_content)
  try:
    if comment.parent_comment:
      html_content = """
                    Кто-то оценил <a href="%s" rel="bookmark">%s</a> вашу мысль <br/> %s <br/> Отгадай, кто!
                    <br/>
                    Если ссылка выше не открывается，то копируй руками:
                    %s
                    """ % (article_url, comment.article.title, comment.parent_comment.body, article_url)
      tomail = comment.parent_comment.author.email
      send_email([tomail], subject, html_content)
  except Exception as e:
    logger.error(e)
