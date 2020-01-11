
from django.conf.urls import url

from apps.QQlogin import views

urlpatterns = [
    url(r'^qq/login/$',views.QQLoginView.as_view(),name='qqlogin'),
    url(r'^oauth_callback$',views.QQUserView.as_view(),name='qquser'),
]
