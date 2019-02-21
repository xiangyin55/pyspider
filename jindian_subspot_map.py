#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-19 22:26:17
# Project: jindian

from pyspider.libs.base_handler import *
import json,re,random,js2py
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
 
        for each in response.doc('.roundbox1 > .zl > a').items():
            self.crawl(each.attr.href, callback=self.detail_page_sub,proxy=get_proxy())
        

    @config(priority=2)
    def detail_page_sub(self, response):

        
            
        return {
            "id":response.url.split("/")[-1],
            "sub_detail":response.doc('.spotinfo').text(),
            "img": 'https://i.meet99.cn'+js(response.doc('#curphoto > div').attr.l),
            "url": response.url,
            "title": response.doc('.title').text(),
        }
