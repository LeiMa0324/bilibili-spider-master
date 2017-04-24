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
import VideoTest

#初始化计数器
count=[0]



def datetime_to_timestamp_in_milliseconds(d):
    current_milli_time = lambda: int(round(time.time() * 1000))
    return current_milli_time()

reload(sys)


#载入userAgent
def LoadUserAgents(uafile):

    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas

uas = LoadUserAgents("user_agents.txt")
head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://space.bilibili.com/45388',
    'Origin': 'http://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}



#获取数据函数
def getsource(url):
    #线程睡眠(30-60)的随机秒数
    time.sleep(random.choice(range(1,5)))
    try:
        payload = {
            '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now()),
            'mid': url.replace('http://space.bilibili.com/ajax/member/GetInfo?mid=', '')
        }
        #随机选择useragent
        ua = random.choice(uas)
        head = {'User-Agent':ua,
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

        s=requests.session()
        s.keep_alive = False
        response= s.post('http://space.bilibili.com/ajax/member/GetInfo', headers=head,  data=payload,
                         # proxies = tempproxy
                         )
        jscontent =response.text

        print"-------------------------------------------------------------"+"\n"
        # print responseCode
        if response.status_code ==200:
            print "请求成功，获取用户信息...mid:%s "%(payload["mid"])
            # print ("request success,getting user mid:"+payload["mid"]+"\n"+ jscontent)
            '''
            检查403表中是否已有该数据，如果有，则删除
            '''
            #处理json数据
            processjson(jscontent)
            #获取视频与tag列表
            VideoTest.GetVideoSource(payload["mid"])

        else:
            print "请求失败，用户mid %s 错误码：%s "% (payload["mid"],response.status_code,
                                                   # tempproxy
                                                   )
            '''
            检查403表中是否有该数据，如果没有，则插入
            '''
            #将错误id存入数据库
            user2file(payload["mid"])
            #如果被403则线程阻塞，随机睡眠（60-120s）

            time.sleep(random.choice(range(30,120)))
    except ProxyError:
        print "代理异常:"
        time.sleep(random.choice(range(60,100)))

    except Exception,e:
        traceback.print_exc(file=sys.stdout)
    #打印当前时间
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))


#处理json数据
def processjson(jscontent):
    time2 = time.time()
    try:
        jsDict = json.loads(jscontent)
        statusJson = jsDict['status'] if 'status' in jsDict.keys() else False
        if statusJson == True:
            if 'data' in jsDict.keys():
                jsData = jsDict['data']
                mid = jsData['mid']
                name = jsData['name']
                sex = jsData['sex']
                face = jsData['face']
                coins = jsData['coins']
                regtime = jsData['regtime'] if 'regtime' in jsData.keys() else 0
                spacesta = jsData['spacesta']
                birthday = jsData['birthday'] if 'birthday' in jsData.keys() else 'nobirthday'
                place = jsData['place'] if 'place' in jsData.keys() else 'noplace'
                description = jsData['description']
                article = jsData['article']
                fans = jsData['fans']
                friend = jsData['friend']
                attention = jsData['attention']
                sign = jsData['sign']
                attentions = jsData['attentions']
                level = jsData['level_info']['current_level']
                exp = jsData['level_info']['current_exp']
                #增加播放数
                playnum = jsData['playNum'] if 'playNum' in jsData.keys() else 0


                regtime_format = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(regtime))
                #将要存入的数据设置为列表
                userlist=[mid, mid, name, sex, face, coins, regtime_format, spacesta, birthday, place, description,
                article, fans, friend, attention, sign, str(attentions), level, exp,playnum]
                #插入用户数据
                insertuser(userlist)
            else:
                print('no data now')

        else:
            print"该用户没有json数据 " , url
    except ValueError:
        print('decoding json has failed')
        print(jscontent)

#插入用户数据到mysql数据库
def insertuser(userlist):
    conn = pymysql.connect(host=dbconfig["ip"], user=dbconfig["user"], passwd=dbconfig["passwd"], charset='utf8')
    try:
        cur = conn.cursor()
        conn.select_db(dbconfig["db"])
        #检查是否该用户已存在
        cur.execute("select count(*) from bilibili_user_info where id=%s",userlist[0])
        record=cur.fetchone()[0]
        if record==1:
            print "用户在数据库中已存在！mid:%s" % userlist[0]
        else:
            cur.execute('INSERT INTO bilibili_user_info VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            userlist)
            print "用户成功存入数据库，mid：", userlist[0]
            #计数
            count[0] +=1
            print "已存入%d个用户" % count[0]
    except Exception:
        print("Mysql Error")
        #关闭数据库
    finally:
        conn.close()

#检查数据库中最后一条记录
def lastuserindb():
      conn = pymysql.connect(host=dbconfig["ip"], user=dbconfig["user"], passwd=dbconfig["passwd"], charset='utf8')
      lastuser=[0]
      try:

          cur = conn.cursor()
          # cur.execute('create database if not exists python')
          conn.select_db(dbconfig["db"])
          #检查是否该用户已存在
          cur.execute("select max(id) from bilibili_user_info;")
          lastuser[0] = cur.fetchone()[0]

      except Exception:
        print "插入失败"
      finally:
          #关闭数据库
        conn.close()
        if lastuser[0] :
            lastuser[0]=lastuser[0]
        else:
            lastuser[0]=0
        return  lastuser[0]

#存入错误用户id到数据库
def user2file(userid):
      conn = pymysql.connect(host=dbconfig["ip"], user=dbconfig["user"], passwd=dbconfig["passwd"], charset='utf8')
      try:
          cur = conn.cursor()
          conn.select_db(dbconfig["db"])
          cur.execute("insert into fail_users(mid) values (%s);",userid)
      except Exception:
        print "插入403用户失败"
      finally:
        conn.close()


time1 = time.time()

#原for循环
# for m in range(1691,2000): #26 ,1000
#     urls = []
#     for i in range(m*100, (m+1)*100):
#         url = 'http://space.bilibili.com/ajax/member/GetInfo?mid=' + str(i)
#         urls.append(url)

#程序开始，输入ip最后一位，链接数据库

dbconfig={}

with open("dbconfig.txt","rb") as config:

    con=config.readlines()
    dbconfig["ip"]=con[0].replace("ip=","").replace("\r\n","")
    dbconfig["user"]=con[1].replace("user=","").replace("\r\n","")
    dbconfig["passwd"]=con[2].replace("passwd=","").replace("\r\n","")
    dbconfig["db"]=con[3].replace("db=","").replace("\r\n","")
    dbconfig["maxid"]=con[4].replace("maxid=","").replace("\r\n","")

print(dbconfig)


lastuser =lastuserindb()

#选择数据库和文件中最大值
maxid=int(dbconfig["maxid"]) if int(dbconfig["maxid"])>int(lastuserindb()) else int(lastuserindb())


print"当前数据库中最大用户为：", maxid



'''
优化方案
'''

#一次获取100w个用户
for m in range(0,9999):
    urls = []
    for i in range(maxid+m*100,maxid+(m+1)*100):
        url= 'http://space.bilibili.com/ajax/member/GetInfo?mid=' + str(i)
        urls.append(url)

    #开启4个线程
    pool = ThreadPool(4)
    try:
        results = pool.map(getsource, urls)

    except Exception, e:
        # print 'ConnectionError'
        print e
        #用map函数代替for循环，开启多线程运行函数
        results = pool.map(getsource, urls)

    pool.close()
    pool.join()

#再次获取403数据