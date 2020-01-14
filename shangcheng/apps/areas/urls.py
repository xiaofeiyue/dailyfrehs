from django.conf.urls import url

from apps.areas.views import AddressView

urlpatterns = [
    url(r'^areas/$',AddressView.as_view(),name='address')
]
