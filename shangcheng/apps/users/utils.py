import re
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render

from apps.users.models import User


class UsernameMobileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # username 有可能是手机号也有可能是用户名
        # 如果是username满足手机号的规则则我们就认为它手机号登录
        try:
            if re.match(r'1[3-9]\d{9}',username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username= username)
        except User.DoesNotExist:
            return render(request,'register.html')


       # 在判断密码是否正确
        if user.check_password(password) and self.user_can_authenticate(user):
            return user