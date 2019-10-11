from django.urls import path,re_path
from Saller import views


urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('index/', views.index),
    path('logout/', views.logout),
    path('goods_list/', views.goods_list),
    path('personal_info/', views.personal_info),
    re_path('goods_list/(?P<status>[01])/(?P<page>\d+)/', views.goods_list),
    re_path('goods_status/(?P<status>\w+)/(?P<id>\d+)/', views.goods_status),
    path('add_goods/',views.add_goods),
]
