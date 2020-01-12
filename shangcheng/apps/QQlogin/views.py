import re
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.QQlogin.models import OAuthQQUser
from apps.users.models import User
from shangcheng import settings

"""
QQ登录步骤
1.申请成为开发者
2.创建应用
3.按照开发文档
    准备:1.appid,appkey
        QQ_client_ID = ''
        QQ_CLIENT_SECRET=''
        QQ_REDIRECT_URL=""
    2.放置QQ按钮
    3.拼接QQ按钮点击的url,根据文档进行拼接
        1.Step1：获取Authorization Code,就是拼接跳转的url
            请求地址：
            PC网站：https://graph.qq.com/oauth2.0/authorize
            请求方法：
            GET
            请求参数：
            http://www.meiduo.site:8000/oauth_callback?response_type=code&client_id=101518219&redirect_uri

            https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=test

            qq登录后跳转到http://www.meiduo.site:8000/oauth_callback?code=E43454076518F99615BF07A57874A2FA&state=test,

        2.Step2：通过Authorization Code获取Access Token
            请求地址：
            PC网站：https://graph.qq.com/oauth2.0/token
            请求方法：
            GET
            请求参数
https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=101518219&client_secret=418d84ebdc7241efb79536886ae95224&code=E43454076518F99615BF07A57874A2FA&redirect_uri=http://www.meiduo.site:8000/oauth_callback
    4.获取openid
        PC网站：https://graph.qq.com/oauth2.0/me
        2 请求方法
        GET
        openid是此网站上唯一对应用户身份的标识，网站可将此ID进行存储便于用户下次登录时辨识其身份，或将其与用户在网站上的原有账号进行绑定。

        QQ号和openid 一一对应


QQ登录总流程
1.拼接跳转的url
    最好将拼接的url一ajax的形式返回给前端
2.登录qq跳转之后的到一个code
3.用code 换取access token
4.用token换取openid

"""

class QQLoginView(View):
    def get(self,request):
        """
        使用QQLoginTool工具


        :param request:
        :return:
        """
        # 1.创建OAuthQQ对象
        #2.调用指定的方法获取指定数据
        state = 'wertyu'

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code':'ok','errmsg':'ok','login_url':login_url})




class QQUserView(View):
    def get(self,request):
        # 获取code
        code = request.GET.get('code')

        print(code)

        state = request.GET.get('state')
        if code is None:
            return http.HttpResponseBadRequest('参数缺失')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)

        token = oauth.get_access_token(code)
        print(token)

        openid = oauth.get_open_id(token)
        print(openid)
        """
        根据openid进行查询,
        如果查询有相应的记录,说明用户之间绑定过,直接登录
        如果查询没有记录,说明用户没有绑定,返回到绑定页面,实现绑定



        """
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 没有绑定,应该绑定
            return render(request, 'oauth_callback.html',context={'openid':openid})

        else:
            # 有记录走else:,没有异常走else

            # 设置登录状态,跳转到首页(重定向)
            login(request,qquser)

            response =  redirect(reverse('contents:index'))
            response.set_cookie('username',qquser.username,max_age=3600)




    def post(self,request):
        data = request.POST
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        openid = data.get('openid')
        if not all([mobile,password,sms_code,openid]):
            return http.HttpResponseBadRequest('缺少参数')

        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseBadRequest('手机号不符合规则')
        if not re.match(r'^[a-zA-Z0-9]{8,20}$',password):
            return http.HttpResponseBadRequest('密码不符合规则')

        # 判断短信验证码是否一致
        # 链接redis数据库
        redis_conn = get_redis_connection('code')
        redis_sms_code = redis_conn.get('sms_%s'%mobile)
        if redis_sms_code is None:
            return http.HttpResponseBadRequest('短信验证码过期')
        # redis中的数据为bytes类型
        if redis_sms_code.decode().lower() != sms_code.lower():
            return http.HttpResponseBadRequest('短信验证码不一致')

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号没有注册过创建用户
            user = User.objects.create_user(mobile=mobile,
                                     password=password,
                                     username=mobile)

        else:
            # 手机号注册过,验证密码是否正确
            if not user.check_password(password):
                return http.HttpResponseBadRequest('密码错误')
        # 绑定
        qquser = OAuthQQUser.objects.create(
            user  = user,
            openid =openid
        )
        # 设置登录状态
        login(request,user)

        # 设置cookie,跳转到首页的时候,不再显示登录,而是显示用户名



        # 重定向到首页
        response =  redirect(reverse('contents:index'))
        response.set_cookie('username',user.username,max_age=3600)
        return response







"""
绑定qq登录的业务逻辑    openid  和user

绑定页面没哟openid,openid在后端,所以将openid模板渲染的形式返回给前端


用户输入:
    手机号,密码,图片验证码,短信验证码

    手机号:如果这个手机号用户之前注册过,验证密码
    如果手机号没有注册过,就创建一个用户


前端收集用户输入信息
    :手机号.密码 短信验证码 以及openid

后端
    1.接受数据
    2.验证数据
    3.根据手机号判断用户是否注册过,
        如果注册过,验证密码是否正确
        如果没有注册过,创建新用户
    4.绑定用户信息和openid
    5.设置登录状态
    6.返回响应


用户信息和openid绑定

"""


###################################################
"""
itsdangerous 加密

"""
# 导入库
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from shangcheng import settings

# 2.创建实例对象
#secret_key, 秘钥    一般使用settings中的秘钥
#  expires_in=None 过期时间,默认3600

s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
# 3.组织数据
data = {
    'openid':'1234'
}

# 加密处理
token = s.dumps(data)
#b'eyJhbGciOiJIUzUxMiIsImlhdCI6MTU3ODc1NDQzNCwiZXhwIjoxNTc4NzU4MDM0fQ.eyJvcGVuaWQiOiIxMjM0In0.ugL_0K1ESCABgnd6d8_B9iV1LMWYtx4sBNko1-QHRVrAYSGJgbmIB3p0Xwn6f3WYs5zo6Zv3jRnMAxoqWGFz4w'


# 解密:
# s.loads()
























