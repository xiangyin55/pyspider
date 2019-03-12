# -*- encoding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        模块2
# Purpose:
#
# Author:      Administrator
#
# Created:     12/03/2019
# Copyright:   (c) Administrator 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import requests
import json
import xlwt

amap_web_key = 'c69bd09bde2e2a17eff5edf9b89720a5'
poi_search_url = "http://restapi.amap.com/v3/place/text"
poi_boundary_url = "https://ditu.amap.com/detail/get/detail"



# 单页获取pois
def getpoi_page(region, query, page):

    parameters = {
        'keywords': query ,
        'city': region ,
        'extensions': 'all',
        'citylimit': True,
        'output': 'json',
        'key': amap_web_key,
        'type' : u'风景名胜' ,
        'offset':'25' ,
        'page': page
    }

    response = requests.get(poi_search_url, parameters)
    rest = response.json()
    return rest




# 根据城市名称和分类关键字获取poi数据
def getpois(cityname, keywords):
    i = 1
    poilist = []
    while True:  # 使用while循环不断分页获取数据
        result = getpoi_page(cityname, keywords, i)
        if result['count'] == '0':
            break
        hand(poilist, result)
        i = i + 1
    return poilist


#根据id获取边界数据
def getBounById (id):

    parameters = { 'id': id }
    response = requests.get(poi_boundary_url, parameters)
    data = response.json()
    rest = data['data']['spec']
    if len(rest) ==1:
        return []
    if 'mining_shape' in rest:
        return rest['mining_shape']['shape']


#数据写入csv 文件
def wirte_2_csv(pois, cityname, classfield):
    wf= open(r'' + cityname + "_" + classfield + '.csv','w',encoding='utf-8')
    for l in pois:
        if '风景名胜' in l['type']:
            wf.write(json.dumps(l,ensure_ascii = False)+"\n")
    wf.close()


# 将返回的poi数据装入集合返回
def hand(poilist, result):
    # result = json.loads(result)  # 将字符串转换为json
    pois = result['pois']
    for i in range(len(pois)):
        poilist.append(pois[i])



#TODO 需要爬取的POI所属的城市名，以及分类名. (中文名或者代码都可以，代码详见高德地图的POI分类编码表)
cityname = "340100"
classfiled = "三河古镇"


# 获取城市分类数据

pois = getpois(cityname, classfiled)

# 将数据写入csv
wirte_2_csv(pois, cityname, classfiled)
print('写入成功')


#根据获取到的poi数据的id获取边界数据
dataList = getBounById('B02270I45I')
print(type(dataList))

print(str(dataList))

