#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-03-01 09:27:32
# Project: mfw_hefei_v2



from pyspider.libs.base_handler import *
import json
import re
import random
import js2py
import pymongo
from pyquery import PyQuery as pq
from urllib import urlencode
import datetime
    
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
        "User-Agent": random_agent(),
    }

class Handler(BaseHandler):
    crawl_config = {
        'process_time_limit' : 60,
        'itag' : "1.0.10" ,
    }


    @every(minutes=24 * 60)
    def on_start(self):
        poi = "10793"
        
        jdata = '{"iMddid":"'+poi+'","iPage":"1","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}';
        param = json.loads( jm( jdata ) )
        url = "https://www.mafengwo.cn/ajax/router.php"
        self.crawl(url,params=param,callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
   

        list_doc = pq(response.json["data"]["list"])  #print (list_doc.html())
        page_doc = pq(response.json["data"]["page"])  #print (page_doc.html())
        

        for d in list_doc('a').items():

            self.crawl("https://www.mafengwo.cn"+d.attr.href, callback=self.detail_page_poi,proxy=random_proxy())

        if  page_doc(".pg-next"):
            ipage = page_doc(".pg-next").attr("data-page")
            jdata = '{"iMddid":"10793","iPage":"'+ipage+'","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}';
            param = json.loads( jm( jdata ) )
            url = "https://www.mafengwo.cn/ajax/router.php"
            self.crawl(url,params=param,callback=self.index_page)
    #        self.crawl(url,params=param,callback=self.index_page,proxy=random_proxy())

    @config(priority=2)
    def detail_page_poi(self, response):
        
        poi = response.url.split('/')[-1].split('.')[0]   #

        img = response.doc(".pic-big > img").attr.src
        area = response.doc(".cur").text(),
  
            
        poiLocationApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiLocationApi?params={"poi_id":"'+poi+'"}'
        self.crawl(poiLocationApi, callback=self.detail_page_Location,headers=gen_headers(response.url))
        
        poiCommentListApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?params={"poi_id":"'+poi+'"}'
        self.crawl(poiCommentListApi, callback=self.detail_page_Comment,headers=gen_headers(response.url))
        
        poiSubPoiApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+poi+'","type":"3"}'
        self.crawl(poiSubPoiApi, callback=self.index_page_subpoi,headers=gen_headers(response.url),save={'parent':poi})
        
        if not response.doc(".mod-detail").html() is None :
            open("/var/mfwdata/{}_detail.txt".format(poi),'w').write(response.doc(".mod-detail").html().encode('utf8'))


        return {
            "poi": int(poi),

            "url": response.url,
            "area" : area[0].replace(u'景点','') if area else "",
            "name" : response.doc("h1").text(),
            "image": img.split('?')[0] if  img else "" ,
            "en_alias": response.doc(".en").text(),
            "summary": response.doc(".summary").text(),
            "address" : response.doc(".mhd > p").html(),
        }
    
    @config(priority=2)
    def detail_page_Location(self, response):
        

        poi_data = response.json["data"]["controller_data"]["poi"]
        poi_data["poi"] = poi_data['id']
        poi_data.pop("id")
        
        return  poi_data

        #{'table': 'scenic'，u'name': u'恭王府', u'is_cnmain': True, u'country_mddid': 21536, u'lat': 39.937295, u'lng': 116.386344, u'type': 3, u'id': 3506}

        
    @config(priority=2)
    def detail_page_Comment(self, response):
        

        comment_data = response.json["data"]
        poi = comment_data['controller_data']['poi_id']
        open("/var/mfwdata_anhui/{}_comment.txt".format(poi),'w').write(comment_data['html'].encode('utf8'))

        
    @config(priority=2)
    def detail_page_l(self, response):
        print (response.json)
        
        
    @config(age=10 * 24 * 60 * 60)
    def index_page_subpoi(self, response):
        print (response.json)
        parent = response.save['parent']

        result = response.json["data"]
        if result["html"] =="" :  return
        list_doc = pq(result["html"])
        for d in list_doc('a[href^="/poi"]').items():   
            self.crawl("https://www.mafengwo.cn"+d.attr.href, callback=self.detail_page_subpoi,save={'go':d.find('em').text(),'parent':parent},proxy=random_proxy())
#            self.crawl("https://www.mafengwo.cn"+d.attr.href, callback=self.detail_page_subpoi,save={'go':d.find('em').text(),'pid':pid},proxy=random_proxy())

        page_json = result['controller_data']
        if page_json['hasMore'] :
            page = page_json['curPage'] + 1
            poi = page_json['poi_id']
            poiSubPoiApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+str(poi)+'","type":3,"page":'+str(page)+'}'
            refer = "https://www.mafengwo.cn/poi/{}.html".format(str(poi))
            self.crawl(poiSubPoiApi, callback=self.index_page_subpoi,headers=gen_headers(refer),save={'parent':poi})

            
            
    @config(priority=2)
    def detail_page_subpoi(self, response):
        
        
        poi = response.url.split('/')[-1].split('.')[0]   #print (poi)
        img =  response.doc(".row-bg img").attr.src
        
        poiLocationApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiLocationApi?params={"poi_id":"'+poi+'"}'
        self.crawl(poiLocationApi, callback=self.detail_page_Location,headers=gen_headers(response.url))
        
        poiCommentListApi = 'http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?params={"poi_id":"'+poi+'"}'
        self.crawl(poiCommentListApi, callback=self.detail_page_Comment,headers=gen_headers(response.url))
        


        return {

            "poi": int(poi),
            "go" : int(response.save["go"]),
            "parent": int(response.save["parent"]),
            "url": response.url,
            "area" : response.doc(".cur").text(),
            "image": "" if  ( img is None) else img.split('?')[0] ,
            "name" : response.doc("h1").text(),
            "en_alias": response.doc(".en").text(),
            "summary" : response.doc(".mod-detail > div").text(),
            "address" : response.doc(".mhd > p").html(),
        }

    
    def on_result(self, result):
        super(Handler, self).on_result(result)
        if not result:
            return
        result["update"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client = pymongo.MongoClient('127.0.0.1')
        db = client["scenics_hefei"]
        poi = db["mfw"]
        poi.update({'poi': result.get('poi')}, {'$set': result},True,False)
        
