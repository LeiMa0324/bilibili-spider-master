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
import math


# 代理服务器
proxyHost = "proxy.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = "HHV0AG22S43L45FD"
proxyPass = "AF85C01E36506837"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}


def datetime_to_timestamp_in_milliseconds(d):
    current_milli_time = lambda: int(round(time.time() * 1000))
    return current_milli_time()

reload(sys)



head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
}

#?mid=20779567&pagesize=30&tid=0&page=1&keyword=&order=senddate

'''
返回的是当页的 video，并不是所有的,
需要做一个 for 循环遍历所有 page
'''
#发送请求
def VideoRequest(mid,pagenum):
    payload={
    'mid':mid,
    'pagesize':'100',
    'tid':'0',
    'page':pagenum,
    'keyword':'',
    'order':'senddate'}
    url='http://space.bilibili.com/ajax/member/getSubmitVideos'

    VideoRequestList=[]
    #发送请求
    videocJson = requests.get(url,params=payload, headers=head,proxies = proxies).content
    print videocJson

    avDict = json.loads(videocJson)
    #校验Json数据
    statusJson = avDict['status'] if 'status' in avDict.keys() else False
    if statusJson == True:
        #json中有数据
        if 'data' in avDict.keys():
            #每一页的视频列表与视频总个数
            if avDict['data']['count']>0:
                VideoRequestList.append(avDict['data']['count'])
                VideoRequestList.append(avDict['data']['vlist'])
                return VideoRequestList
            else:
                print "该用户视频数为0"
        else:
            print 'no data'
    else:
        print 'NoJson'



#返回某个用户的所有视频列表
def GetVideoSource(mid):
    pagecount=0
    pagenum=1
    #视频分页列表，其中每一项都是每一页的视频列表
    VideoPageAllList=[]
    #视频分条列表
    VideoList=[]
    #请求第一页
    VideoPageOneList=VideoRequest(mid,str(pagenum))
    if VideoPageOneList!=None:
        VideoPageAllList.append(VideoPageOneList[1])
        #获取总页数
        pagecount=math.ceil(int(VideoPageOneList[0])/100.0)
        #遍历所有页
        while pagenum!=pagecount:
            pagenum +=1
            VideoPageAllList.append(VideoRequest(mid,pagenum)[1])
        #整理video数据
        for i in range(0,len(VideoPageAllList)):
            for j in range(0,len(VideoPageAllList[i])):
                VideoList.append(VideoPageAllList[i][j])
        print "获取用户%s共视频%s条" %(mid,len(VideoList))
        #每个video检查Tag
        getTags(VideoList)
    else:
        print "该用户%s没有视频数据"% mid
#获取tag列表
def getTags(VideoList):

    VideoListlocal = VideoList
    tagList4Page=[]
    url="http://api.bilibili.com/x/tag/archive/tags"
    payload={
        'jsonp':'jsonp'
    }
    #对每一个视频处理
    for i in range(0,len(VideoListlocal)):
        payload['aid']=VideoListlocal[i]['aid']
        tagJson = requests.get(url,params=payload,headers=head,proxies = proxies).content
        tgDict = json.loads(tagJson)
        #删除不需要的键值
        del VideoListlocal[i]['author']
        del VideoListlocal[i]['description']
        del VideoListlocal[i]['hide_click']
        del VideoListlocal[i]['pic']
        del VideoListlocal[i]['subtitle']
        if VideoListlocal[i]['play']=="--":
            VideoListlocal[i]['play']= 0
        VideoListlocal[i]['created']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(VideoListlocal[i]['created']))
        #单个视频的tag列表
        tagList=[]
        if 'data' in tgDict.keys():
            #对于每一个tag
            tagDictList=tgDict['data']
            #某个视频的tag列表可能为空
            if tagDictList:
                for k in range(0,len(tagDictList)):
                    tag_id = tagDictList[k]['tag_id']
                    tag_name = tagDictList[k]['tag_name']
                    tag_type = tagDictList[k]['type']
                    tag_content = tagDictList[k]['content']
                    tag_ctime = tagDictList[k]['ctime']
                    tag_use = tagDictList[k]['count']['use']
                    tag_atten = tagDictList[k]['count']['atten']

                    tag_ctime_format = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tag_ctime))
                    tag=[tag_id,tag_name,tag_type,tag_content,tag_ctime_format,tag_use,tag_atten]
                    tagList4Page.append(tag)
                    tagList.append(str(tag_id))
                string =','.join(tagList)
                VideoListlocal[i]['tags'] =string
                # print "第%d条视频%d的tag列表为：%r" % (i,VideoListlocal[i]['aid'],tagList)
            else:
                VideoListlocal[i]['tags']=''
        else:
            VideoListlocal[i]['tags']=''
    '''删除tag列表中的重复项
    '''
    for tag in tagList4Page:
        while tagList4Page.count(tag)>1:
            del tagList4Page[tagList4Page.index(tag)]

    print "该用户共tag%d条" % len(tagList4Page)
    #将tagListNew和视频插入表
    InsertTagsandVideo2DB(tagList4Page,VideoListlocal)



#视频数据和tag插入数据库
def InsertTagsandVideo2DB(tagListNew,VideoListlocal):
    conn = pymysql.connect(host=dbconfig["ip"], user=dbconfig["user"], passwd=dbconfig["passwd"], charset='utf8')
    tagSavedcount=0
    tagrepeated=0
    try:
        cur = conn.cursor()
        conn.select_db(dbconfig["db"])
        #插入视频数据
        sql="INSERT INTO bilibili_video_info(aid, comment,copyright,created,favourites,length,mid,play,review,title,typeid,video_review,tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        tmp=[]
        for i in range(0, len(VideoListlocal)):
            data = [VideoListlocal[i]['aid'],VideoListlocal[i]['comment'],VideoListlocal[i]['copyright'],VideoListlocal[i]['created'],VideoListlocal[i]['favorites'],
                 VideoListlocal[i]['length'],VideoListlocal[i]['mid'],VideoListlocal[i]['play'],VideoListlocal[i]['review'],VideoListlocal[i]['title'],
                 VideoListlocal[i]['typeid'],VideoListlocal[i]['video_review'],VideoListlocal[i]['tags']]
            tmp.append(data)
        cur.executemany(sql,tmp)
        # conn.commit()
        print "用户：%s视频：%s条已存入数据库" %(VideoListlocal[0]['mid'],len(VideoListlocal))
        #插入tag数据
        for i in range(0,len(tagListNew)):
        #检查tag是否已存在
            cur.execute("select count(*) from bilibili_tags where tagid=%s",tagListNew[i][0])
            record=cur.fetchone()[0]
            if record==1:
                print "该tag已存在！tagid:%s" % tagListNew[i][0]
                tagrepeated +=1
            else:
                cur.execute('INSERT INTO bilibili_tags(tagid,tagname,tagtype,tagcontent,tagctime,taguse,tagatten) VALUES (%s,%s,%s,%s,%s,%s,%s)', tagListNew[i])
                tagSavedcount +=1
        print "用户：%s有%d条已存在的tag，%d条已存入数据库" %(VideoListlocal[0]['mid'],tagrepeated,tagSavedcount)
        conn.commit()
        cur.close()
    except Exception,e:
        print e
    finally:
        conn.close()

dbconfig={}
with open("dbconfig.txt","rb") as config:

    con=config.readlines()
    dbconfig["ip"]=con[0].replace("ip=","").replace("\r\n","")
    dbconfig["user"]=con[1].replace("user=","").replace("\r\n","")
    dbconfig["passwd"]=con[2].replace("passwd=","").replace("\r\n","")
    dbconfig["db"]=con[3].replace("db=","").replace("\r\n","")
    dbconfig["maxid"]=con[4].replace("maxid=","").replace("\r\n","")


