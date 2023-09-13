import logging

from django.utils.translation import gettext_lazy as _

from djangoblog.utils import get_current_site
from djangoblog.utils import send_email

logger = logging.getLogger(__name__)


def send_comment_email(comment):
    site = get_current_site().domain
    subject = _('Thanks for your comment')
    article_url = f"https://{site}{comment.article.get_absolute_url()}"
    html_content = _("""<p>Thank you very much for your comments on this site</p>
                    You can visit <a href="%(article_url)s" rel="bookmark">%(article_title)s</a>
                    to review your comments,
                    Thank you again!
                    <br />
                    If the link above cannot be opened, please copy this link to your browser.
                    %(article_url)s""") % {'article_url': article_url, 'article_title': comment.article.title}
    tomail = comment.author.email
    send_email([tomail], subject, html_content)
    try:
        if comment.parent_comment:
            html_content = _("""Your comment on <a href="%(article_url)s" rel="bookmark">%(article_title)s</a><br/> has 
                   received a reply. <br/> %(comment_body)s
                    <br/>   
                    go check it out!
                     <br/>
                     If the link above cannot be opened, please copy this link to your browser.
                     %(article_url)s
                    """) % {'article_url': article_url, 'article_title': comment.article.title,
                            'comment_body': comment.parent_comment.body}
            tomail = comment.parent_comment.author.email
            send_email([tomail], subject, html_content)
    except Exception as e:
        logger.error(e)
