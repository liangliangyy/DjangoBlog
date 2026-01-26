import json
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.contrib.auth import get_user_model
from blog.models import Article
from comments.models import Comment

User = get_user_model()


class ArticleStatisticsView(View):
    """文章统计接口"""
    
    def get(self, request):
        """获取文章统计数据"""
        try:
            # 获取查询参数
            period = request.GET.get('period', 'month')  # month, week, year
            time_range = request.GET.get('range', '6')  # 6, 7, 12 (months/days/months)
            
            # 根据period和range计算时间范围
            now = timezone.now()
            
            if period == 'month':
                months = int(time_range)
                start_date = now - timedelta(days=months * 30)  # 近似计算
                # 按月份分组统计
                stats = Article.objects.filter(
                    pub_time__gte=start_date,
                    status='p'
                ).extra(
                    select={'month': "strftime('%%Y-%%m', pub_time)"}
                ).values('month').annotate(count=Count('id')).order_by('month')
                
            elif period == 'week':
                days = int(time_range)
                start_date = now - timedelta(days=days)
                # 按天分组统计
                stats = Article.objects.filter(
                    pub_time__gte=start_date,
                    status='p'
                ).extra(
                    select={'day': "strftime('%%Y-%%m-%%d', pub_time)"}
                ).values('day').annotate(count=Count('id')).order_by('day')
                
            elif period == 'year':
                years = int(time_range)
                start_date = now - timedelta(days=years * 365)
                # 按月份分组统计
                stats = Article.objects.filter(
                    pub_time__gte=start_date,
                    status='p'
                ).extra(
                    select={'month': "strftime('%%Y-%%m', pub_time)"}
                ).values('month').annotate(count=Count('id')).order_by('month')
            
            # 本月文章数量
            current_month = now.strftime('%Y-%m')
            current_month_count = Article.objects.filter(
                pub_time__gte=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                status='p'
            ).count()
            
            # 转换数据格式为前端需要的格式
            if period == 'week':
                data = {
                    'labels': [item['day'] for item in stats],
                    'values': [item['count'] for item in stats]
                }
            else:
                data = {
                    'labels': [item['month'] for item in stats],
                    'values': [item['count'] for item in stats]
                }
            
            return JsonResponse({
                'success': True,
                'data': data,
                'current_month_count': current_month_count,
                'period': period,
                'range': time_range
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class UserStatisticsView(View):
    """用户统计接口"""
    
    def get(self, request):
        """获取用户注册统计数据"""
        try:
            # 获取查询参数
            period = request.GET.get('period', 'month')  # month, week, year
            time_range = request.GET.get('range', '6')  # 6, 7, 12 (months/days/months)
            
            # 根据period和range计算时间范围
            now = timezone.now()
            
            if period == 'month':
                months = int(time_range)
                start_date = now - timedelta(days=months * 30)  # 近似计算
                # 按月份分组统计
                stats = User.objects.filter(
                    date_joined__gte=start_date
                ).extra(
                    select={'month': "strftime('%%Y-%%m', date_joined)"}
                ).values('month').annotate(count=Count('id')).order_by('month')
                
            elif period == 'week':
                days = int(time_range)
                start_date = now - timedelta(days=days)
                # 按天分组统计
                stats = User.objects.filter(
                    date_joined__gte=start_date
                ).extra(
                    select={'day': "strftime('%%Y-%%m-%%d', date_joined)"}
                ).values('day').annotate(count=Count('id')).order_by('day')
                
            elif period == 'year':
                years = int(time_range)
                start_date = now - timedelta(days=years * 365)
                # 按月份分组统计
                stats = User.objects.filter(
                    date_joined__gte=start_date
                ).extra(
                    select={'month': "strftime('%%Y-%%m', date_joined)"}
                ).values('month').annotate(count=Count('id')).order_by('month')
            
            # 转换数据格式为前端需要的格式
            if period == 'week':
                data = {
                    'labels': [item['day'] for item in stats],
                    'values': [item['count'] for item in stats]
                }
            else:
                data = {
                    'labels': [item['month'] for item in stats],
                    'values': [item['count'] for item in stats]
                }
            
            return JsonResponse({
                'success': True,
                'data': data,
                'period': period,
                'range': time_range
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ActiveUserStatisticsView(View):
    """活跃用户统计接口"""
    
    def get(self, request):
        """获取活跃用户统计数据"""
        try:
            # 获取查询参数
            period = request.GET.get('period', 'month')  # month, week, year
            time_range = request.GET.get('range', '6')  # 6, 7, 12 (months/days/months)
            
            # 根据period和range计算时间范围
            now = timezone.now()
            
            if period == 'month':
                months = int(time_range)
                start_date = now - timedelta(days=months * 30)  # 近似计算
                # 按月份分组统计活跃用户（有文章或评论的用户）
                stats = []
                for i in range(months):
                    month_start = (now - timedelta(days=(months-i) * 30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
                    
                    # 统计这个月的活跃用户（发表文章或评论的用户）
                    active_users = User.objects.filter(
                        Q(article__pub_time__range=[month_start, month_end]) |
                        Q(comment__creation_time__range=[month_start, month_end])
                    ).distinct().count()
                    
                    stats.append({
                        'month': month_start.strftime('%Y-%m'),
                        'count': active_users
                    })
                
            elif period == 'week':
                days = int(time_range)
                # 按天分组统计活跃用户
                stats = []
                for i in range(days):
                    day_start = (now - timedelta(days=days-i-1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
                    
                    # 统计这一天的活跃用户
                    active_users = User.objects.filter(
                        Q(article__pub_time__range=[day_start, day_end]) |
                        Q(comment__creation_time__range=[day_start, day_end])
                    ).distinct().count()
                    
                    stats.append({
                        'day': day_start.strftime('%Y-%m-%d'),
                        'count': active_users
                    })
                
            elif period == 'year':
                years = int(time_range)
                # 按月份分组统计活跃用户
                stats = []
                for i in range(years * 12):
                    month_start = (now - timedelta(days=(years*12-i) * 30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
                    
                    # 统计这个月的活跃用户
                    active_users = User.objects.filter(
                        Q(article__pub_time__range=[month_start, month_end]) |
                        Q(comment__creation_time__range=[month_start, month_end])
                    ).distinct().count()
                    
                    stats.append({
                        'month': month_start.strftime('%Y-%m'),
                        'count': active_users
                    })
            
            # 转换数据格式为前端需要的格式
            if period == 'week':
                data = {
                    'labels': [item['day'] for item in stats],
                    'values': [item['count'] for item in stats]
                }
            else:
                data = {
                    'labels': [item['month'] for item in stats],
                    'values': [item['count'] for item in stats]
                }
            
            return JsonResponse({
                'success': True,
                'data': data,
                'period': period,
                'range': time_range
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)