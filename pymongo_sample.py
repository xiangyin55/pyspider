#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-03-30 09:20:41
# Project: IvskyDemo
 
from pyspider.libs.base_handler import *
from pymongo import MongoClient
# 向mongodb中插入数据的类
class MongoWriter(object):
 
    def __init__(self):
        # 构造对象
        self.client = MongoClient()
        # 获取数据库
        db = self.client.imgs
        # 获取集合(表)
        self.imgs = db.imgs
 
    def insert_result(self, result):
 
        if result:
            # 向mongodb中插入数据
            self.imgs.insert(result)
 
    def __del__(self):
        # 关闭数据库连接
        self.client.close()
 
 
class Handler(BaseHandler):
    # 构造对象
    mongo = MongoWriter()
 
    # 准备请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Host': 'www.ivsky.com',
        'Cookie': 'Hm_lvt_862071acf8e9faf43a13fd4ea795ff8c=1520298270,1520557723,1521015467,1522372414; BDTUJIAID=d4090b1fdf20d8f75ec2d25014d87217; Hm_lpvt_862071acf8e9faf43a13fd4ea795ff8c=1522372461; statistics_clientid=me',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
    }
 
    crawl_config = {
    }
 
    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(
            'www.ivsky.com/tupian/',
            callback=self.big_categray,
            headers=self.headers
        )
 
    @config(age=10 * 24 * 60 * 60)
    def big_categray(self, response):
        # for循环遍历找到的所有标签
        for each in response.doc('.tpmenu>li>a').items():
            # 创建一个新的爬取任务
            self.crawl(
                # 获取标签的href属性值,把属性值作为url创建新任务
                each.attr.href,
                callback=self.small_categray,
                # save 可以将数据传递到下一个回调函数中,类似于scrapy中的meta
                save={'big_cate': each.text()}
 
            )
        # .page-next
 
    def small_categray(self, response):
        '''
        解析小分类
        :param response:
        :return:
        '''
        save = response.save
        # 找到小分类
        for each in response.doc('.sline>div>a').items():
            # 将小分类存储到save中
            save['small_cate'] = each.text()
            # 创建新的爬取任务
            self.crawl(
                each.attr.href,
                callback=self.list_page,
                save=save,
                headers=self.headers
            )
 
    def list_page(self, response):
        '''
        解析列表
        :param response:
        :return:
        '''
        # 把save取出来
        save = response.save
        # 找到当前页所有图片的详细地址
        for each in response.doc('.pli>li>div>a').items():
            # 创建一个新的爬取任务
            self.crawl(
                each.attr.href,
                callback=self.detail_page,
                save=save,
                headers=self.headers
            )
 
        # 翻页
 
    def detail_page(self, response):
        '''
        解析图片地址
        :param response:
        :return:
        '''
        # 找到指定标签拥有某个属性值的标签
        # 标签[属性名="属性值"]
        for each in response.doc('img[id="imgis"]').items():
            # 返回需要保存的数据,返回一个字典
            return {
                'url': each.attr.src,
                'title': each.attr.src.split('/')[-1],
                'big_cate': response.save['big_cate'],
                'small_cate': response.save['small_cate']
            }
    def on_result(self, result):
        # 执行插入数据的操作
        self.mongo.insert_result(result)
        # 调用原有的数据存储
        super(Handler, self).on_result(result)
 
 
