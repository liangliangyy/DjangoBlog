from django.conf.urls import url
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "accounts"

urlpatterns = [url(r'^login/$',
                   views.LoginView.as_view(success_url='/'),
                   name='login',
                   kwargs={'authentication_form': LoginForm}),
               url(r'^register/$',
                   views.RegisterView.as_view(success_url="/"),
                   name='register'),
               url(r'^logout/$',
                   views.LogoutView.as_view(),
                   name='logout'),
               path(r'account/result.html',
                    views.account_result,
                    name='result'),
               url(r'^forget_password/$',
                   views.ForgetPasswordView.as_view(),
                   name='forget_password'),
               url(r'^forget_password_code/$',
                   views.ForgetPasswordEmailCode.as_view(),
                   name='forget_password_code'),
               ]
