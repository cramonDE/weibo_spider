# coding=utf-8

"""
Created on 2016-04-28
@author: xuzhiyuan

功能: 爬取新浪微博的搜索结果,支持高级搜索中对搜索时间的限定
网址：http://s.weibo.com/
实现：采取selenium测试工具，模拟微博登录，结合PhantomJS/Firefox，分析DOM节点后，采用Xpath对节点信息进行获取，实现重要信息的抓取

写入数据库的版本

"""

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
import xlwt
import pymysql
import random
from selenium.common.exceptions import TimeoutException


defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

#先调用无界面浏览器PhantomJS或Firefox
#driver = webdriver.PhantomJS()
driver = webdriver.Firefox()

#********************************************************************************
#                            第一步: 登陆login.sina.com
#                     这是一种很好的登陆方式，有可能有输入验证码
#                          登陆之后即可以登陆方式打开网页
#********************************************************************************

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

        #获取Coockie 推荐资料：http://www.cnblogs.com/fnng/p/3269450.html
        print 'Crawl in ', driver.current_url
        print u'输出Cookie键值对信息:'
        for cookie in driver.get_cookies():
            print cookie
            for key in cookie:
                print key, cookie[key]
        print u'登陆成功...'
    except Exception,e:
        print "Error: ",e
    finally:
        print u'End LoginWeibo!\n'

#********************************************************************************
#                  第二步: 访问http://s.weibo.com/页面搜索结果
#               输入关键词、时间范围，得到所有微博信息、博主信息等
#                     考虑没有搜索结果、翻页效果的情况
#********************************************************************************

def GetSearchContent(key):
    # driver.get("http://s.weibo.com/")

    driver.get("http://weibo.com/p/10080894e9598635edea876a4340b06da7f3c4?pids=Pl_Third_App__11&feed_sort=timeline&feed_filter=timeline#Pl_Third_App__11")
    #
    #
    #
    driver.set_page_load_timeout(2.5)




    # 输入关键词并点击搜索

    # item_inp = driver.find_element_by_xpath("//input[@class='searchInp_form']")
    # item_inp.send_keys(key.decode('utf-8'))
    #
    # searchBtn = driver.find_element_by_xpath("//a[@class='searchBtn']")
    # searchBtn.click()    #采用点击回车直接搜索


    # #每一天使用一个sheet存储数据
    # initDatabase()
    time.sleep(2)
    # #通过构建URL实现每一天的查询


    #
    # url = driver.current_url.split('&')[0] + '&scope=ori&suball=1&Refer=g'
    #
    # print driver.current_url
    # print driver.current_url.split('&')[0]
    # try:
    #     driver.get(url)
    # except Exception as e:
    #     driver.execute_script('window.stop()')



    #
    # http://s.weibo.com/weibo/%25E5%2593%2588%25E5%25B0%2594%25E6%25BB%25A8%25E5%25A4%25A9%25E4%25BB%25B7%25E9%25B1%25BC&Refer=STopic_box
    #
    # http://s.weibo.com/weibo/%25E5%2593%2588%25E5%25B0%2594%25E6%25BB%25A8%25E5%25A4%25A9%25E4%25BB%25B7%25E9%25B1%25BC&scope=ori&suball=1&Refer=g

    handlePage()  #处理当前页面内容

        # start_stamp = end_stamp
        # end_stamp = end_stamp + delta_date

#********************************************************************************
#                  辅助函数，考虑页面加载完成后得到页面所需要的内容
#********************************************************************************

#页面加载完成后，对页面内容进行处理
def handlePage():
    global numOFItem
    numOFItem = 0
    while True:
        #之前认为可能需要sleep等待页面加载，后来发现程序执行会等待页面加载完毕
        #sleep的原因是对付微博的反爬虫机制，抓取太快可能会判定为机器人，需要输入验证码
        time.sleep(random.random() * 2 + 1)
        #先行判定是否有内容

        getContent()
        #先行判定是否有下一页按钮
        if checkNext():
            print "下一页"
            #拿到下一页按钮
            next_page_btn = driver.find_element_by_xpath("//a[@class='page next S_txt1 S_line1']")
            next_page_btn.click()
        else:
            print "已达到最后一页"
            break


#判断页面加载完成后是否有内容
def checkContent():
    #有内容的前提是有“导航条”？错！只有一页内容的也没有导航条
    #但没有内容的前提是有“pl_noresult”
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

    # sql = 'CREATE TABLE ' + key + '(博主昵称 char(200), 博主主页 char(200), 微博内容 varchar(10000), 微博认证 char(20), 发布时间 char(20), 转发 int(8), 评论 int(8), 赞 int(8), 粉丝数 int(8)) character set = utf8mb4'
    # cur.execute(sql)
    # cur.connection.commit()


#将dic中的内容写入excel
def writeDatabase(dic):
    global cur

    # for k in dic:
    #     for i in range(len(dic[k])):
    #         sheet.write(row, i, dic[k][i])
    #     row = row + 1
    # outfile.save("./crawl_output_YS.xls")

    for k in range(len(dic)):

        sql = 'INSERT INTO ' + key + '(博主昵称, 博主主页, 微博内容, 微博认证 , 发布时间, 转发, 评论, 赞, 粉丝数) VALUES ('

        for i in range(len(dic[k])):
            if i == 0:
                sql += '\'' + dic[k][i] + '\''
            else:
                sql += ', \'' + dic[k][i] + '\''

        sql += ')'
        try:
            cur.execute(sql)
        except Exception as e:
            sql = 'INSERT INTO ' + key + '(博主昵称, 博主主页, 微博内容, 微博认证 , 发布时间, 转发, 评论, 赞, 粉丝数) VALUES ('
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

    #寻找到每一条微博的class
    nodes = driver.find_elements_by_xpath("//div[@class='WB_cardwrap WB_feed_type S_bg2']")

    #在运行过程中微博数==0的情况，可能是微博反爬机制，需要输入验证码
    if len(nodes) == 0:
        # raw_input("请在微博页面输入验证码！")
        url = driver.current_url
        try:
            driver.get(url)
        except Exception as e:
            driver.execute_script('window.stop()')

        getContent()
        return

    dic = {}
    fansPage = []
    # global page
    # print str(start_stamp.strftime("%Y-%m-%d-%H"))
    # print u'页数:', page
    # page = page + 1
    # print u'微博数量', len(nodes)

    for i in range(len(nodes)):
        dic[i] = []
        global numOFItem
        numOFItem = numOFItem + 1
        print '正在写入第', numOFItem, '条记录'
        try:
            BZNC = nodes[i].find_element_by_xpath(".//div[@class='WB_info']/a[@class='W_f14 W_fb S_txt1']").text
        except:
            BZNC = ''
        # print u'博主昵称:', BZNC
        dic[i].append(BZNC)

        try:
            BZZY = nodes[i].find_element_by_xpath(".//div[@class='WB_info']/a[@class='W_f14 W_fb S_txt1']").get_attribute("href")
        except:
            BZZY = ''
        # print u'博主主页:', BZZY
        dic[i].append(BZZY)
        fansPage.append(BZZY)



        try:
            WBNR = nodes[i].find_element_by_xpath(".//div[@class='WB_detail']/div[@class='WB_text W_f14']").text
        except Exception as e:
            WBNR = ''
        # print '微博内容:', WBNR
        dic[i].append(WBNR)

        try:
            WBRZ = nodes[i].find_element_by_xpath(".//div[@class='WB_info']//i[@class='W_icon icon_approve']").get_attribute('title')#若没有认证则不存在节点
            print WBRZ
        except:
            WBRZ = ''

        if WBRZ == '':
            try:
                WBRZ = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_icon icon_approve_co']").get_attribute('title')#若没有认证则不存在节点
                print WBRZ
            except:
                WBRZ = ''


        if WBRZ == '':
            try:
                WBRZ = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_icon icon_approve_gold']").get_attribute('title')#若没有认证则不存在节点
                WBRZ += '(gold)'
                print WBRZ
            except:
                WBRZ = ''


        # print '微博认证:', WBRZ
        dic[i].append(WBRZ)

        try:
            FBSJ = nodes[i].find_element_by_xpath(".//div[@class='WB_from S_txt2']//a[@class='S_txt2']").get_attribute('title')
        except:
            FBSJ = ''
        # print u'发布时间:', FBSJ
        dic[i].append(FBSJ)


        try:
            ZF_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='fl_forward']//em").text
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

        # print '\n'

    #写入Excel
    current_url = driver.current_url
    for i in range(len(fansPage)) :
        url = fansPage[i]
        try:
            driver.get(url)

        except Exception as e:
            driver.execute_script('window.stop()')

        if (dic[i][3] == "微博机构认证"):
            print "jigou"
            searchEMs = "//td[@class='S_line1']"
        else:
            searchEMs = "//a[@class='t_link S_txt1']"
        if (dic[i][3] == "微博个人认证(gold)"):
            print "gold"
            searchEM = ".//strong[@class='W_f14']"
        else:
            searchEM = ".//strong[@class='W_f18']"
        FANS = driver.find_elements_by_xpath(searchEMs)

        try:
            FAN = FANS[1].find_element_by_xpath(searchEM).text
        except Exception as e:

            driver.execute_script('window.location.reload()')


            FANS = driver.find_elements_by_xpath(searchEMs)
            try:
                FAN = FANS[1].find_element_by_xpath(searchEM).text
            except Exception as e:
                time.sleep(3)
                FANS = driver.find_elements_by_xpath(searchEMs)
                try:
                    FAN = FANS[1].find_element_by_xpath(searchEM).text
                except Exception as e:
                    searchEM = ".//strong[@class='W_f16']"
                    try:
                        FAN = FANS[1].find_element_by_xpath(searchEM).text
                    except Exception as e:
                        searchEM = ".//strong[@class='W_f14']"
                        try:
                            FAN = FANS[1].find_element_by_xpath(searchEM).text
                        except Exception as e:
                            searchEM = ".//strong[@class='W_f12']"
                            try:
                                FAN = FANS[1].find_element_by_xpath(searchEM).text
                            except Exception as e:
                                FAN = 0
        print FAN
        dic[i].append(str(FAN))
    try:
        driver.get(current_url)
    except Exception as e:
        driver.execute_script('window.stop()')

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

    # key = raw_input("请输入相关话题关键词: ")
    key = '哈尔滨天价鱼话题'
    GetSearchContent(key)

    global cur
    global conn
    cur.close()
    # conn.close()
    print "数据已采集完成"
