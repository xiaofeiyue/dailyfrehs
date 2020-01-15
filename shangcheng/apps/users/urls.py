
from django.conf.urls import url

from apps.users import views

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'^login/$',views.LoginView.as_view(),name='login'),
    url(r'^logout/$',views.LogoutView.as_view(),name='logout'),

    # 用户中心
    url(r'^user_center/$',views.UserCenterView.as_view(),name='user_center'),


    # 发送邮件
    url(r'^emails/$',views.EmailView.as_view(),name='email'),

    # 邮件激活
    url(r'^emails_active/$', views.EmailActiveView.as_view(), name='email_acctive'),



    # 用户中心的展示
    url(r'^address/$',views.UserAddressView.as_view(),name='address'),
]
