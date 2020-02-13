import json
import urllib
import urllib.request
import requests
import time
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

def auth(code):
    """Функция получает значения code для получения ключа доступа. Затем при помощи
    значения code сервер приложения получает ключ доступа access_token для доступа к API ВКонтакте.
    Далее при помощи API ВКонтакте получает имя авторизованного пользователя и список из 5 его друзей,
    выбранных в произвольном порядке. Функция возвращает сообщение с именем авторизованного
    пользователя и списком из 5 его друзей"""
    request_link = 'https://oauth.vk.com/access_token?client_id=%s&client_secret=%s&redirect_uri=http://i-empire.ru/vk_auth/final/&code=%s' % (settings.VK_APP_ID, settings.VK_SECURITY_KEY, code)
    logger.info(code)

    # https: // oauth.vk.com / access_token?client_id = 1 & client_secret = H2Pk8htyFD8024mZaPHm & redirect_uri = http: // mysite.ru & code = 7
    # a6fa4dff77a228eeda56603b8f53806c883f011c40b72630bb50df056f6479e52a
    #
    try:
        r = requests.get(url=request_link) # через API запрос получаем словарь в формате JSON
    except Exception as e:
        error_report =  "<h1 style='color:blue'>Сервер ВКонтакте временно недоступен. Повторите попытку позже. </h1>"
        return error_report

    # logger.info(r.json())
    data = r.json()
    logger.info(data)
    access_token = data['access_token']
    request_link = "https://api.vk.com/method/users.get?user_ids=%s&fields=bdate,photo_max&access_token=%s&v=5.101" % (data['user_id'], access_token)
    try:
        r = requests.get(url=request_link) # через API запрос получаем словарь в формате JSON
    except Exception as e:
        error_report =  "<h1 style='color:blue'>Сервер ВКонтакте временно недоступен. Повторите попытку позже. </h1>"
        return error_report
    data = r.json()
    logger.info(data)
    first_name = data['response'][0]['first_name'] # получаем имя авторизованного пользователя
    last_name = data['response'][0]['last_name'] # получаем фамилию авторизованного пользователя
    greeting_string = 'Здравствуйте, %s %s, вы авторизованы. <br>' % (first_name, last_name)

    request_link = "https://api.vk.com/method/friends.get?order=random&count=5&access_token=%s&v=5.101 " % access_token # создаем запрос на 5 друзей, выбранных в случайном порядке
    try:
        r = requests.get(url=request_link) # через API запрос получаем словарь в формате JSON
    except Exception as e:
        error_report =  "<h1 style='color:blue'>Сервер ВКонтакте временно недоступен. Повторите попытку позже. </h1>"
        return error_report
    data = r.json()
    array_of_friends_ID = data['response']['items'] # получаем массив ID друзей
    amount_of_friends = len(array_of_friends_ID)
    if amount_of_friends == 0 :
        greeting_string += 'У вас нет друзей'
        return greeting_string
    elif amount_of_friends < 5 :
        greeting_string += 'У вас меньше 5 друзей: <br>'
        for i in range(amount_of_friends):  # создаем список друзей
            user_id = str(array_of_friends_ID[i])
            time.sleep(0.5)
            request_link = "https://api.vk.com/method/users.get?user_ids=%s&fields=bdate&access_token=%s&v=5.101" % (user_id, access_token)# создаем запрос на данные пользователя из "В Контакт" по его ID
            try:
                r = requests.get(url=request_link) # через API запрос получаем словарь в формате JSON
            except Exception as e:
                error_report =  "<h1 style='color:blue'>Сервер ВКонтакте временно недоступен. Повторите попытку позже. </h1>"
                return error_report
            data = r.json()
            temp_first_name = data['response'][0]['first_name']
            temp_last_name = data['response'][0]['last_name']
            temp_new_string = '{0} {1} \n'
            temp_new_string = temp_new_string.format(temp_first_name, temp_last_name)
            new_string = '<a href="https://vk.com/id{0}">{1}</a><br> '
            new_string = new_string.format(user_id, temp_new_string)
            greeting_string += new_string
        return greeting_string
    else:
        greeting_string += '5 друзей из вашего контакт листа, выбранных в случайном порядке: <br>'
        for i in range(amount_of_friends): # создаем список друзей
            user_id =str(array_of_friends_ID[i])
            time.sleep(0.5)
            request_link = "https://api.vk.com/method/users.get?user_ids={0}&fields=bdate&access_token={1}&v=5.101" # создаем запрос на данные пользователя из "В Контакт" по его ID
            request_link = request_link.format(user_id, access_token)
            try:
                r = requests.get(url=request_link) # через API запрос получаем словарь в формате JSON
            except Exception as e:
                error_report =  "<h1 style='color:blue'>Сервер ВКонтакте временно недоступен. Повторите попытку позже. </h1>"
                return error_report
            data = r.json()
            temp_first_name = data['response'][0]['first_name']
            temp_last_name = data['response'][0]['last_name']
            temp_new_string = '{0} {1} \n'
            temp_new_string = temp_new_string.format(temp_first_name, temp_last_name)
            new_string = '<a href="https://vk.com/id{0}">{1}</a><br> '
            new_string = new_string.format(user_id, temp_new_string)
            greeting_string += new_string

        return greeting_string