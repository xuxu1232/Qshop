from __future__ import absolute_import
from Qshop.celery import app
import time
## 创建任务
@app.task  ## 将普通的函数转换为celery任务
def test():
    print('----i am test task----')
    return "i am test task"

@app.task
def myprint(name,age):
    time.sleep(2)
    print(name,age)
    return "myprint test"




@app.task
def duanxin(params):
    import requests
    url = 'http://106.ihuyi.com/webservice/sms.php?method=Submit'
    account = 'C10415932'
    password = '0a469d492a1987e2c54f91bad7094b25'

    mobile = params.get('mobile')


    headers = {
        'Content-type': 'application/x-www/form-urlencoded',
        'Accept': 'text/plain'
    }

    data = {
        'account': account,
        'password': password,
        'mobile': mobile,
        'content': params.get('content'),
    }

    response = requests.post(url,headers=headers,data=data)
    print(response.content.decode())
    print(data)
    return response

