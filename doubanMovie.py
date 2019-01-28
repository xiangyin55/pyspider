#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-08-21 02:03:43
# Project: doubanMovie

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }
    headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.3.2.17331',
    'Referer': 'https://movie.douban.com',
    'Connection': 'keep-alive'
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://movie.douban.com/tag/#/', callback=self.index_page,headers=self.headers,timeout=180,fetch_type='js',js_script='''function(){ window.scrollTo(0,document.body.scrollHeight);}''')

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('li > span').items():
            if u'全部' not in each.text():
                for i in range(50):
                    tag='https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags='+each.text()+'&start='+str(20*i)
                    print (tag)
                    self.crawl(tag, callback=self.list_page,headers=self.headers,timeout=180)
    def list_page(self, response):
        for i  in range(20):
            List=response.json['data'][i]['url']
            self.crawl(List,callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('h1 > span').text(),
            "豆瓣评分":response.doc('.rating_num').text(),
            "评价人数":response.doc('.rating_sum span').text(),
            "豆瓣成员常用的标签":response.doc('.tags-body > a').text(),
            "people":response.doc('.actor a').text(),
            "剧情简介":response.doc('.related-info > .indent').text(),
            "img":response.doc('#mainpic img').attr('src')
        }
