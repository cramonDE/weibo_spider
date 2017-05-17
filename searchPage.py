# coding=utf-8
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
driver = webdriver.Firefox()

driver.get("http://login.sina.com.cn/")
elem_user = driver.find_element_by_name("username")
elem_user.send_keys("xiaomixxmm@163.com") #用户名
elem_pwd = driver.find_element_by_name("password")
elem_pwd.send_keys("xiaomixm840")  #密码
elem_sub = driver.find_element_by_xpath("//input[@class='W_btn_a btn_34px']")
elem_sub.click()
# time.sleep(2)
# try:
#     driver.get("http://weibo.com/2346569983/F2o1J1ys7?type=repost#_rnd1495036157769")
#     FANS = driver.find_elements_by_xpath("//a[@class='t_link S_txt1']")
# except TimeoutException:
#     driver.execute_script('window.stop()')
#     FANS = driver.find_elements_by_xpath("//a[@class='t_link S_txt1']")
#
# print FANS[1].find_element_by_xpath(".//strong[@class='W_f18']").text


time.sleep(2)
driver.get("http://weibo.com/2346569983/F2o1J1ys7?type=repost#_rnd1495036157769")

nodes = driver.find_elements_by_xpath("//div[@class='list_li S_line1 clearfix']")

ZF_TEXT = nodes[0].find_element_by_xpath(".//ul[@class='clearfix']/li[2]/span[@class='line S_line1']/a[@class='S_txt1']").text


print ZF_TEXT[3:]


print "done"
