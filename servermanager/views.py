# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from servermanager.api.statisticsapi import StatisticsApi


@csrf_exempt
def statistics_view(request):
    """统计数据API接口"""
    stats_api = StatisticsApi()
    
    if request.method == 'GET':
        stat_type = request.GET.get('type')
        period = request.GET.get('period')
        
        if stat_type == 'monthly_articles':
            result = stats_api.get_monthly_articles()
            return JsonResponse(result, safe=False)
        elif stat_type == 'articles':
            if period in ['7days', '6months', '1year']:
                result = stats_api.get_articles_by_period(period)
                return JsonResponse(result, safe=False)
            else:
                return JsonResponse({"error": "Invalid period parameter"}, status=400)
        elif stat_type == 'registrations':
            if period in ['7days', '6months', '1year']:
                result = stats_api.get_registrations_by_period(period)
                return JsonResponse(result, safe=False)
            else:
                return JsonResponse({"error": "Invalid period parameter"}, status=400)
        elif stat_type == 'active_users':
            if period in ['7days', '6months', '1year']:
                result = stats_api.get_active_users_by_period(period)
                return JsonResponse(result, safe=False)
            else:
                return JsonResponse({"error": "Invalid period parameter"}, status=400)
        else:
            return JsonResponse({"error": "Invalid type parameter"}, status=400)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
