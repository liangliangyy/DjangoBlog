from django.shortcuts import render

# Create your views here.
import json
from itertools import groupby
from django.http import HttpResponse
from .models import OwnTrackLog
from DjangoBlog.utils import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import requests


@csrf_exempt
def manage_owntrack_log(request):
    try:
        s = json.loads(request.read().decode('utf-8'))
        tid = s['tid']
        lat = s['lat']
        lon = s['lon']

        logger.info('tid:{tid}.lat:{lat}.lon:{lon}'.format(tid=tid, lat=lat, lon=lon))
        if tid and lat and lon:
            m = OwnTrackLog()
            m.tid = tid
            m.lat = lat
            m.lon = lon
            m.save()
            return HttpResponse('ok')
        else:
            return HttpResponse('data error')
    except Exception as e:
        logger.warn(e)
        return HttpResponse('error')


@login_required
def show_maps(request):
    return render(request, 'owntracks/show_maps.html')


def convert_to_amap(locations):
    datas = ';'.join(map(lambda x: str(x.lon) + ',' + str(x.lat), locations))

    key = '8440a376dfc9743d8924bf0ad141f28e'
    api = 'http://restapi.amap.com/v3/assistant/coordinate/convert'
    query = {
        'key': key,
        'locations': datas,
        'coordsys': 'gps'
    }
    rsp = requests.get(url=api, params=query)
    logger.info(type(rsp.text))
    result = json.loads(rsp.text)
    return result['locations']


@login_required
def get_datas(request):
    models = OwnTrackLog.objects.all()
    result = list()
    if models and len(models):
        for tid, item in groupby(sorted(models, key=lambda k: k.tid), key=lambda k: k.tid):

            d = dict()
            d["name"] = tid
            paths = list()
            locations = convert_to_amap(item)
            for i in locations.split(';'):
                paths.append(i.split(','))
            d["path"] = paths
            result.append(d)
        return JsonResponse(result, safe=False)
