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
        return http.HttpResponse(image,content_type='image/jpeg')
    """
    content_type :所对应的是MIME类型
    语法形式:大类/小
    image/jpeg image/png  image/gif
    text/html  text/css
    如果不告知浏览器,ＭＩＭＥ类型浏览器默认会以text/html



    """


# 短信验证码
class SmsCodeView(View):
    def get(self,request,mobile):
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 验证参数
        if not all([image_code_client,uuid]):
            return http.JsonResponse({'code':0,'errmsg':'缺少东西'})
        #链接redis 数据库
        redis_conn =get_redis_connection('code')
        # 从redis 数据库中提取图片验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code':0,'errmsg':'图片验证码失效'})
        # 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s'% uuid)
        except Exception as e:
            import logging
            logger = logging.getLogger('django')
            logger.error(e)

        # 对比图形验证码
        image_code_server = image_code_server.decode()
        if image_code_client != image_code_server.lower():
            return http.JsonResponse({'code':0,'errmsg':'输入图片验证码'})

        redis_conn.setex()