#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-22 16:30:14
# Project: mfw_all

from pyspider.libs.base_handler import *
import json
import re
import random
import js2py
import pymongo
from pyquery import PyQuery as pq
from urllib import urlencode

jm = js2py.eval_js(open("/var/mfw.js",'r').read())

def random_agent():
    list = open('/var/agents.lst', 'r').read().split('\n')
    return random.choice(list)

def random_proxy():
    data = open('/var/mee99_ips.txt', 'r').read().split('\n')
    return random.choice(data)

def gen_headers(url):
    return { 
        "Referer" : url,
        'User-Agent': random_agent(),
    }

class Handler(BaseHandler):
    crawl_config = {
        'process_time_limit' : 60
    }


    @every(minutes=24 * 60)
    def on_start(self):
        
        jdata = '{"iMddid":"10065","iPage":"1","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}';
        param = json.loads( jm( jdata ) )
        url = "https://www.mafengwo.cn/ajax/router.php"
        self.crawl("{}?{}".format(url,urlencode(param)), callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):

        list_doc = pq(response.json["data"]["list"])  #print (list_doc.html())
        page_doc = pq(response.json["data"]["page"])  #print (page_doc.html())
        

        for d in list_doc('a').items():
            self.crawl("https://www.mafengwo.cn"+d.attr.href, callback=self.detail_page_poi)


        ipage = page_doc(".pg-next").attr("data-page")
        jdata = '{"iMddid":"10065","iPage":"'+ipage+'","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}';
        param = json.loads( jm( jdata ) )
        url = "https://www.mafengwo.cn/ajax/router.php"
        self.crawl("{}?{}".format(url,urlencode(param)), callback=self.index_page)
            


    @config(priority=2)
    def detail_page_poi(self, response):
        
        poi = response.url.split('/')[-1].split('.')[0]   #print (poi)
        
        poiLocationApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiLocationApi?params={"poi_id":"'+poi+'"}'
        self.crawl(poiLocationApi, callback=self.detail_page_l,headers=gen_headers(response.url))
        
        poiCommentListApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?params={"poi_id":"'+poi+'"}'
        self.crawl(poiCommentListApi, callback=self.detail_page_l,headers=gen_headers(response.url))
        
        poiSubPoiApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+poi+'"}'
        self.crawl(poiSubPoiApi, callback=self.index_page_subpoi,headers=gen_headers(response.url))


        return {
            "poi": poi,
            "url": response.url,
            "area" : response.doc(".cur").text(),
            "name" : response.doc("h1").text(),
            "en_alias": response.doc(".en").text(),
            "detail" : response.doc(".mod-detail").html(),
            "address" : response.doc(".mhd > p").html(),
        }
    
    @config(priority=2)
    def detail_page_l(self, response):
        print (response.json)

    @config(age=10 * 24 * 60 * 60)
    def index_page_subpoi(self, response):
        print (response.json)
        result = response.json["data"]
        list_doc = pq(result["html"])
        print (list_doc)

        page_json = result['controller_data']
        if page_json['hasMore'] :
            page = page_json['curPage'] + 1
            poi = page_json['poi_id']
            poiSubPoiApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+str(poi)+'","page":'+str(page)+'}'
            refer = "https://www.mafengwo.cn/poi/{}.html".format(str(poi))
            self.crawl(poiSubPoiApi, callback=self.index_page_subpoi,headers=gen_headers(refer))
        
