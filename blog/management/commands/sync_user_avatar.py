import requests
from django.core.management.base import BaseCommand
from django.templatetags.static import static

from djangoblog.utils import save_user_avatar
from oauth.models import OAuthUser
from oauth.oauthmanager import get_manager_by_type


class Command(BaseCommand):
    help = 'sync user avatar'

    def test_picture(self, url):
        try:
            if requests.get(url, timeout=2).status_code == 200:
                return True
        except:
            pass

    def handle(self, *args, **options):
        static_url = static("../")
        users = OAuthUser.objects.all()
        self.stdout.write(f'开始同步{len(users)}个用户头像')
        for u in users:
            self.stdout.write(f'开始同步:{u.nickname}')
            url = u.picture
            if url:
                if url.startswith(static_url):
                    if self.test_picture(url):
                        continue
                    else:
                        if u.metadata:
                            manage = get_manager_by_type(u.type)
                            url = manage.get_picture(u.metadata)
                            url = save_user_avatar(url)
                        else:
                            url = static('blog/img/avatar.png')
                else:
                    url = save_user_avatar(url)
            else:
                url = static('blog/img/avatar.png')
            if url:
                self.stdout.write(
                    f'结束同步:{u.nickname}.url:{url}')
                u.picture = url
                u.save()
        self.stdout.write('结束同步')
