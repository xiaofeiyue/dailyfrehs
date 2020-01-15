from django.conf.urls import url

from apps.areas.views import  AreasView


urlpatterns = [

    url(r'^areas/$',AreasView.as_view(),name='area'),


]




