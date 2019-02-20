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
        self.crawl('https://www.meet99.com/maps/loadchild/lvyou', callback=self.index_page,proxy=get_proxy())

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        print (response.text)
        open('/var/meetlist.lst','a').write(json.dumps(response.text)+"\n")
        for each in response.json:
            if each.has_key('id') :
                self.crawl('https://www.meet99.com/maps/loadchild/lvyou/'+each["id"], callback=self.index_page,proxy=get_proxy())
            else:
                url = 'https://www.meet99.com/'+each['text'].split('"')[1]
                self.crawl(url, callback=self.list_page,proxy=get_proxy())
               

    @config(priority=2)
    def list_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if re.match("https://www.meet99.com/jingdian-\w+", each.attr.href, re.U):
                self.crawl(each.attr.href, callback=self.detail_page , proxy=get_proxy())
    
    @config(priority=2)
    def detail_page(self, response):
        detail = []
        for each in response.doc('.bd > div').items():
            s = each.html().replace('<h2>','$$$')
            s2 = re.sub(r'<.*?>','',s)
            s3 = s2.split('$$$')
            s4 = [i for i in s3 if i != '']
            detail += s4
        subspot = []
        for each in response.doc('.roundbox1 > .zl').items():
            subspot.append(each.html())
            
        return {
            "subspot": subspot,
            "img": response.doc('#curphoto > img').attr.src,
            "detail": detail,
            "nav": response.doc(".loc").text(),
            "spot_name":response.doc(".title").text(),
            "spotinfo":response.doc(".spotinfo").text(),
            "detailhtml":response.doc(".bd > div").html(),
            "mulu":response.doc(".roundbox").text(),
            "url": response.url,
            "title": response.doc('title').text(),
        }
