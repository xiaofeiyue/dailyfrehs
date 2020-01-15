from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area
from utils.views import LoginRequiredJsonMixin

"""
省市区:三级联动
省市区在一张表中

id              name            parent_id

10000           河北省             null

10010            保定市            10000

10020            石家庄市           10000

10030             唐山市           10000



10011             a县                10010

10012              b县               10010
"""
















class AreasView(View):
    def get(self,request):
        area_id = request.GET.get('area_id')
        # 根据area_id 进行区分
        if area_id is None:
            # 如果没有area_id 则表示获取省份信息
            provinces = Area.objects.filter(parent_id=None)

            pro_list = []
            for province  in provinces:
                pro_list.append({
                    'id':province.id,
                    'name':province.name
                })
            return http.JsonResponse({'code':"0",'errmsg':'ok','province_list':pro_list})
        else:
            # area_id 不等于None:表示获取市区信息
            cities = Area.objects.filter(parent_id=area_id)

            cities_list = []

            for city in cities:
                cities_list.append({
                    'id':city.id,
                    'name':city.name
                })
            return http.JsonResponse({'code':'0','errmsg':'ok','cities':cities_list})






"""
select *from tb_areas where parent_id is NUll and name='甘肃省';
+--------+-----------+-----------+
| id     | name      | parent_id |
+--------+-----------+-----------+
| 620000 | 甘肃省    |      NULL |
+--------+-----------+-----------+
1 row in set (0.01 sec)


# 查询市区
Area.objects.filter(parent_id=620000);



province = Area.objects.filter(parent_id=620000)
<QuerySet [<Area: 兰州市>, <Area: 嘉峪关市>, <Area: 金昌市>, <Area: 白银市>, <Area: 天水市>, <Area: 武威市>, <Area: 张rea: 酒泉市>, <Area: 庆阳市>, <Area: 定西市>, <Area: 陇南市>, <Area: 临夏回族自治州>, <Area: 甘南藏族自治州>]>
>>>

自关联可以使用关联模型类小写加下划线set,
province.area_set.all()



如果在定义模型类的时候,写了related_name = ****,就不能使用模型类小写_set获取,应该使用自己定义的关联名字,
province.subs.all()
<QuerySet [<Area: 兰州市>, <Area: 嘉峪关市>, <Area: 金昌市>, <Area: 白银市>, <Area: 天水市>, <Area: 武威市>, <Area: 张rea: 酒泉市>, <Area: 庆阳市>, <Area: 定西市>, <Area: 陇南市>, <Area: 临夏回族自治州>, <Area: 甘南藏族自治州>]>
>>>







"""




