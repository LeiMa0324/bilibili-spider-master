# coding=utf-8

import requests
import json
import random
import pymysql
from multiprocessing.dummy import Pool as ThreadPool
import sys
import datetime
import time
from imp import reload
import traceback,sys
from requests.exceptions import ProxyError
import urllib

def datetime_to_timestamp_in_milliseconds(d):
    current_milli_time = lambda: int(round(time.time() * 1000))
    return current_milli_time()

reload(sys)



head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
}

#?mid=20779567&pagesize=30&tid=0&page=1&keyword=&order=senddate
payload={
    'mid':'20779567',
    #每页数据大小
    'pagesize':'100',
    #tid=0 默认查询所有主题的视频
    'tid':'0',
    #查询第几页
    'page':'1',
    'keyword':'',
    'order':'senddate'


}


url='http://space.bilibili.com/ajax/member/getSubmitVideos'
html = requests.get(url,params=payload, headers=head)
'''
返回的是当页的 video，并不是所有的,
需要做一个 for 循环遍历所有 page
'''

'''
返回视频json 格式：
aid:6179192
author:"梦亦星逝"
comment:18
copyright:"Original"
created:1473152119
description:"模型..."
favorites:235
hide_click:true
length:"04:53"
mid:20779567
pic:"http
play:"--"
review:14
subtitle:""
title:"【Haku-很可爱】不来系一发？"
typeid:25
video_review:18
'''
print html.content