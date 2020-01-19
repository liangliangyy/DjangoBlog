#!/usr/bin/env python

from DjangoBlog.utils import send_email
from DjangoBlog.utils import get_current_site_domain, render_template
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_comment_email(comment):
  site = get_current_site_domain()
  article_url = "http://{site}{path}".format(site=site, path=comment.article.get_absolute_url())
  article_title = comment.article.title
  comment_url = "{}#div-comment-{}".format(article_url, comment.id)
  comment_text = comment.body
  tomail = comment.author.email
  username = comment.author.username
  content = render_template('new_comment.j2', vars=locals())

  if content is not None:
    send_email(emailto=[tomail],
               title='Спасибо за Ваш комментарий',
               content=content,
               images={"logo.png": "image/png", "comment_icon.png": "image/png"})

  try:
    if comment.parent_comment:
      parent_comment_username = comment.parent_comment.author.username
      parent_comment_url = "{}#div-comment-{}".format(article_url, comment.parent_comment.id)
      tomail = comment.parent_comment.author.email
      content = render_template('new_comment_reply.j2', vars=locals())
      if content is not None:
        send_email(emailto=[tomail],
                   title='Новый ответ на Ваш комментарий',
                   content=content,
                   images={"logo.png": "image/png", "comment_reply_icon.png": "image/png"})
  except Exception as e:
    logger.error(e)
