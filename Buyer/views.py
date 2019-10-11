from django.shortcuts import render
import hashlib
from Saller.models import *
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.core.paginator import Paginator
from Buyer.models import *
import time
from alipay import AliPay
from Qshop.settings import alipay_private_key_string, alipay_public_key_srting
from django.views.decorators.cache import cache_page

import logging
collect = logging.getLogger('django')
# Create your views here.
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

# 注册
def register(request):
    # 获取用户输入
    if request.method == 'POST':
        error = ''
        # 获取用户输入的数据
        username = request.POST.get('user_name')
        email = request.POST.get('email')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        if email:  # 获取到邮箱
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
                        user.save()
                        return HttpResponseRedirect('/Buyer/login/')

                    else:
                        error = '两次密码不一致'
                else:
                    error = '密码不能为空'
            else:
                error = '用户已存在'
        else:
            error = '邮箱不能为空'
    return render(request, 'buyer/register.html', locals())


# 登录装饰器
def loginValid(func):
    def inner(request,*args,**kwargs):
        cookie_email = request.COOKIES.get('email')
        session_email = request.session.get('email')
        if cookie_email and session_email and cookie_email==session_email:
            return func(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/Buyer/login/')
    return inner
# 登录
def login(request):
    if request.method == 'POST':
        error = ''
        # 获取用户的输入
        email = request.POST.get('email')
        password = request.POST.get('pwd')
        if email:
            user = LoginUser.objects.filter(email=email).first()
            if user:
                if user.user_type == 1:
                    if password:
                        if user.password == setPassword(password):
                            # error = '登录成功'
                            response = HttpResponseRedirect('/Buyer/index/')
                            response.set_cookie('email',email)
                            response.set_cookie('userid',user.id)
                            request.session['email'] = email
                            log_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
                            collect.info('['+str(log_time)+']:'+'%s is login!!'%(user.email))
                            return response
                        else:
                            error = '密码错误'

                    else:
                        error = '密码不能为空'
                else:
                    error = '用户不存在'
            else:
                error = '用户不存在'
        else:
            error = '邮箱不能为空'

    return render(request,'buyer/login.html',locals())

#首页
def index(request):
    result = []
    goods_type = GoodsType.objects.all()
    for ty in goods_type:
        goods = ty.goods_set.order_by('-goods_pro_time')
        # print(goods)
        if len(goods) >= 4:
            result.append({'goods_type':ty,'goods':goods[:4]})
    return render(request,'buyer/index.html',locals())

# 登出功能，在登出的时候删除cookie和session
def logout(request):
    response = HttpResponseRedirect('/Buyer/login/')
    response.delete_cookie('email')
    del request.session['email']
    return response


def base(request):
    return render(request,'buyer/base.html')

# 商品列表
@loginValid
def goods_list(request,page=1):
    goods_types = GoodsType.objects.all()
    req_type = request.GET.get('req_type')
    keywords = request.GET.get('keywords')
    if req_type == "findall":
        goods_type = GoodsType.objects.get(id=keywords)
        goods = goods_type.goods_set.order_by('-goods_pro_time')
    elif req_type == "search":
        goods = Goods.objects.filter(goods_name__contains=keywords).all()
    else:
        goods = Goods.objects.all().order_by('-goods_pro_time')
    # 分页
    page = int(page)
    paginator = Paginator(goods,15)
    page_obj = paginator.page(page)

    current_page = page_obj.number
    start = current_page-3
    end = current_page+2
    if start<0:
        start = 0
        end=5
    if end>paginator.num_pages:
        end = paginator.num_pages
        start = end-5
    page_range = paginator.page_range[start:end]
    # 推荐商品显示
    end = len(page_obj) // 5 + 1
    recommend_goods = goods.order_by('-goods_pro_time')[:end]

    return render(request,'buyer/goods_list.html',locals())

# 商品详情
@loginValid
def goods_detail(request):
    # print(request.COOKIES.get('user_id'))
    goods_types = GoodsType.objects.all()
    keywords = request.GET.get('keywords')
    goods = Goods.objects.get(id=keywords)
    goods_type = goods.goods_type_id
    recommend_goods = Goods.objects.filter(goods_type_id=goods_type).order_by('-goods_pro_time')[:2]
    # print(recommend_goods)
    return render(request,'buyer/goods_detail.html',locals())

# 用户中心
@loginValid
def user_center_info(request):
    user_id = request.COOKIES.get('userid')
    user = LoginUser.objects.get(id=user_id)
    return render(request,'buyer/user_center_info.html',locals())

# 直接点击立即购买生成订单
@loginValid
def place_order(request):
    # 获取goods_id,goods_number
    goods_id = request.GET.get('goods_id')
    goods_number = request.GET.get('goods_number')
    userid = request.COOKIES.get('userid')
    # user_id = request.COOKIES.get('user_id')
    buyer_user = LoginUser.objects.get(id=userid)
    # saller_user = LoginUser.objects.get(id=user_id)
    if goods_id and goods_number:
        goods_id = int(goods_id)
        goods_number = int(goods_number)
        goods = Goods.objects.get(id=goods_id)
        # 保存订单表
        # 生成对象
        payorder = PayOrder()
        # 生成订单编号
        payorder.order_number = str(time.time()).replace('.','')
        payorder.order_status = 0
        payorder.order_total = goods.goods_price*goods_number
        payorder.order_user = buyer_user
        payorder.save()
        # 保存订单详情表
        orderinfo = OrderInfo()
        orderinfo.order_id = payorder
        orderinfo.goods = goods
        orderinfo.goods_count = goods_number
        orderinfo.goods_total = goods.goods_price*goods_number
        orderinfo.goods_price = goods.goods_price
        orderinfo.store_id = goods.goods_store
        orderinfo.save()
    return render(request,'buyer/place_order.html',locals())

# 点击购物车的页面的去结算生成订单
@loginValid
def place_order_more(request):
    userid = request.COOKIES.get('userid')
    user_id = request.COOKIES.get('user_id')
    buyer_user = LoginUser.objects.get(id=userid)
    saller_user = LoginUser.objects.get(id=user_id)
    # print(user_id)
    data = request.GET
    info_list = []
    if data:
        # print(data)
        for k,v in data.items():
            if k.startswith('goods'):
                goods_id = k.split('_')[1]
                cart_id = k.split('_')[2]
                goods_count = data.get('count_'+goods_id)
                info_list.append((int(goods_id),int(goods_count),int(cart_id)))
    # print(info_list)
    # 保存订单表
    # cart_one = Cart.objects.get(id = info_list[0][2])
    # # print(cart_one.order_number)
    # if cart_one.order_number != '0' and cart_one.goods_number == info_list[0][1]:
    #     payorder = PayOrder.objects.get(order_number=cart_one.order_number)
    # if cart_one.order_number == '0' or cart_one.goods_number != info_list[0][1]:
    payorder = PayOrder()
    payorder.order_number = str(time.time()).replace('.','')
    payorder.order_status = 0
    payorder.order_total = 0 ## 因为该字段设置的不能为空，但是数据需要循环计算，可以先设为0，最后在进行修改
    payorder.order_user = buyer_user
    payorder.save()
# 保存订单详情表
    total = 0
    for one in info_list:
        goods_id = one[0]
        goods_count = one[1]
        cart_id = one[2]
        orderinfo = OrderInfo()
        orderinfo.order_id = payorder
        orderinfo.goods = Goods.objects.get(id=goods_id)
        orderinfo.goods_count = goods_count
        orderinfo.goods_price = Goods.objects.get(id=goods_id).goods_price
        orderinfo.goods_total = Goods.objects.get(id=goods_id).goods_price*goods_count
        orderinfo.store_id = saller_user
        orderinfo.save()
        total+=orderinfo.goods_total
        cart = Cart.objects.get(id=cart_id)
        cart.order_number = payorder.order_number
        cart.save()
    payorder.order_total = total
    payorder.save()
    goods_number = len(info_list)


    return render(request,'buyer/place_order.html',locals())

# 支付
def alipayviews(request):
    order_id = request.GET.get('order_id')
    payorder = PayOrder.objects.get(id=order_id)
    # 实例化支付对象
    alipay = AliPay(
        appid='2016101300673930',
        app_notify_url=None,
        app_private_key_string=alipay_private_key_string,
        alipay_public_key_string=alipay_public_key_srting,
        sign_type="RSA2",
    )

    # 实例化订单
    order_string = alipay.api_alipay_trade_page_pay(
        subject='牛羊生鲜',  # 交易主体
        out_trade_no=payorder.order_number,  # 订单号
        total_amount=str(payorder.order_total),  # 交易总金额
        return_url='http://127.0.0.1:8000/Buyer/payresult/',  # 请求支付，之后及时回调的一个接口
        notify_url='http://127.0.0.1:8000/Buyer/payresult/',  ## 通知地址

    )

    # 发送支付请求
    # 请求地址 支付网关 + 实例化订单
    result = "https://openapi.alipaydev.com/gateway.do?" + order_string
    # print(result)
    return HttpResponseRedirect(result)

# 支付结果
def payresult(request):
    order_number = request.GET.get('out_trade_no')
    payorder = PayOrder.objects.get(order_number=order_number)
    payorder.order_status = 1
    payorder.save()
    cart = Cart.objects.filter(order_number=order_number)
    for one in cart:
        one.order_status = 1
        one.save()
    orderinfo = payorder.orderinfo_set.all()
    for one in orderinfo:
        one.status = 1
        one.save()

    return render(request,'buyer/payresult.html',locals())

# 实现添加购物车
@loginValid
def add_cart(request):
    # print(request.COOKIES.get('user_id'))
    result = {'code':10000,'content':''}
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        count = int(request.POST.get('count',1))
        user_id = request.COOKIES.get('userid')
        goods = Goods.objects.get(id=goods_id)
        cart = Cart()
        cart.goods_number = count
        cart.goods_price = goods.goods_price
        cart.goods_total = count*goods.goods_price
        cart.goods = goods
        cart.cart_user = LoginUser.objects.get(id=user_id)
        cart.save()
        result['content'] = '添加数据成功'
    else:
        result['code'] = 10001
        result['content'] = '请求方式不正确'
    return JsonResponse(result)

# 购物车
@loginValid
def cart(request):
    user_id = request.COOKIES.get('userid')
    # print(user_id)
    cart = Cart.objects.filter(cart_user_id=user_id,order_status=0).order_by('-id')
    # print(cart)
    count = cart.count()
    return render(request,'buyer/cart.html',locals())

# 用户的全部订单页
@loginValid
def user_center_order(request,page=1):
    page = int(page)
    user_id = request.COOKIES.get('userid')
    user = LoginUser.objects.get(id=user_id)
    payorder_all = user.payorder_set.order_by('order_status','-order_date')
    paginator = Paginator(payorder_all,5)
    page_obj = paginator.page(page)

    current_page = page_obj.number
    start = current_page-3
    end = current_page+2
    if start < 0:
        start = 0
        end = 5
    if end > paginator.num_pages:
        end = paginator.num_pages
        start = end-5
    page_range = paginator.page_range[start:end]


    return render(request,'buyer/user_center_order.html',locals())

# 点击删除，删除数据库中的数据
def remove(request):
    # print(request.GET)
    result = {'code':10000,'msg':''}
    cart_id = int(request.GET.get('cart_id'))
    cart = Cart.objects.get(id = cart_id)
    if cart.delete():
        result['msg'] = '删除成功'
    else:
        result['code'] = 10001
        result['msg'] = '删除失败'

    return JsonResponse(result)

# 收货地址
def user_center_site(request):
    user_id = request.COOKIES.get('userid')
    buyer_user = LoginUser.objects.get(id=user_id)
    site_id = request.GET.get('site_id')
    if site_id:
        for one in buyer_user.site_set.all():
            # print(one)
            one.status = 0
            one.save()
        site = Site.objects.get(id=site_id)
        site.status = 1
        site.save()
        buyer_user.address = Site.objects.filter(status=1).first().adderss_detail
        buyer_user.save()

    if request.method == 'POST':
        username = request.POST.get('username')
        u_code = request.POST.get('youbian')
        address_detail = request.POST.get('site')
        phone = request.POST.get('phone')
        if username and u_code and address_detail and phone:
            site = Site()
            site.username = username
            site.u_code = u_code
            site.adderss_detail = address_detail
            site.phone = phone
            site.status = 0
            site.user = buyer_user
            site.save()
        else:
            error = '输入不完整'

    return render(request,'buyer/user_center_site.html',locals())






















from CeleryTask.tasks import *
def reqtest(request):
    # 执行celery任务
    test.delay() ## 发布任务

    # 带参数的任务
    name = request.GET.get('name')
    age = request.GET.get('age')
    myprint.delay(name,age)
    return HttpResponse('req test')


# 短信任务
import random
def duanxincode(request):
    code = random.randint(1000, 9999)
    content = '您的验证码是:%s,请不要把验证码泄露给其他人。' %(code)
    params = {
        'mobile':'15852463859',
        'content':content
    }
    duanxin.delay(params)
    return HttpResponse('发送成功')


def process_tem_rep(request):
    def test():
        return HttpResponse("my test")
    rep = HttpResponse("process_tem_rep")
    rep.render = test
    return rep


from django.core.cache import cache
def cache_test(request):
    order_number = request.GET.get('order_number')
    # 缓存中如果有数据，直接从缓存中获取
    data = cache.get(order_number)    ### cache结构:key:value
    print('--------------')
    print(cache)
    ## 如果缓存中没有数据，就从数据库中查询保存到缓存中。
    if not data:
        print('++++++++++++++')
        payorder = PayOrder.objects.filter(order_number=order_number).first()
        cache.set(order_number,payorder.order_total,60)
        data = payorder.order_total

    return HttpResponse('total_count%s'%data)


