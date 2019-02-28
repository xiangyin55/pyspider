#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-19 22:26:17
# Project: jingdian_bytravel_anhui_v1

from pyspider.libs.base_handler import *
import json,re,random,datetime,pymongo

def get_proxy():
    data = open('/var/mee99_ips.txt', 'r').read().split('\n')
    return random.choice(data)

class Handler(BaseHandler):
    crawl_config = {
        'process_time_limit' : 60
    }

    @every(minutes=24 * 60)
    def on_start(self):
        #self.crawl('http://wap.bytravel.cn/', callback=self.index_page)
        self.crawl('http://wap.bytravel.cn/view/index120_list.html', callback=self.list_page)
        
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('li > a').items():
            open ('/var/bytravel_list_anhui.txt','a').write(each.attr.href+"\n")
            if re.match("http://wap.bytravel.cn/view/\w+", each.attr.href, re.U):
                self.crawl(each.attr.href.replace(".html","_list.html"), callback=self.list_page)
               

    @config(priority=2)
    def list_page(self, response):
        for each in response.doc("nav a").items():
            if u'下一页' in each.text():
                next = each.attr.href
                print (next)
                self.crawl(next, callback=self.list_page)
        for each in response.doc('#titlename a').items():
            self.crawl(each.attr.href, callback=self.detail_page)
            
        
    
    @config(priority=2)
    def detail_page(self, response):

        area_s = response.doc("#mainbao a").text()
        area_full = area_s.replace(" ",".").replace(u"首页",u"中国").replace(u"旅游",u"") if area_s else ""
        
        sid = response.url.replace(u'http://wap.bytravel.cn/Landscape/','').replace('/','-').replace('.html','')

            
        return {
            "id": sid,
            "url": response.url,
            "name": response.doc('h1').text(),
            "summary":  response.doc('article').text()[0:response.doc('article').text().find(u"下一景区：")],
            "area_full" :  area_full,
            "area" : area_full.split(".")[-1] if area_full else "",
            "image": response.doc('article > div > a > img').attr.src,
            "qualification":  response.doc('.f14b').text()    
        }
    
    def on_result(self, result):
        super(Handler, self).on_result(result)
        if not result: return
        result["update"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client = pymongo.MongoClient('127.0.0.1')
        db = client["scenics_anhui"]
        travel = db["bytravel"]
        try:
            travel.update({'id': result.get('id')}, {'$set': result},True,False)
        except Exception as e:
            print (e)
            print ("Error")
