import re
from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from pymysql import DatabaseError

from apps.users.models import User


class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')
    def post(self,request):
        data = request.POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseBadRequest('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')
        # 保存注册数据
        try:
            user = User.objects.create_user(username=username,
                                            password=password,
                                            mobile = mobile
                                            )
        except Exception as e:
            import logging
            logger = logging.getLogger('django')
            logger.error(e)
            return render(request, 'register.html', {'register_errmsg': '注册失败'})



        # 使用django再带的login实现状态保持
        login(request,user)
        # 响应注册结果
        # return http.HttpResponse('注册成功，重定向到首页')

        # 登陆成功之后返回到首页
        return redirect(reverse('contents:index'))


# 判断用户名是否已经使用过了
class UsernameCountView(View):
    def get(self,request,username):
        """
        接受用户名
        根据用户名进行查询
        如果查询数量为1,说明已经存在
        如果查询数量为0,说明不存在

        :param request:
        :param username:
        :return:
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code':0,'errmsg':'ok','count':count})


class MobileCountView(View):

    def get(self,request,mobile):

        count=User.objects.filter(mobile=mobile).count()

        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


