#encoding=utf8
import urllib2
from bs4 import BeautifulSoup
import urllib
import socket
import requests
import json
import random
import pymysql
from multiprocessing.dummy import Pool as ThreadPool
import sys
import datetime
import time
from imp import reload

User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'


head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
    'Referer':'http://space.bilibili.com/'+str(random.randint(9000,10000))+'/',
    'Host': 'space.bilibili.com',
    'Connection': 'keep-alive',
    'Content-Length': '28',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'http://space.bilibili.com',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}


proxies = [
'http://125.88.74.122:85',
'http://125.88.74.122:84',
'http://125.88.74.122:82',
'http://125.88.74.122:83',
'http://125.88.74.122:81',
'http://123.57.184.70:8081',
'http://61.191.173.31:808',
'http://221.216.94.77:808',
'http://218.2.184.37:8118'
]

def datetime_to_timestamp_in_milliseconds(d):
    current_milli_time = lambda: int(round(time.time() * 1000))
    return current_milli_time()

reload(sys)

payload = {
    '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now()),
    'mid': "197521"
}

def validateIp(proxies):
    url = "http://space.bilibili.com/ajax/member/GetInfo"
    socket.setdefaulttimeout(3)
    for i in range(0,len(proxies)):
        try:
            ip = proxies[i]
            proxy_temp = {"http":ip}
            response= requests.session().post('http://space.bilibili.com/ajax/member/GetInfo', headers=head,  data=payload,proxies = proxy_temp)
            print response.text
            print "代理成功！"+ proxies[i]
        except Exception,e:
            continue



if __name__ == '__main__':
    validateIp(proxies)