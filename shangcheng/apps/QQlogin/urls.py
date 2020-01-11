
from django.conf.urls import url

from apps.QQlogin import views

urlpatterns = [
    url(r'^qq/login/$',views.QQLoginView.as_view(),name='qqlogin'),
]
