from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha


class ImageCodeView(View):
    def get(self,request,uuid):
        """
        获取图片和图片验证码
        将图片验证码的内容保存到redis中
        返回图片


        :param request:
        :param uuid:
        :return:
        """
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'% uuid,120,text)
        return http.HttpResponse(image,content_type='image/jpeng')
    """
    content_type :所对应的是MIME类型
    语法形式:大类/小类
    image/jpeg image/png  image/gif
    text/html  text/css
    如果不告知浏览器,ＭＩＭＥ类型浏览器默认会以text/html



    """