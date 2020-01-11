from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

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