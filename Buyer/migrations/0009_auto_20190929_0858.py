# Generated by Django 2.2.1 on 2019-09-29 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Buyer', '0008_cart_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payorder',
            name='order_status',
            field=models.IntegerField(choices=[(0, '未支付'), (1, '已支付'), (2, '待发货'), (3, '待收货'), (4, '完成'), (5, '拒收')], verbose_name='订单状态'),
        ),
    ]
