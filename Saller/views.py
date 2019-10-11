from django.shortcuts import render
import hashlib
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from Saller.models import *
from django.core.paginator import Paginator
import random,datetime,calendar
from Buyer.models import *
from django.db.models import Count,Sum

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

# 定义获取当月第一天和最后一天的函数
def get_day():
    # 获取当月第一天的星期和当月的总天数
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    last_day = calendar.monthrange(year, month)[1]

    # 获取当月的第一天
    firstDay = datetime.date(year=year, month=month, day=1)
    lastDay = datetime.date(year=year, month=month, day=last_day)
    return firstDay,lastDay
@loginValid
def index(request):
    user_id = request.COOKIES.get('user_id')
    saller_user = LoginUser.objects.get(id=user_id)
    first_day,last_day = get_day()

    ### 获取当月所有的订单
    payorder = PayOrder.objects.filter(order_date__range=[first_day,last_day])
    # print(payorder)
    ### 获取属于该店铺的订单详情
    orderinfo = OrderInfo.objects.filter(store_id=saller_user,order_id__in=payorder,status=3)
    # print(orderinfo)
    sum_all = orderinfo.aggregate(Sum('goods_total'),Count('id'),Sum('goods_count'))
    # 查找当月销售额
    # print(sum_all)
    sum_money = sum_all.get('goods_total__sum')
    if sum_money is None:
        sum_money = 0
    # 查找当月交易订单量
    count = sum_all.get('id__count')
    if count is None:
        count = 0
    # 查找当月销售商品量
    goods_count__sum = sum_all.get('goods_count__sum')
    if goods_count__sum is None:
        goods_count__sum = 0
    # 查找当月热销单品
    ### 分组查询
    ### 根据商品进行分组，返回商品id和对应订单详情数量
    orderinfo = OrderInfo.objects.filter(store_id=saller_user,order_id__in=payorder)
    orderinfo_group = orderinfo.values('goods').annotate(Sum('goods_count'))
    # print(orderinfo_group)
    ### 将返回的queryset转换为字典
    d = {}
    for i in orderinfo_group:
        d[i['goods']] = i['goods_count__sum']
    #### 找到商品数量最大的id
    max_goods_id = []
    for k, v in d.items():
        if v == max(d.values()):
            max_goods_id.append(k)
    goods = Goods.objects.filter(id__in=max_goods_id)[:2]
    return render(request,'saller/index.html',locals())

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
    if start <= 0 and int(paginator.num_pages) <= 6:
        start = 0
        end = paginator.num_pages

    if end > paginator.num_pages:
        end = paginator.num_pages
        start = end - 6

    page_range = paginator.page_range[start:end]
    print(page_range)
    print(start,end)
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

# 修改
def update(request):
    goods_id = request.GET.get('goods_id')
    goods = Goods.objects.get(id=goods_id)
    goods_type = GoodsType.objects.all()
    data = request.POST
    if data:
        goods.goods_number = data.get('goods_number')
        goods.goods_name = data.get('goods_name')
        goods.goods_price = data.get('goods_price')
        goods.goods_count = data.get('goods_count')
        goods.goods_location = data.get('goods_location')
        goods.goods_safe_date = data.get('goods_safe_date')
        goods.goods_type = GoodsType.objects.get(id=data.get('goods_type'))
        if request.FILES.get('picture'):
            goods.picture = request.FILES.get('picture')
        goods.save()
    return render(request,'saller/update_goods.html',locals())
# 使用邮件发送验证码
import smtplib
from email.mime.text import MIMEText


# def send_code(params):
#     # 构建邮件
#     # 主题
#     subject = params.get('subject')
#     # 发送内容
#     content = params.get('content')
#     # 发送人
#     sender = 'str_wjp@163.com'
#     # 收件人
#     recver = params.get('toemail')
#     password = "qaz123"
#     ## MIMEText 参数：发送内容，内容类型，编码
#     message = MIMEText(content, 'plain', 'utf-8')
#     message['Subject'] = subject
#     message['From'] = sender
#     message['To'] = recver
#
#     # 发送邮件
#     try:
#         smtp = smtplib.SMTP_SSL("smtp.163.com", 465)
#         smtp.login(sender, password)
#         # smtp 参数：发件人，收件人（列表），发送邮件（类似有json）
#         smtp.sendmail(sender, recver.split(',\n'), message.as_string())
#
#         smtp.close()
#         return True
#     except:
#         return False
#
#
# def get_code(request):
#     result = {'code': 10000, 'msg': ''}
#     email = request.GET.get('email')
#     # print(email)
#     if email:
#         user_flag = LoginUser.objects.filter(email=email).first()
#         if user_flag:
#             valid_code = random.randint(1000, 9999)
#             content = '您的验证码是%s,请不要泄露给他人'%(valid_code)
#             params = {'subject':'登录验证码','content':content,'toemail':[email]}
#             code_flag = send_code(params)
#             if code_flag:
#                 code = Valid_Code()
#                 code.code_content = valid_code
#                 code.code_status = 0
#                 code.code_user = email
#                 code.save()
#                 result['content'] = '验证码发送成功'
#             else:
#                 result['code'] = 10001
#                 result['content'] = '未知错误，请联系客服'
#         else:
#             result['code'] = 10002
#             result['content'] = '用户不存在，去注册'
#     else:
#         result['code'] = 10003
#         result['content'] = '邮箱不能为空'
#
#     return HttpResponse(result)

# 登录
# import time
# import datetime
def login(request):
    if request.method == 'POST':
        error = ''
        # 获取用户的输入
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email:
            user = LoginUser.objects.filter(email=email,user_type=0).first()
            if user:
                if password:
                    if user.password == setPassword(password):
                        # 判断验证码
                        # 从数据库中取出刚保存的验证码
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


def order(request,status):
    status = int(status)
    user_id = request.COOKIES.get('user_id')
    user = LoginUser.objects.get(id=user_id)
    orderinfo = user.orderinfo_set.filter(store_id=user,status=status)
    # payorder = set()
    # for i in orderinfo:
    #     payorder.add(i.order_id)
    return render(request,'saller/order.html',locals())


def send_email(params):
    import smtplib
    from email.mime.text import MIMEText

    # 构建邮件
    # 主题
    subject = '提醒付款'
    # 发送内容
    content = params.get('content')
    # 发送人
    sender = params.get('sender')
    # 收件人
    recver = params.get('recv')
    password = "qaz123"
    ## MIMEText 参数：发送内容，内容类型，编码
    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recver
    try:
        # 发送邮件
        smtp = smtplib.SMTP_SSL("smtp.163.com", 465)
        smtp.login(sender, password)
        # smtp 参数：发件人，收件人（列表），发送邮件（类似有json）
        smtp.sendmail(sender, [recver], message.as_string())

        smtp.close()
        return True
    except:
        return False


def sendemail(request):
    result = {
        'code':10000,
        'content':''
    }
    user_id = request.COOKIES.get('user_id')
    order_number = request.POST.get('order_number')
    user = LoginUser.objects.get(id=user_id)
    payorder = PayOrder.objects.filter(order_number=order_number).first()
    params = {
        'sender':user.email,
        'recv':payorder.order_user.email,
        'content':'亲，您还没有支付哦，请尽快付款哦'
    }
    flag = send_email(params)
    # if flag:
    result['content'] = '邮箱发送成功'
    # else:
    #     result['content'] = '未知错误，请联系客服'
    #     result['code'] = 10001

    return JsonResponse(result)


def saller_caozuo(request):
    req_type = request.GET.get('req_type')
    orderinfo_id = request.GET.get('orderinfo_id')
    if req_type == 'refuse':
        orderinfo = OrderInfo.objects.get(id=orderinfo_id)
        orderinfo.status = 4
        orderinfo.save()
    if req_type == 'fahuo':
        orderinfo = OrderInfo.objects.get(id=orderinfo_id)
        orderinfo.status = 2
        orderinfo.save()
    url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(url)


