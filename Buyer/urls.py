from django.urls import path,re_path
from Buyer import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('index/', views.index),
    path('logout/', views.logout),
    path('base/', views.base),
    path('goods_list/', views.goods_list),
    re_path('goods_list/(?P<page>\d+)', views.goods_list),
    path('goods_detail/', views.goods_detail),
    path('user_center_info/', views.user_center_info),
    path('place_order/', views.place_order),
    path('alipayviews/', views.alipayviews),
    path('payresult/', views.payresult),
    path('add_cart/', views.add_cart),
    path('cart/', views.cart),
    path('place_order_more/', views.place_order_more),
    path('user_center_order/', views.user_center_order),
    re_path('user_center_order/(?P<page>\d+)', views.user_center_order),
    path('remove/', views.remove),
    path('user_center_site/', views.user_center_site),
    path('reqtest/', views.reqtest),
    path('duanxincode/', views.duanxincode),
    path('process_tem_rep/', views.process_tem_rep),
    path('cache_test/', views.cache_test),
]
