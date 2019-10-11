from django.db import models

# Create your models here.
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
    picture = models.ImageField(upload_to='images')
    goods_type = models.ForeignKey(to=GoodsType,on_delete=models.CASCADE,default=1)
    goods_store = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE,default=1)