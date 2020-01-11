from django.db import models

# Create your models here.
"""
用户的qq号和oppenid是一一对应的,所以需要建立联系


"""


# class BaseModel(models.Model):
#     """为模型类补充字段"""
#
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#     update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
#
#     class Meta:
#         abstract = True  # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表
#


from utils.models import BaseModel

class OAuthQQUser(BaseModel):
    """QQ登录用户数据"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name