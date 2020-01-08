from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.verifications.constant import IMAGE_CODE_EXPIRE_TIME
from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP


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
        redis_conn.setex('img_%s'% uuid,IMAGE_CODE_EXPIRE_TIME,text)
        return http.HttpResponse(image,content_type='image/jpeg')
    """
    content_type :所对应的是MIME类型
    语法形式:大类/小
    image/jpeg image/png  image/gif
    text/html  text/css
    如果不告知浏览器,ＭＩＭＥ类型浏览器默认会以text/html



    """


"""
用户输入手机号和图片验证码之后，点击获取短信验证码
前端：收集手机号和用户输入的图片验证码以及ｕｕｉｄ
后端：实现验证发送短信

"""

"""
后端：
１．接受数据
２．验证数据
３．提取redis中的验证码
4．删除redis中验证码　　　　防止用户多次恶意输
５．对比用户输入的和redis 的是否一致
６．生成随机短信验证码
７．将短信验证码保存到redis中
８．蓉莲润发送短信
９返回响应
"""

# 短信验证码

"""
三.确定请求方式和路由
    GET  sms_code/mobile/?image_code=xxxx&image_code_id=xxx  v

    GET
    提取URL的特定部分，如/weather/beijing/2018，可以在服务器端的路由中用正则表达式截取；
        sms_code/mobile/image_code/uuid/

    查询字符串（query string)，形如key1=value1&key2=value2；
        sms_code/?mobile=xxx&image_code=xxxx&uuid=xxxx

    POST
    json        sms_code/


"""
class SmsCodeView(View):
    def get(self,request,mobile):
        # 从查询字符串中获取参数信息
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 验证参数
        if not all([image_code_client,uuid]):
            return http.JsonResponse({'code':0,'errmsg':'缺少东西'})
        #链接redis 数据库
        redis_conn =get_redis_connection('code')
        # 从redis 数据库中提取图片验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 判断验证码是否过期
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
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code':0,'errmsg':'输入图片验证码错误'})

        #  添加一个标记未，防止用户恶意多次请求发送短信，
        send_flag = redis_conn.get('send_flag_%s'%mobile)
        if send_flag == 1:
            return http.JsonResponse({'code':'短信频繁操作'})
        # 生成短信验证码，将生成的短信验证码保存到redis 中
        from random import randint
        sms_code = '%06d' % randint(0,999999)
        # sms_code = randint(100000,999999)
        redis_conn.setex('sms_%s'%mobile,300,sms_code)
        # 发送短信验证码之后，添加标记位
        redis_conn.setex('send_flag_%s'%mobile,60,1)
        CCP().send_template_sms(mobile,[sms_code,5],1)

        # 使用容联运发送短信
        # 返回响应
        return http.JsonResponse({'code':0,'errmsg':'ok'})


