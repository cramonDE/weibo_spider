# coding=utf-8

import time
import datetime
import re
import os
import sys
import codecs
import shutil
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains

import pymysql
import random
from selenium.common.exceptions import TimeoutException


defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


driver = webdriver.Firefox()


def LoginWeibo(username, password):
    try:
        #输入用户名/密码登录
        print u'准备登陆Weibo.cn网站...'
        driver.get("http://login.sina.com.cn/")
        elem_user = driver.find_element_by_name("username")
        elem_user.send_keys(username) #用户名
        elem_pwd = driver.find_element_by_name("password")
        elem_pwd.send_keys(password)  #密码
        elem_sub = driver.find_element_by_xpath("//input[@class='W_btn_a btn_34px']")
        elem_sub.click()              #点击登陆 因无name属性

        time.sleep(3)

        print key, cookie[key]
        print u'登陆成功...'



def GetSearchContent(key):

    driver.set_page_load_timeout(5)
    try:
        driver.get("http://weibo.com/jlsgat?profile_ftype=1&is_all=1&is_search=1&key_word=304#_0")
    except Exception as e:
        driver.execute_script('window.stop()')

    initDatabase()
    time.sleep(2)

    handlePage()  #处理当前页面内容

def handlePage():
    global numOFItem
    numOFItem = 0
    while True:

        time.sleep(random.random() * 2 + 3)

        selectBtn = driver.find_element_by_xpath("//select[@node-type='changeLanguage']")
        selectBtn.click()
        time.sleep(5)

        if checkContent():

            getContent()

            if checkNext():
                print "下一页"

                next_page_btn = driver.find_element_by_xpath("//a[@class='page next S_txt1 S_line1']")
                next_page_btn.click()
            else:
                driver.execute_script('window.location.reload()')

                if checkNext():
                    continue
                else:
                    print "已达到最后一页"
                    break
        else:
            print "该页面没有数据"
            break

def checkContent():

    try:
        driver.find_element_by_xpath("//div[@class='pl_noresult']")
        flag = False
    except:
        flag = True
    return flag

def checkNext():
    time.sleep(2)
    try:
        driver.find_element_by_xpath("//a[@class='page next S_txt1 S_line1']")
        flag = True
    except:
        flag = False
    return flag

def initDatabase():

    # 初始化数据库对应操作
    global coon
    conn = pymysql.connect(host="127.0.0.1", port=3306,
    user='root', passwd='xiaomixm', db='spider', charset='utf8mb4')

    global cur
    cur = conn.cursor()

    # #建表
    # #
    # sql = 'CREATE TABLE ' + key + '(博主昵称 char(200), 内容 varchar(10000), 发布时间 char(20), 转发 int(8), 评论 int(8), 赞 int(8)) character set = utf8mb4'
    #
    # cur.execute(sql)
    # cur.connection.commit()


def writeDatabase(dic):
    global cur


    for k in range(len(dic)):

        sql = 'INSERT INTO ' + key + '(博主昵称, 内容, 发布时间, 转发, 评论, 赞) VALUES ('

        for i in range(len(dic[k])):
            if i == 0:
                sql += '\'' + dic[k][i] + '\''
            else:
                sql += ', \'' + dic[k][i] + '\''

        sql += ')'
        try:
            cur.execute(sql)
        except Exception as e:
            sql = 'INSERT INTO ' + key + '(博主昵称, 内容, 发布时间, 转发, 评论, 赞) VALUES ('
            for i in range(len(dic[k])):
                if i == 0:
                    sql += '\"' + dic[k][i] + '\"'
                else:
                    sql += ', "' + dic[k][i] + '\"'

            sql += ')'
            try:
                cur.execute(sql)
            except Exception as e:
                print sql
        cur.connection.commit()

def getContent():

    #寻找到每一条微博的class
    nodes = driver.find_elements_by_xpath("//div[@action-type='feed_list_item']")

    if len(nodes) == 0:

        url = driver.current_url
        try:
            driver.get(url)
        except Exception as e:
            driver.execute_script('window.stop()')

        getContent()
        return

    dic = {}


    for i in range(len(nodes)):
        dic[i] = []
        global numOFItem
        numOFItem = numOFItem + 1
        print '正在写入第', numOFItem, '条记录'
        try:
            BZNC = nodes[i].find_element_by_xpath(".//div[@class='WB_info']/a[@class='W_f14 W_fb S_txt1']").text
        except:
            BZNC = ''
        print u'博主昵称:', BZNC
        dic[i].append(BZNC)

        try:
            WBNR = nodes[i].find_element_by_xpath(".//div[@class='WB_detail']/div[@class='WB_text W_f14']").text
        except Exception as e:
            WBNR = ''
        print '微博内容:', WBNR
        dic[i].append(WBNR)


        try:
            FBSJ = nodes[i].find_element_by_xpath(".//div[@class='WB_from S_txt2']/a[@class = 'S_txt2']").get_attribute('title')
        except:
            FBSJ = ''
        print u'发布时间:', FBSJ
        dic[i].append(FBSJ)


        try:
            ZF_TEXT = nodes[i].find_element_by_xpath(".//ul[@class='WB_row_line WB_row_r4 clearfix S_line2']/li[2]//em[2]").text
            if ZF_TEXT == '':
                ZF = 0
            else:
                ZF = int(ZF_TEXT)
        except:
            ZF = 0
        print '转发:', ZF
        dic[i].append(str(ZF))

        try:
            PINGLUN_TEXT = nodes[i].find_element_by_xpath(".//ul[@class='WB_row_line WB_row_r4 clearfix S_line2']/li[3]//em[2]").text #可为空
            if PINGLUN_TEXT == '':
                PINGLUN = 0
            else:
                PINGLUN = int(PINGLUN_TEXT)
        except:
            PINGLUN = 0
        print '评论:', PINGLUN
        dic[i].append(str(PINGLUN))

        try:
            ZAN_TEXT = nodes[i].find_element_by_xpath(".//ul[@class='WB_row_line WB_row_r4 clearfix S_line2']/li[4]//em[2]").text #可为空
            if ZAN_TEXT == '':
                ZAN = 0
            else:
                ZAN = int(ZAN_TEXT)
        except:
            ZAN = 0
        print '赞:', ZAN
        dic[i].append(str(ZAN))


    writeDatabase(dic)

#*******************************************************************************
#                                程序入口
#*******************************************************************************
if __name__ == '__main__':

    #定义变量
    username = 'xiaomixxmm@163.com'             #输入你的用户名
    password = 'xiaomixm840'               #输入你的密码

    #操作函数
    LoginWeibo(username, password)       #登陆微博

    #搜索热点微博 爬取评论

    key = raw_input("请输入相关话题关键词: ")
    key = '吉林警事'
    GetSearchContent(key)

    global cur
    global conn
    cur.close()

    print "数据已采集完成"
