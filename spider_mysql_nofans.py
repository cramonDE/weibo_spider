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

    except Exception,e:
        print "Error: ",e
    finally:
        print u'End LoginWeibo!\n'


def GetSearchContent(key):
    driver.get("http://s.weibo.com/")


    # driver.get("http://s.weibo.com/weibo/%25E5%2593%2588%25E5%25B0%2594%25E6%25BB%25A8%25E5%25A4%25A9%25E4%25BB%25B7%25E9%25B1%25BC&nodup=1&page=49")
    # driver.get("")


    driver.set_page_load_timeout(3)






    item_inp = driver.find_element_by_xpath("//input[@class='searchInp_form']")
    item_inp.send_keys(key.decode('utf-8'))

    searchBtn = driver.find_element_by_xpath("//a[@class='searchBtn']")
    searchBtn.click()    #采用点击回车直接搜索


    showFullBtn = driver.find_element_by_xpath("//div[@class='search_rese clearfix']/a[@suda-data='key=tblog_search_weibo&value=weibo_filter_nodup']")
    showFullBtn.click()

    initDatabase()
    time.sleep(2)


#

    #
    url = driver.current_url.split('&')[0] + '&scope=ori&suball=1&Refer=g'

    print driver.current_url
    print driver.current_url.split('&')[0]
    try:
        driver.get(url)
    except Exception as e:
        driver.execute_script('window.stop()')


    handlePage()  #处理当前页面内容


def handlePage():
    global numOFItem
    numOFItem = 0
    while True:


        if (numOFItem > 500):
            time.sleep(random.random() * 2 + 5)
        else:
            time.sleep(random.random() * 2 + 3)
        #先行判定是否有内容
        print driver.current_url
        if checkContent():

            getContent()
            #先行判定是否有下一页按钮
            if checkNext():
                print "下一页"
                #拿到下一页按钮
                next_page_btn = driver.find_element_by_xpath("//a[@class='page next S_txt1 S_line1']")
                next_page_btn.click()
            else:
                driver.execute_script('window.location.reload()')
                time.sleep(2)
                if checkNext():
                    continue
                else:
                    print "已达到最后一页"
                    break

        else:
            print "该页面没有数据"
            break

#判断页面加载完成后是否有内容
def checkContent():

    try:
        driver.find_element_by_xpath("//div[@class='pl_noresult']")
        flag = False
    except:
        flag = True
    return flag

#判断是否有下一页按钮
def checkNext():
    time.sleep(2)
    try:
        driver.find_element_by_xpath("//a[@class='page next S_txt1 S_line1']")
        flag = True
    except:
        flag = False
    return flag

#在添加每一个sheet之后，初始化字段
def initDatabase():

    # 初始化数据库对应操作
    global coon
    conn = pymysql.connect(host="127.0.0.1", port=3306,
    user='root', passwd='xiaomixm', db='spider', charset='utf8mb4')

    global cur
    cur = conn.cursor()

    #建表
    #
    # sql = 'CREATE TABLE ' + key + '(博主昵称 char(200), 博主主页 char(200), 微博内容 varchar(10000), 微博认证 char(20), 发布时间 char(20), 转发 int(8), 评论 int(8), 赞 int(8), 粉丝数 int(8) DEFAULT 0) character set = utf8mb4'
    #
    # cur.execute(sql)
    # cur.connection.commit()


def writeDatabase(dic):
    global cur


    for k in range(len(dic)):

        sql = 'INSERT INTO ' + key + '(博主昵称, 博主主页, 微博内容, 微博认证 , 发布时间, 转发, 评论, 赞) VALUES ('

        for i in range(len(dic[k])):
            if i == 0:
                sql += '\'' + dic[k][i] + '\''
            else:
                sql += ', \'' + dic[k][i] + '\''

        sql += ')'
        try:
            cur.execute(sql)
        except Exception as e:
            sql = 'INSERT INTO ' + key + '(博主昵称, 博主主页, 微博内容, 微博认证 , 发布时间, 转发, 评论, 赞) VALUES ('
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
#在页面有内容的前提下，获取内容
def getContent():
    time.sleep(2)
    #寻找到每一条微博的class
    nodes = driver.find_elements_by_xpath("//div[@class='WB_cardwrap S_bg2 clearfix']")

    if len(nodes) == 0:
        # raw_input("请在微博页面输入验证码！")
        url = driver.current_url
        driver.get(url)
        getContent()
        return
    dic = {}
    fansPage = []


    for i in range(len(nodes)):
        dic[i] = []
        global numOFItem
        numOFItem = numOFItem + 1
        print '正在写入第', numOFItem, '条记录'
        try:
            BZNC = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_texta W_fb']").text
        except:
            BZNC = ''
        # print u'博主昵称:', BZNC
        dic[i].append(BZNC)

        try:
            BZZY = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_texta W_fb']").get_attribute("href")
        except:
            BZZY = ''
        # print u'博主主页:', BZZY
        dic[i].append(BZZY)
        fansPage.append(BZZY)

        try:
            fullTextBtn = nodes[i].find_element_by_xpath(".//a[@class='WB_text_opt']")
            fullTextBtn.click()
            time.sleep(1)
            WBNRarr = nodes[i].find_elements_by_xpath(".//div[@class='feed_content wbcon']/p")
            WBNR = WBNRarr[1].text
        except:
            try:
                WBNR = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/p[@class='comment_txt']").text
            except Exception as e:
                WBNR = ''
        # print '微博内容:', WBNR
        dic[i].append(WBNR)

        try:
            WBRZ = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_icon icon_approve']").get_attribute('title')#若没有认证则不存在节点

        except:
            WBRZ = ''

        if WBRZ == '':
            try:
                WBRZ = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_icon icon_approve_co']").get_attribute('title')#若没有认证则不存在节点
                # print WBRZ
            except:
                WBRZ = ''


        if WBRZ == '':
            try:
                WBRZ = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_icon icon_approve_gold']").get_attribute('title')#若没有认证则不存在节点
                WBRZ += '(gold)'

            except:
                WBRZ = ''


        # print '微博认证:', WBRZ
        dic[i].append(WBRZ)

        try:
            FBSJ = nodes[i].find_element_by_xpath(".//div[@class='feed_from W_textb']/a[@class='W_textb']").get_attribute('title')

        except:
            FBSJ = ''

        if FBSJ == '' :
            try:
                FBSJ = nodes[i].find_element_by_xpath(".//div[@class='feed_from W_textb']/a[@suda-data='key=tblog_search_weibo&value=weibo_ss_1_time']").get_attribute('title')
            except:
                FBSJ = ''

        if FBSJ == '' :
            try:
                FBSJ = nodes[i].find_element_by_xpath(".//div[@class='content clearfix']/div[@class='feed_from W_textb']/a[@class='W_textb']").get_attribute('title')
            except:
                FBSJ = ''
        if FBSJ == '' :
            try:
                FBSJ = nodes[i].find_element_by_xpath(".//em/div[@class='feed_from W_textb']/a[@class='W_textb']").get_attribute('title')
            except:
                FBSJ = ''
        # print u'发布时间:', FBSJ

        dic[i].append(FBSJ)


        try:
            ZF_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='feed_list_forward']//em").text
            if ZF_TEXT == '':
                ZF = 0
            else:
                ZF = int(ZF_TEXT)
        except:
            ZF = 0
        # print '转发:', ZF
        dic[i].append(str(ZF))

        try:
            PL_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='feed_list_comment']//em").text#可能没有em元素
            if PL_TEXT == '':
                PL = 0
            else:
                PL = int(PL_TEXT)
        except:
            PL = 0
        # print '评论:', PL
        dic[i].append(str(PL))

        try:
            ZAN_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='feed_list_like']//em").text #可为空
            if ZAN_TEXT == '':
                ZAN = 0
            else:
                ZAN = int(ZAN_TEXT)
        except:
            ZAN = 0
        # print '赞:', ZAN
        dic[i].append(str(ZAN))



    writeDatabase(dic)

if __name__ == '__main__':

    #定义变量
    username = 'xiaomixxmm@163.com'             #输入你的用户名
    password = 'xiaomixm840'               #输入你的密码

    #操作函数
    LoginWeibo(username, password)       #登陆微博


    key = '哈尔滨天价鱼'
    GetSearchContent(key)

    global cur
    global conn
    cur.close()
    # conn.close()
    print "数据已采集完成"
