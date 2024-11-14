import geoip2.database
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import os 
from django.http import HttpResponse
import logging
"""
    解析ip地址来自哪个国家的代码

112.250.105.164

import geoip2.database

# 指定GeoLite2-Country.mmdb文件的路径
reader = geoip2.database.Reader('GeoLite2-Country.mmdb')

# 查询特定IP地址的国家信息
response = reader.country('128.101.101.101')

# 打印查询结果
print('IP地址:', response.ip_address)
print('国家代码:', response.country.iso_code)
print('国家名称:', response.country.name)

# 关闭数据库读取器
reader.close()
"""


class LogIPMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        # 在请求处理之前做一些操作
        #response = self.get_response(request)
        logger=logging.getLogger(__name__)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address=None
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
            #print(ip_address)
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            #print("来自",ip_address,"的请求")
        #print("设置路径",settings.GEOIP_DATABASE)
        #print("系统当前路径",os.path.dirname(settings.BASE_DIR))
        #GeoLite2-Country.mmdb
        #GeoLite2-City.mmdb
        #datapath=os.path.join(os.path.dirname(settings.BASE_DIR), "GeoLite2-Country.mmdb")
        #print(os.path.join(os.path.dirname(settings.BASE_DIR), "test.log"))
        mm_db = geoip2.database.Reader(settings.GEOIP_DATABASE)
        mm_db_city =geoip2.database.Reader(settings.GEOIP_DATABASE2)
        #print("数据库路径",mm_db)
        try:
            response = mm_db.country(ip_address)
            response2=mm_db_city.city(ip_address)
            print(response.country.name)
            country = response.country.name
            city=response2.city.name
            # 可以记录到日志或使用其他方式
            #log.waring("查询ip开始")
            print(f"IP: {ip_address}, Country: {country}")
            logger.info(f"来自IP:{ip_address},Country:{country},city {city} 的请求")
        except Exception as e:
            print(f"Error querying GeoIP: {e}")
            city, country = 'Unknown', 'Unknown'

        # 将地理位置信息附加到request对象，供后续使用
        request.ip_info = {
            'city': city,
            'country': country
        }
        # 在请求处理之后做一些操作"""
        #return response
        response = self.get_response(request)
        return response
    def process_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
            print(ip_address)
        else:
            ip_address = request.META.get('REMOTE_ADDR')
 
        # 查询IP地址的地理位置
        print("地图数据库路径",mm_db)
        mm_db = geoip2.database.Reader(settings.GEOIP_DATABASE)
        print("地图数据库路径",mm_db)
        try:
            response = mm_db.country(ip_address)
            city = response.country.name
            country = response.country.name
            # 可以记录到日志或使用其他方式
            #log.waring("查询ip开始")
            print(f"IP: {ip_address}, City: {city}, Country: {country}")
        except Exception as e:
            print(f"Error querying GeoIP: {e}")
            city, country = 'Unknown', 'Unknown'
 
        # 将地理位置信息附加到request对象，供后续使用
        request.ip_info = {
            'city': city,
            'country': country
        }
