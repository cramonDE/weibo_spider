#!/usr/bin/python
#coding:utf-8
#
import sys
import pymysql
import re

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

conn = pymysql.connect(host="127.0.0.1", port=3306,
user='root', passwd='xiaomixm', db='spider', charset='utf8mb4')
cur = conn.cursor()
name = '梓丰'
studentID = '想想这些'
# cur.execute("INSERT INTO test (姓名, 学好) VALUES (%s, %s)", (name, studentID))
name = ['博主昵称', '博主主页', '微博内容', '发布时间', '转发', '评论', '赞']
#建表
# sql = 'CREATE TABLE '+ studentID + '(博主昵称 char(16), 博主主页 char(16), 微博内容 char(16), 发布时间 char(16), 转发 int(8), 评论 int(8), 赞 int(8)) character set = utf8'
# cur.execute(sql)

sql = 'INSERT  INTO ' + '想想这些' + '(博主昵称, 博主主页, 微博内容, 发布时间, 转发, 评论, 赞) VALUES ('
topic = ['11122qqq', 'zhuye', '吃到传说中的天价鳇鱼鱼🤔现鱼现在已经', 'shijian', '1', '2', '3']

for i in range(len(topic)):
    if i == 0:
        sql += '\'' + topic[i]+ '\''
    else:
        sql += ', \'' + topic[i]+ '\''

sql += ')'



try:
    cur.execute(sql)
    cur.connection.commit()
except Exception as e:
    print e



print sql
cur.close()
conn.close()

# 哈尔滨天价鱼
# SELECT DISTINCT * FROM `哈尔滨天价鱼` ORDER BY `转发`*0.5 + `粉丝数`*0.35 + `评论`*0.1 + `赞`*0.05 DESC
