# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from blog.models import Article, Category
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# 创建测试分类
category, _ = Category.objects.get_or_create(name='测试分类')

# 创建测试用户
user, _ = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})

# 创建一些测试文章
for i in range(10):
    Article.objects.get_or_create(
        title='测试文章{}'.format(i+1),
        defaults={
            'body': '这是测试文章{}的内容'.format(i+1),
            'author': user,
            'category': category,
            'pub_time': timezone.now() - timedelta(days=i*5),
            'status': 'p'
        }
    )

print('测试数据创建完成')