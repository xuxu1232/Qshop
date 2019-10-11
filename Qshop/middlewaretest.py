from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import os,time
from Qshop.settings import BASE_DIR

class MiddleWareTest(MiddlewareMixin):
    def process_request(self,request):
        ###  request.META.get("REMOTE_ADDR"):获取ip
        # print('我是 process_request')
        ip = request.META.get('REMOTE_ADDR')
        if ip == '10.10.107.106':
            return HttpResponse('我是你的小宝贝')

    # def process_view(self,request,callback,callback_args,callback_kwargs):
        # print('我是 process_view')
        # print(callback)
        # print(callback_args)
        # print(callback_kwargs)

    # def process_exception(self,request,exception):
    #     # print('我是 process_exception')
    #     # print(exception)
    #     # 将报错信息写入日志
    #     file = os.path.join(BASE_DIR,'error.log')
    #     with open(file,'a') as f:
    #         now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    #         content = "[%s]:%s\n"%(now,str(exception))
    #         f.write(content)
    #     return HttpResponse(content)



    def process_template_response(self,request,response):
        # print('我是 process_template_response')
        return response


    def process_response(self,request,response):
        # print('我是 process_response')
        return response



