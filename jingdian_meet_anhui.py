#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-28 11:04:12
# Project: meet_anhui_v1

from pyspider.libs.base_handler import *
import json,re,random,js2py,datetime,pymongo

js = js2py.eval_js(open("/var/meet99.js",'r').read())

def get_proxy():
    data = open('/var/mee99_ips.txt', 'r').read().split('\n')
    return random.choice(data)

class Handler(BaseHandler):
    crawl_config = {
        'process_time_limit' : 60,
        "itag" : "1.0.1"
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.meet99.com/maps/loadchild/lvyou/hefei', callback=self.index_page,proxy=get_proxy())

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        print (response.text)
        open('/var/meetlist.lst','a').write(json.dumps(response.text)+"\n")
        for each in response.json:
            if each.has_key('id') :
                self.crawl('https://www.meet99.com/maps/loadchild/lvyou/'+each["id"], callback=self.index_page,proxy=get_proxy())
            else:
                url = 'https://www.meet99.com/'+each['text'].split('"')[1]

                self.crawl(url, callback=self.list_page,proxy=get_proxy()  )
               

    @config(priority=2)
    def list_page(self, response):
        for each in response.doc('[t=""]').items():
            url = each('a[href^="http"]').attr.href
            gone = each('.ever span').text()
            want = each('.never span').text()
            self.crawl(url, callback=self.detail_page,save={"gone":gone,"want":want},proxy=get_proxy())
    
    @config(priority=2)
    def detail_page(self, response):
        ll = response.doc('.bd > div').text()
        match = re.findall(r"(.*>.*)",ll,re.U)
        area_full = match[0].replace(">",".") if match[0] else "" 
        area_list = area_full.split(".")
        area_full = '.'.join(area_list[0:4]) if len(area_list)>4 else area_full
        
        for each in response.doc('.roundbox1 > .zl > a').items():
            #scenic_spot
            self.crawl(each.attr.href, callback=self.detail_page_sub,proxy=get_proxy())
            
            
        sid = response.url.split('/')[-1].split('.')[0]
        detail = []
        for each in response.doc('.bd > div').items():
            s = each.html().replace('<h2>','$$$')
            s2 = re.sub(r'<.*?>','',s)
            s3 = s2.split('$$$')
            s4 = [i for i in s3 if i != '']
            detail += s4
            
        summary = [ s for s in detail if u"景区简介：" in s ]
        summary = summary[0].replace(u'景区简介：\u3000\u3000','') if  summary else ""
        
        feature = [ s for s in detail if u"景区特色：" in s ]
        feature = feature[0].replace(u'景区特色：\u3000\u3000','') if  feature else ""
        feature = feature.split(u"从您位置到")[0]
        
        qualification = [ s for s in detail if u"景区资质：" in s ]
        qualification = qualification[0].replace(u'景区资质：\u3000\u3000','') if  qualification else ""
        
            
        subspot = []
        for each in response.doc('.roundbox1 > .zl').items():
            subspot.append(each.html())
    
        navimage = None
        if response.doc('.bd  div.img[l]'):
            navimage = 'https://i.meet99.cn'+js(response.doc('.bd  div.img[l]').attr.l)

        if  response.doc(".bd > div").html() :
            open("/root/anhui_meet/{}_detail.txt".format(sid),'w').write(response.doc(".bd > div").html().encode('utf8'))

        
        return {
            "id" : response.url.split("/")[-1].split(".")[0],
            "gone" : int(response.save["gone"]),
            "want" : int(response.save["want"]),
            "url": response.url,
            "area_full": area_full,
            "summary" : summary,
            "feature" : feature,
            "qualification": qualification,
            "img": 'https://i.meet99.cn'+js(response.doc('#curphoto > div').attr.l),
            "navimage": navimage if (navimage) else "", 
            "name":response.doc(".title").text().split(u"旅游")[0],
            "subspot": subspot,
            "detail": detail,
            "type": "scenic_area",
            "area": area_full.split('.')[-1] if area_full else ""
        }
    
    @config(priority=2)

    @config(priority=2)
    def detail_page_sub(self, response):

        sid = response.url.split("/")[-1].split(".")[0]
            
        ll = response.doc('.bd > div').text()
        match = re.findall(r"(.*>.*)",ll,re.U)
        area_full = match[0].replace(">",".") if match[0] else "" 
        area_list = area_full.split(".")

        area_full = '.'.join(area_list[0:4]) if len(area_list)>4 else area_full
        
        title = response.doc('.title').text().split(u"（")

        return {
            "id" : sid,
            "parent" : sid.rsplit("-",1)[0],
            "name_full": title[0].replace(u"旅游攻略","") if title else "" ,
            "name" : title[0].split(" ")[-1] if title[0] else "" ,

            "url": response.url,
            "detail" : response.doc('.spotinfo').text(),
            "area_full" : area_full ,
            "area": area_full.split('.')[-1] if area_full else "",
            "image" : 'https://i.meet99.cn'+js(response.doc('#curphoto > div').attr.l),
            "type" : "scenic_spot",
            "sort" : response.doc('.title > span').text()
        }
    def on_result(self, result):
        super(Handler, self).on_result(result)
        if not result:
            return
        result["update"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client = pymongo.MongoClient('127.0.0.1')
        db = client["scenics_hefei"]
        travel = db["meet"]
        travel.update({'id': result.get('id')}, {'$set': result},True,False)
    

            
