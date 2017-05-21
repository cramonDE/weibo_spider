#!/usr/bin/python
#coding:utf-8
#
import sys
import pymysql
import re
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

defaultencoding = 'utf-8'

if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

conn = pymysql.connect(host="127.0.0.1", port=3306,
user='root', passwd='xiaomixm', db='spider', charset='utf8mb4')
cur = conn.cursor()
name = '梓丰'
studentID = '想想这些'

driver = webdriver.Firefox()

driver.get("http://login.sina.com.cn/")
elem_user = driver.find_element_by_name("username")
elem_user.send_keys("xiaomixxmm@163.com") #用户名
elem_pwd = driver.find_element_by_name("password")
elem_pwd.send_keys("xiaomixm840")  #密码
elem_sub = driver.find_element_by_xpath("//input[@class='W_btn_a btn_34px']")
elem_sub.click()

time.sleep(2)

key = '丽江打人'
sql = "SELECT `博主主页`, `微博认证` FROM "+ key +" ORDER BY `转发` DESC LIMIT 50;"



cur.execute(sql)

cur.connection.commit()

results = cur.fetchall()

driver.set_page_load_timeout(2.5)

for i in range(len(results)) :

    url = results[i][0]
    try:
        driver.get(url)

    except Exception as e:
        driver.execute_script('window.stop()')

    if (results[i][1] == "微博机构认证(企业号)"):
        print "jigou"
        searchEMs = "//td[@class='S_line1']"
    else:
        searchEMs = "//a[@class='t_link S_txt1']"
    if (results[i][1] == "微博个人认证 (vip)"):
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
                            FAN = ''
    if FAN == '':
        searchEMs = "//td[@class='S_line1']"
        searchEM = ".//strong[@class='W_f18']"
        FANS = driver.find_elements_by_xpath(searchEMs)
        try:
            FAN = FANS[1].find_element_by_xpath(searchEM).text
        except Exception as e:
            FAN = ''
    if FAN == '':
        searchEMs = "//td[@class='S_line1']"
        searchEM = ".//strong[@class='W_f16']"
        FANS = driver.find_elements_by_xpath(searchEMs)
        try:
            FAN = FANS[1].find_element_by_xpath(searchEM).text
        except Exception as e:
            FAN = ''

    print FAN
    sql = 'UPDATE '+ key + ' SET `粉丝数` = '+ FAN + ' WHERE `博主主页` = \'' + results[i][0] + '\''

    try:
        cur.execute(sql)
        cur.connection.commit()
    except Exception as e:
        print sql

    # results[i].append(str(FAN))




cur.close()
conn.close()

# 哈尔滨天价鱼
# SELECT DISTINCT * FROM `哈尔滨天价鱼` ORDER BY `转发`*0.5 + `粉丝数`*0.35 + `评论`*0.1 + `赞`*0.05 DESC
