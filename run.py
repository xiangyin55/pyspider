# -*- coding: UTF-8 -*-
#  This file will be run on startup and when a remote Python engine
#  gets initialized

#  Add import statements or anything else you want here
#import sys

# -*- coding:utf-8 -*-
#!flask/bin/python
# pip install flask
# pip install flask-httpauth
'''
==========  ===============================================  =============================
HTTP 方法   URL                                              动作
==========  ===============================================  ==============================
GET         http://[hostname]/todo/api/v1.0/tasks            检索任务列表
GET         http://[hostname]/todo/api/v1.0/tasks/[task_id]  检索某个任务
POST        http://[hostname]/todo/api/v1.0/tasks            创建新任务
PUT         http://[hostname]/todo/api/v1.0/tasks/[task_id]  更新任务
DELETE      http://[hostname]/todo/api/v1.0/tasks/[task_id]  删除任务
==========  ================================================ =============================
'''

from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
import random,json

app = Flask(__name__)

def save_ips():

    """保存所有代理IP的数据"""
    url = "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list"# github上的开源IP

    try:
        r = requests.get(url)
        s = '['+ r.text.replace('\n',',').rstrip(',')+']'
        j = json.loads(s)
    except Exception as e:
        return
        raise e

    # 处理数据
    proxies = []

    for d in j:

        if d["anonymity"] == "high_anonymous":  # 这里只保存了高匿代理
            t = {}
            t["type"] = d["type"]
            t["host"] = d["host"]
            t["port"] = d["port"]
            proxies.append(t)

    # 把代理IP保存下来，不要频繁访问该网站
    path = u'ips_all.txt'

    try:
        # 如果config.SAVE_PATH路径不存在，自动创建
        open(path, "w").write(json.dumps(proxies)) # 以json格式保存数据，方便解析
        print(path,'save succeed')
    except Exception as e:
        raise e

def get_ips(total=1,type='https'):
    """读取已经保存的IP，随机抽出total数量的IP"""
    """type='http'  返回http代理 socket """
    """type='https'  返回https代理 socket """
    """type='proxies'  返回proxies参数代理格式 """


    path = u'ips_all.txt'
    if os.path.exists(path) == False:
        print(path,"文件不存在")
        return

    j = json.load(open(path,'r').read())


    http_list = []
    https_list = []
    for d in j:
        if d['type'] == 'http':
            http_list.append(d['host'] + ':' + d['port'])
        elif d['type'] == 'https':
            http_list.append(d['host'] + ':' + d['port'])

    proxies = []
    for i in range(total):
        http = random.choice(http_list)
        https = random.choice(https_list)
        proxy = {'http':'http://'+http,'https':'https://'+https}  # 返回的每一个代理
        proxies.append(proxy)

    if type == 'http':
        return random.sample(http_list,total)
    elif type == 'https':
        return random.sample(https_list,total)
    elif type == 'proxies':
        return proxies

def verify_ips(proxies):
    useful_proxies = []
    for proxy in proxies:
        try:
            r = requests.get(url=config.URL,proxies=proxy,timeout=5)
            useful_proxies.append(proxy)
        except:
            continue
    return useful_proxies

def random_agent():
    user_agent_list = [\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
       ]
    return random.choice(user_agent_list)

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task



@app.route('/')
def index():
    return "Hello, World!\n"

@app.route('/agent' , methods=['GET'])
def get_agent():
    return random_agent()

@app.route('/proxy' , methods=['GET'])
def get_proxy():
    return random_proxy()

@app.route('/proxy' , methods=['DELETE'])
def del_proxy():
    return random_proxy()



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=9000)
