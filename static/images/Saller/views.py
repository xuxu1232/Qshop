from django.shortcuts import render
import hashlib
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from Saller.models import *
from django.core.paginator import Paginator
import random

# Create your views here.
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

# 完成注册
def register(request):
    if request.method == 'POST':
        error = ''
        # 获取用户输入的数据
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if email:   #获取到邮箱
            user = LoginUser.objects.filter(email=email).first()
            # 用户不存在
            if not user:
                # 判断是否输入密码
                # 输入
                if password and password2:
                    # 判断两次密码是否一致
                    # 一致
                    if password == password2:
                        user = LoginUser()
                        user.username = username
                        user.email = email
                        user.password = setPassword(password)
                        user.user_type = 0
                        user.save()
                        return HttpResponseRedirect('/Saller/login/')

                    else:
                        error = '两次密码不一致'
                else:
                    error = '密码不能为空'
            else:
                error = '用户已存在'
        else:
            error = '邮箱不能为空'
    return render(request,'saller/register.html',locals())

# 登录装饰器
def loginValid(func):
    def inner(request,*args,**kwargs):
        cookie_email = request.COOKIES.get('email')
        session_email = request.session.get('email')
        if cookie_email and session_email and cookie_email==session_email:
            return func(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/Saller/login/')
    return inner
# 登录
def login(request):
    if request.method == 'POST':
        error = ''
        # 获取用户的输入
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email:
            user = LoginUser.objects.filter(email=email).first()
            if user:
                if password:
                    if user.password == setPassword(password):
                        # error = '登录成功'
                        response = HttpResponseRedirect('/Saller/index/')
                        response.set_cookie('email',email)
                        response.set_cookie('user_id',user.id)
                        request.session['email'] = email
                        return response
                    else:
                        error = '密码错误'
                else:
                    error = '密码不能为空'
            else:
                error = '用户不存在'
        else:
            error = '邮箱不能为空'

    return render(request,'saller/login.html',locals())

@loginValid
def index(request):
    return render(request,'saller/index.html')

# 登出功能，在登出的时候删除cookie和session
def logout(request):
    response = HttpResponseRedirect('/Saller/login/')
    response.delete_cookie('email')
    del request.session['email']
    return response


# 定义一个商品列表的视图，显示商品数据
def goods_list(request,status='1',page=1):
    # 实现分页
    if status == '1':
        goods_all = Goods.objects.filter(goods_status=1).order_by('goods_number')
    else:
        goods_all = Goods.objects.filter(goods_status=0).order_by('goods_number')
    paginator = Paginator(goods_all,10)
    page_obj = paginator.page(page)

    # 当前页码
    current_page = page_obj.number
    start = current_page-4
    end = current_page+2
    if start<0:
        start = 0
        end = 6
    if end > paginator.num_pages:
        end = paginator.num_pages
        start = end-6
    page_range = paginator.page_range[start:end]
    return render(request,'saller/goods_list.html',locals())

def goods_status(request,status,id):
    id = int(id)
    goods = Goods.objects.get(id=id)
    if status == 'up':
        goods.goods_status = 1
    else:
        goods.goods_status = 0
    goods.save()
    url = request.META.get('HTTP_REFERER','Saller/goods_list/1/1/')
    return HttpResponseRedirect(url)

@loginValid
def personal_info(request):
    user_id = request.COOKIES.get('user_id')
    user = LoginUser.objects.get(id=user_id)
    if request.method == 'POST':
        data = request.POST
        user.username = data.get('username')
        user.phone_number = data.get('phone')
        user.age = data.get('age')
        user.gender = data.get('gender')
        user.address = data.get('address')
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')
        user.save()

    return render(request,'saller/personal_info.html',locals())

@loginValid
def add_goods(request):
    goods_type = GoodsType.objects.all()
    if request.method == 'POST':
        data = request.POST
        goods = Goods()
        goods.goods_number = data.get('goods_number')
        goods.goods_name = data.get('goods_name')
        goods.goods_price = data.get('goods_price')
        goods.goods_count = data.get('goods_count')
        goods.goods_location = data.get('goods_location')
        goods.goods_safe_date = data.get('goods_safe_date')
        goods.goods_status = 1
        goods.picture = request.FILES.get('picture')
        goods.save()
        goods.goods_type = GoodsType.objects.get(id=data.get('goods_type'))
        goods.save()
    return render(request,'saller/add_goods.html',locals())

