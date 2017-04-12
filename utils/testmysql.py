#coding:utf-8
import pymysql

def insertuser(userlist):
    try:
        print "connecting"
        conn = pymysql.connect(host='127.0.0.1', user='root', passwd='root', charset='utf8')
        print "connected"
        cur = conn.cursor()
        # cur.execute('create database if not exists python')
        conn.select_db('123')
        #检查是否该用户已存在
        cur.execute("select count(*) from bilibili_user_info where id=%s",userlist[0])
        record=cur.fetchone()[0]
        if record==1:
            print "用户在数据库中已存在！mid:%s" % userlist[0]
        else:
            cur.execute('INSERT INTO bilibili_user_info VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            userlist)
            print "用户成功存入数据库，mid：", userlist[0]
            #计数
            print "已存入%d个用户"
    except Exception:
        print("Mysql Error")

insertuser(123)