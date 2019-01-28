#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-01-08 17:18:56
# Project: Bytravel

from pyspider.libs.base_handler import *
import re

sSpotSelector = "h1"
sAreaSelector = "#mainbao a"
sImageSelector = "article > div > a > img"
sFeatureSelector = ".f14b"
sContentSelector = "article"



class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://wap.bytravel.cn/', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if re.match("http://wap.bytravel.cn/Landscape/\w+", each.attr.href, re.U):
                self.crawl(each.attr.href, callback=self.detail_page)
            elif re.match("http://wap.bytravel.cn/\w+", each.attr.href, re.U):
                self.crawl(each.attr.href, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        aArea = response.doc(sAreaSelector).text().split(" ")
        sProvince = aArea[-3]
        if sProvince == u"首页" :
            sProvince = aArea[-2]
        sCity = aArea[-2]
        sArea = aArea[-1]
        sSpot = response.doc(sSpotSelector).text()
        sContentAll=response.doc(sContentSelector).text()
        sContent=sContentAll[0:sContentAll.find(u"下一景区：")]
        sImage = response.doc(sImageSelector).attr.src
        sFeature = response.doc(sFeatureSelector).text()
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
