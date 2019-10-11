from django.db import models
from Saller.models import *


# Create your models here.
ORDER_LIST = (
    (0,'未支付'),
    (1,'已支付'),
    (2,'待发货'),
    (3,'待收货'),
    (4,'完成'),
    (5,'拒收'),
    (6,'拒绝订单'),
)
# 订单表
class PayOrder(models.Model):
    # 订单编号，唯一不为空
    # 利用时间戳生成订单编号
    order_number = models.CharField(max_length=32,verbose_name='订单编号',unique=True)
    order_date = models.DateField(auto_now=True,verbose_name='订单日期')

    # 订单状态：0 未支付，1 已支付，2 待发货，3 待收货，4 完成，5 拒收
    order_status = models.IntegerField(choices=ORDER_LIST,verbose_name='订单状态')
    order_total = models.FloatField(verbose_name='订单总价')
    # 外键，关联LoginUser
    order_user = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE,verbose_name='订单用户')

ORDER_INFO = (
    (0,'未支付'),
    (1,'已支付'),
    (2,'已发货'),
    (3,'已完成'),
    (4,'拒绝订单'),
)
# 订单详情表
class OrderInfo(models.Model):
    # 外键 关联订单表
    order_id = models.ForeignKey(to=PayOrder,on_delete=models.CASCADE,verbose_name='订单表')
    # 外键，关联商品表
    goods = models.ForeignKey(to=Goods,on_delete=models.CASCADE,verbose_name='商品表')
    goods_count = models.IntegerField(verbose_name='商品数量')
    goods_total = models.FloatField(verbose_name='商品小计')
    goods_price = models.FloatField(verbose_name='商品单价')
    # 外键表 关联用户表
    store_id = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE)
    status = models.IntegerField(choices=ORDER_INFO,default=0)

class Cart(models.Model):
    order_number = models.CharField(max_length=32,default=0)
    goods_number = models.IntegerField(verbose_name='商品数量')
    goods_price = models.FloatField(verbose_name='商品单价')
    goods_total = models.FloatField(verbose_name='商品总价')
    goods = models.ForeignKey(to=Goods,on_delete=models.CASCADE)
    cart_user = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE)
    order_status = models.IntegerField(default=0)