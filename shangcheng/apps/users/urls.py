
from django.conf.urls import url

from apps.users import views

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'^login/$',views.LoginView.as_view(),name='login'),
]
