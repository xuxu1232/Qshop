# Generated by Django 2.2.1 on 2019-09-24 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Saller', '0002_auto_20190923_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='loginuser',
            name='user_type',
            field=models.IntegerField(default=1),
        ),
    ]
