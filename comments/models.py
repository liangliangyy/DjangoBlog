from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from blog.models import Article


# Create your models here.

class Comment(models.Model):
    body = models.TextField('正文', max_length=300)
    creation_time = models.DateTimeField(_('creation time'), default=now)
    last_modify_time = models.DateTimeField(_('last modify time'), default=now)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('author'),
        on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,
        verbose_name=_('article'),
        on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        'self',
        verbose_name=_('parent comment'),
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    is_enable = models.BooleanField(_('enable'),
                                    default=False, blank=False, null=False)

    class Meta:
        ordering = ['-id']
        verbose_name = _('comment')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
        indexes = [
            # 优化评论列表查询：article + parent_comment + is_enable组合索引
            models.Index(fields=['article', 'parent_comment', 'is_enable'], name='idx_art_parent_enable'),
            # 优化侧边栏评论查询：is_enable + id组合索引
            models.Index(fields=['is_enable', '-id'], name='idx_enable_id'),
        ]

    def __str__(self):
        return self.body

    def get_reactions_summary(self, user=None):
        """
        获取评论的 reactions 统计信息
        返回格式: {
            '👍': {
                'count': 5,
                'has_reacted': True,
                'users': ['Alice', 'Bob', 'Charlie']
            },
            '❤️': {'count': 3, 'has_reacted': False, 'users': [...]},
            ...
        }
        """
        from django.db.models import Count

        reactions = CommentReaction.objects.filter(
            comment=self
        ).values('reaction_type').annotate(count=Count('id'))

        result = {}
        for reaction in reactions:
            emoji = reaction['reaction_type']

            # 获取该 emoji 的所有点赞用户
            reaction_users = CommentReaction.objects.filter(
                comment=self,
                reaction_type=emoji
            ).select_related('user')[:10]  # 最多显示10个用户

            user_names = [r.user.nickname or r.user.username for r in reaction_users]

            result[emoji] = {
                'count': reaction['count'],
                'has_reacted': False,
                'users': user_names
            }

            if user and user.is_authenticated:
                result[emoji]['has_reacted'] = CommentReaction.objects.filter(
                    comment=self,
                    user=user,
                    reaction_type=emoji
                ).exists()

        return result


class CommentReaction(models.Model):
    """
    评论的 Emoji 反应/点赞
    """
    REACTION_CHOICES = [
        ('👍', 'thumbs_up'),
        ('👎', 'thumbs_down'),
        ('❤️', 'heart'),
        ('😄', 'laugh'),
        ('🎉', 'hooray'),
        ('😕', 'confused'),
        ('🚀', 'rocket'),
        ('👀', 'eyes'),
    ]

    comment = models.ForeignKey(
        Comment,
        verbose_name=_('comment'),
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        on_delete=models.CASCADE
    )
    reaction_type = models.CharField(
        _('reaction type'),
        max_length=10,
        choices=REACTION_CHOICES
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('comment reaction')
        verbose_name_plural = _('comment reactions')
        # 每个用户对同一评论的同一种 emoji 只能点一次
        unique_together = ['comment', 'user', 'reaction_type']
        indexes = [
            models.Index(fields=['comment', 'reaction_type'], name='idx_comment_reaction'),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.reaction_type} on comment {self.comment.id}'
