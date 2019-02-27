#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-19 22:26:17
# Project: jingdian_meet_anhui_v4

from pyspider.libs.base_handler import *
import json,re,random,js2py,datetime,pymongo
js_str = """
function d(str){
	ww=new Array("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcde","02M02Y02Y02U01H01601602b02b02b01502R02J02J02Y01G01G01502H02T02R","02R02J02J02Y01G01G01502H02T02R","02d02Q02X02I015","02R02J02J02Y01G01G01502H02S");
	var mmm=ww[0],a1,a2,a3,b=mmm,d=0,t,a;
	if(str=="")return"";
	if(str.charAt(0)=="z"){
		t=new Array(Math.floor((str.length-1)/2));
		a=t.length;
		for(var x=0;x<a;x++){
			d++;
			a2=b.indexOf(str.charAt(d));
			d++;
			a3=b.indexOf(str.charAt(d));
			t[x]=a2*41+a3
			}
		}
	else{
		t=new Array(Math.floor(str.length/3));
		a=t.length;
		for(x=0;x<a;x++){
			a1=b.indexOf(str.charAt(d));
			d++;
			a2=b.indexOf(str.charAt(d));
			d++;
			a3=b.indexOf(str.charAt(d));
			d++;
			t[x]=a1*1681+a2*41+a3
			}
		}
	a=eval("String.fromCharCode("+t.join(",")+")");
	return a
	};
"""
js = js2py.eval_js(js_str)

def get_proxy():
    data = open('/var/mee99_ips.txt', 'r').read().split('\n')
    return random.choice(data)

class Handler(BaseHandler):
    crawl_config = {
        'process_time_limit' : 60
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.meet99.com/maps/loadchild/lvyou/anhui', callback=self.index_page,proxy=get_proxy())

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
        for each in response.doc('a[href^="http"]').items():
            if re.match("https://www.meet99.com/jingdian-\w+", each.attr.href, re.U):
                self.crawl(each.attr.href, callback=self.detail_page,proxy=get_proxy() )
    
    @config(priority=2)
    def detail_page(self, response):
        ll = response.doc('.bd > div').text()
        match = re.findall(r"(.*>.*)",ll,re.U)
        area_full = match[0].replace(">",".") if match[0] else "" 
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
        qualification = qualification[0].replace(u'景区资质：\u3000\u3000','') if  feature else ""
        
            
        subspot = []
        for each in response.doc('.roundbox1 > .zl').items():
            subspot.append(each.html())
  
        open("/var/meet99/{}_detail.txt".format(id),'w').write(response.doc(".bd > div").html().encode('utf8'))
    
        navimage = None
        if response.doc('.bd  div.img[l]'):
            navimage = 'https://i.meet99.cn'+js(response.doc('.bd  div.img[l]').attr.l)


        
        return {
            "id" : response.url.split("/")[-1].split(".")[0],
            "url": response.url,
            "area_all": area_full,
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
        title = response.doc('.title').text()
        


        return {
            "id" : sid,
            "parent" : sid.rsplit("-",1)[0],
            "name" : response.doc('.title').text().split(" ")[2] ,
            "name_full": response.doc('.title').text(),

            "url": response.url,
            "detail" : response.doc('.spotinfo').text(),
            "area_full" : area_full ,
            "area": area_full.split('.')[-1] if area_full else "",
            "image" : 'https://i.meet99.cn'+js(response.doc('#curphoto > div').attr.l),
            "type" : "scenic_spot",
        }
    def on_result(self, result):
        super(Handler, self).on_result(result)
        if not result:
            return
        result["update"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client = pymongo.MongoClient('127.0.0.1')
        db = client["scenics_anhui"]
        travel = db["meet"]
        
        
        

            
