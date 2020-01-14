from django.shortcuts import render

# Create your views here.
from django.views import View

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





class AddressView(LoginRequiredJsonMixin,View):
    def get(self,request):
        return render(request,'user_center_site.html')