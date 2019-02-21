#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-19 22:26:17
# Project: jindian

from pyspider.libs.base_handler import *
import json,re,random

def get_proxy():
    data = open('/var/mee99_ips.txt', 'r').read().split('\n')
    return random.choice(data)

class Handler(BaseHandler):
    crawl_config = {
        'process_time_limit' : 60
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://wap.bytravel.cn/', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('li > a').items():
            open ('/var/bytravel_list.txt','a').write(each.attr.href+"\n")
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

        aArea = response.doc("#mainbao a").text().split(" ")
        sProvince = aArea[-3]
        if sProvince == u"首页" :
            sProvince = aArea[-2]
        sCity = aArea[-2]
        sArea = aArea[-1]
        sSpot = response.doc('h1').text()
        sContentAll=response.doc('article').text()
        sContent=sContentAll[0:sContentAll.find(u"下一景区：")]
        sImage = response.doc('article > div > a > img').attr.src
        sFeature = response.doc('.f14b').text()
        sFeature = sFeature[len(sSpot)+1:-1]

        return {
            "Province" : sProvince,
            "City" : sCity,
            "Area" :  sArea,
            "Spot" :  sSpot,
            "Image": sImage,
            "Feature":  sFeature,
            "Content":  sContent,
            "url": response.url,
            "title": response.doc('title').text(),
        }
