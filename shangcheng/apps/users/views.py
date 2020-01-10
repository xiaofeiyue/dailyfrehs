import re
from django import http
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
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
        # 判断短信验证码
        # 接受短信验证码参数
        sms_code_client = request.POST.get('sms_code')
        # 验证数据
        # 1.链接数据库
        redis_conn = get_redis_connection('code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 判断短信验证码是否过期
        if sms_code_server is None:
            return render(request,'register.html')
        if sms_code_client != sms_code_server.decode():
            return render(request,'register.html')
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






class LoginView(View):
    def get(self,request):
        return render(request,'login.html')

    def post(self,request):
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        # 登录之后跳转到首页还是个人中心有next决定
        next = request.GET.get('next')

        # 验证参数
        if not all([username,password,remembered]):
            return http.HttpResponseBadRequest('缺少参数')
        # 判断用户名是否符合规则
        if not re.match(r'[a-zA-Z0-9_-]{5,20}',username):
            return http.HttpResponseBadRequest("用户名不符合规则")


        # 判断密码是否符合规则
        if not re.match(r'[a-zA-Z0-9]{8,20}',password):
            return http.HttpResponseBadRequest('密码不符合规定')


        # 判断用户名和密码是否正确,使用django的后端认证
        # 认证登陆用户
        from django.contrib.auth import authenticate
        from django.contrib.auth.backends import ModelBackend
        user = authenticate(username=username,password = password)
        if user is None:
            return redirect(request,'login.html')

        # 实现状态保持
        login(request,user)


        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户,浏览器关闭回话就会结束
            request.session.set_expiry(0)
        else:
            # 记住用户,None默认两周后过期
            request.session.set_expiry(None)



        # is_authenticated是否是认证用户
        # request.user.is_authenticated

        """
        用户登录之后,返回到首页,上面应该显示用户,不应该显示登录
        我们用cookie去实现,如果是登录用户将用户名保存到cookie中,提取cookie中的信息,

        """
        """
        在首页如何用户没有登录点击到个人中心,会跳转到登录页面登录之后进入到
        个人中心,而不是首页,
        这里需要判断登录之后跳转到哪里,是首页还是个人中心
        跳转到个人中心的urlhttp://www.meiduo.site:8000/login/?next=/user_center/


        """
        if next:
            response = redirect(next)
        else:

            # 响应登录结果
            response =  redirect(reverse('contents:index'))
        response.set_cookie('username',user.username,max_age=3600)
        return response







class LogoutView(View):
    def get(self,request):


        """
        退出,就是删除状态保持的信息,然后重定向
        :param request:
        :return:
        """
        logout(request)

        # 还要删除cookie总的用户名

        # 跳转到首页
        response =  redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response




# 用户中心的展示

"""
登录用户才能进去,如果用户没有登录就跳转到登录页面
LoginrequiredMixin:可以帮助我们做用户的登录验证
如果没有登录,默认会跳转到account/login/
"""
from django.contrib.auth.mixins import LoginRequiredMixin
class UserCenterView(LoginRequiredMixin,View):
    def get(self,request):

        return render(request,'user_center_info.html')



"""
使用python manage.py shell 查看类视图的继承顺序
from apps.users.views import UserCenterView
>>> UserCenterView.__mro__
(<class 'apps.users.views.UserCenterView'>, <class 'django.contrib.auth.mixins.LoginRequiredMixin'>, <class 'django.contrib.auth.mixins.AccessMixin'>, <class 'django.views.generic.base.View'>, <class 'object'>)
>>>


"""