from django.db import models
from django.db.models import Manager
# Create your models here.

# 自定义操作
class GoodsManager(Manager):
    def query(self):
        goods = Goods.objects.filter(id__lt = 5).values('goods_name')
        return goods
    def addgoods(self,goods_number,goods_name,goods_price,goods_count,goods_location,goods_safe_date,goods_status=1,picture='images/li.jpg'):
        goods = Goods()
        goods.goods_number = goods_number
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_count = goods_count
        goods.goods_location = goods_location
        goods.goods_safe_date = goods_safe_date
        goods.goods_status = goods_status
        goods.picture = picture
        goods.save()
        return goods


class LoginUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)
    username = models.CharField(max_length=32,null=True,blank=True)
#     null数据库中的数据可以为空，blank针对表单，表单中的数据可以不填
    phone_number = models.CharField(max_length=11,null=True,blank=True)
    photo = models.ImageField(upload_to='images',null=True,blank=True)
    age = models.IntegerField(null=True,blank=True)
    gender = models.CharField(null=True,blank=True,max_length=4)
    address = models.TextField(null=True,blank=True)
    # 0是卖家   1是买家   2是管理员
    user_type = models.IntegerField(default=1)

class Site(models.Model):
    username = models.CharField(max_length=32,verbose_name='用户姓名')
    adderss_detail = models.TextField(verbose_name='详细地址')
    u_code = models.CharField(max_length=11,verbose_name='邮编')
    phone = models.CharField(max_length=11,verbose_name='电话')
    status = models.IntegerField(verbose_name='地址状态') ### 1代表选中，0代表未选中
    user = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE)


class GoodsType(models.Model):
    type_label = models.CharField(max_length=32)
    type_description = models.TextField()
    type_picture = models.ImageField(upload_to='images')

class Goods(models.Model):
    goods_number = models.CharField(max_length=11)
    goods_name = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_count = models.IntegerField()
    goods_location = models.CharField(max_length=254)
    goods_safe_date = models.IntegerField()
    goods_pro_time = models.DateField(auto_now=True,verbose_name='生产日期')
    goods_status = models.IntegerField()
    goods_description = models.TextField(null=True)
    goods_detail = models.TextField(null=True)
    picture = models.ImageField(upload_to='images')
    goods_type = models.ForeignKey(to=GoodsType,on_delete=models.CASCADE,default=1)
    goods_store = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE,default=1)
    objects = GoodsManager()


# 验证码练习
class Valid_Code(models.Model):
    code_content = models.CharField(max_length=8,verbose_name='验证码')
    code_time = models.DateTimeField(auto_now=True,verbose_name='创建时间')
    code_status = models.IntegerField(verbose_name='验证码状态')## 1 使用 0 未使用
    code_user = models.EmailField(verbose_name='邮箱')
