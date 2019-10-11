import os
from celery import Celery
from django.conf import settings


## 设置celery的环境变量和django-celery 的主目录
os.environ.setdefault('DJANGO_SETTINGS_MODULE','CeleryTask.settings')
## 实例化一个应用 art_project:celery服务器的名字
app = Celery('art_project')

## 加载celery配置
app.config_from_object('django.conf:settings')

## 如果在项目当中，创建了tasks.py，celery就会沿着app寻找这个文件夹来生成任务
app.autodiscover_tasks(lambda :settings.INSTALLED_APPS)
