#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-04-25 09:40:20
# Project: baidu
from pyspider.libs.base_handler import *
import json
import re
import random
import js2py
import pymongo
from pyquery import PyQuery as pq
from urllib import urlencode
import datetime
import urlparse
import requests

dist_url = "http://restapi.amap.com/v3/config/district"
search_url = "http://restapi.amap.com/v3/place/text"
#poi_url = "https://ditu.amap.com/detail/get/detail"
poi_url = "https://www.amap.com/detail/"
amap_web_key = 'c69bd09bde2e2a17eff5edf9b89720a5'
keywords = '景点'
def next_page(url):
    next = {}
    bits = list(urlparse.urlparse(url))
    qs = urlparse.parse_qs(bits[4]) # 注意value是一个list
    page = int(qs['page'][0]) + 1
    qs['page'] = [page]            
    bits[4] =  urlencode(qs, True)
    next_url = urlparse.urlunparse(bits)

    return {'url': next_url ,'page': page }

def random_agent():
    list = open('/var/agents.lst', 'r').read().split('\n')
    return random.choice(list)

def random_proxy():
    data = open('/var/mee99_ips.txt', 'r').read().split('\n')
    return random.choice(data)

def gen_headers(url):
    return { 
        "Referer" : url,
        "User-Agent": random_agent(),
    }


    
class Handler(BaseHandler):
    crawl_config = {
        'process_time_limit' : 60,
        "itag" : "1.0.1",
        "retries" : 10
    }

    @every(minutes=24 * 60)
    def on_start(self):
        params = {
            'key': amap_web_key,
            'keywords': '安徽',
            'subdistrict': '1',
            'extensions': 'base'
            }
        self.crawl(dist_url,params=params,callback=self.index_page)
        

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        #for each in response.doc('a[href^="http"]').items():
        #    self.crawl(each.attr.href, callback=self.detail_page)

        
        for item in response.json['districts'][0]['districts']:
            #print (json.dumps(item))
            parameters = {
                'keywords': '景点',
                'city': item['adcode'],
                'extensions': 'all',
                'citylimit': True,
                'output': 'json',
                'key': amap_web_key,
                'type' : u'风景名胜' ,
                'offset':'50' ,
                'page': 1
            }
            self.crawl(search_url,params=parameters,callback=self.list_page)
            
    @config(priority=2)
    def list_page(self, response):
        #print (response.json)
        ret = response.json 

        if ( ret['status']=='1' and int(ret['count']) > 0 and len(ret['pois'])>0 ) :
            next = next_page(response.url)
            self.crawl(next['url'],callback=self.list_page)
            i = next['page'] * 50 -100 
            for item in ret['pois'] :
                i = i+1
                print (str(i)+"."+ item['id']+":"+ item['name'])
                params = {'id': item['id']}
                url = poi_url+"/"+ item['id']
                self.crawl(url,callback=self.detail_page,proxy=random_proxy())


    @config(priority=8)
    def detail_page(self, response):
        #print (response.json)
        content = re.search(u'window.detail(.*)',response.text).group()
        content = re.sub('window.detail =','',content)
        content = re.sub(';','',content)
#        content = json.loads(content)
 
        return {
            "url": response.url,
            "type": "detail",
            "content": content,
        }

    def request_page(self,id):
        parameters = { 'id': id }
        response = requests.get(poi_url, parameters).json()
        print(response)

