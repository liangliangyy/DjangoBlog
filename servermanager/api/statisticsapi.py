from datetime import datetime, timedelta
from django.db.models import Count, Q
from blog.models import Article
from accounts.models import BlogUser


class StatisticsApi:
    def __init__(self):
        pass

    def get_monthly_articles(self):
        """获取本月发布的文章数量"""
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        
        count = Article.objects.filter(
            pub_time__gte=start_date,
            pub_time__lt=end_date,
            status='p'
        ).count()
        
        return {"month": today.strftime("%Y-%m"), "count": count}

    def get_articles_by_period(self, period):
        """根据时间段获取文章数量统计"""
        today = datetime.today()
        data = []
        
        if period == '7days':
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                count = Article.objects.filter(
                    pub_time__gte=date.replace(hour=0, minute=0, second=0, microsecond=0),
                    pub_time__lt=date.replace(hour=23, minute=59, second=59, microsecond=999999),
                    status='p'
                ).count()
                data.append({"date": date.strftime("%Y-%m-%d"), "count": count})
        elif period == '6months':
            for i in range(5, -1, -1):
                date = today - timedelta(days=30*i)
                month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = month.replace(month=month.month + 1) if month.month < 12 else month.replace(year=month.year + 1, month=1)
                count = Article.objects.filter(
                    pub_time__gte=month,
                    pub_time__lt=next_month,
                    status='p'
                ).count()
                data.append({"month": month.strftime("%Y-%m"), "count": count})
        elif period == '1year':
            for i in range(11, -1, -1):
                date = today - timedelta(days=30*i)
                month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = month.replace(month=month.month + 1) if month.month < 12 else month.replace(year=month.year + 1, month=1)
                count = Article.objects.filter(
                    pub_time__gte=month,
                    pub_time__lt=next_month,
                    status='p'
                ).count()
                data.append({"month": month.strftime("%Y-%m"), "count": count})
        
        return data

    def get_registrations_by_period(self, period):
        """根据时间段获取注册用户数量统计"""
        today = datetime.today()
        data = []
        
        if period == '7days':
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                count = BlogUser.objects.filter(
                    date_joined__gte=date.replace(hour=0, minute=0, second=0, microsecond=0),
                    date_joined__lt=date.replace(hour=23, minute=59, second=59, microsecond=999999)
                ).count()
                data.append({"date": date.strftime("%Y-%m-%d"), "count": count})
        elif period == '6months':
            for i in range(5, -1, -1):
                date = today - timedelta(days=30*i)
                month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = month.replace(month=month.month + 1) if month.month < 12 else month.replace(year=month.year + 1, month=1)
                count = BlogUser.objects.filter(
                    date_joined__gte=month,
                    date_joined__lt=next_month
                ).count()
                data.append({"month": month.strftime("%Y-%m"), "count": count})
        elif period == '1year':
            for i in range(11, -1, -1):
                date = today - timedelta(days=30*i)
                month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = month.replace(month=month.month + 1) if month.month < 12 else month.replace(year=month.year + 1, month=1)
                count = BlogUser.objects.filter(
                    date_joined__gte=month,
                    date_joined__lt=next_month
                ).count()
                data.append({"month": month.strftime("%Y-%m"), "count": count})
        
        return data

    def get_active_users_by_period(self, period):
        """根据时间段获取活跃用户数量统计"""
        today = datetime.today()
        data = []
        
        if period == '7days':
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                # 活跃用户定义：发布过文章或评论过的用户
                active_users = BlogUser.objects.filter(
                    Q(article__pub_time__gte=start_date, article__pub_time__lt=end_date, article__status='p') |
                    Q(comment__created_time__gte=start_date, comment__created_time__lt=end_date, comment__is_enable=True)
                ).distinct().count()
                
                data.append({"date": date.strftime("%Y-%m-%d"), "count": active_users})
        elif period == '6months':
            for i in range(5, -1, -1):
                date = today - timedelta(days=30*i)
                month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = month.replace(month=month.month + 1) if month.month < 12 else month.replace(year=month.year + 1, month=1)
                
                active_users = BlogUser.objects.filter(
                    Q(article__pub_time__gte=month, article__pub_time__lt=next_month, article__status='p') |
                    Q(comment__created_time__gte=month, comment__created_time__lt=next_month, comment__is_enable=True)
                ).distinct().count()
                
                data.append({"month": month.strftime("%Y-%m"), "count": active_users})
        elif period == '1year':
            for i in range(11, -1, -1):
                date = today - timedelta(days=30*i)
                month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = month.replace(month=month.month + 1) if month.month < 12 else month.replace(year=month.year + 1, month=1)
                
                active_users = BlogUser.objects.filter(
                    Q(article__pub_time__gte=month, article__pub_time__lt=next_month, article__status='p') |
                    Q(comment__created_time__gte=month, comment__created_time__lt=next_month, comment__is_enable=True)
                ).distinct().count()
                
                data.append({"month": month.strftime("%Y-%m"), "count": active_users})
        
        return data