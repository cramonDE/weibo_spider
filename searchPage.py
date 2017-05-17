# coding=utf-8
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
driver = webdriver.Firefox()
driver.set_page_load_timeout(2)
driver.get("http://login.sina.com.cn/")
elem_user = driver.find_element_by_name("username")
elem_user.send_keys("xiaomixxmm@163.com") #用户名
elem_pwd = driver.find_element_by_name("password")
elem_pwd.send_keys("xiaomixm840")  #密码
elem_sub = driver.find_element_by_xpath("//input[@class='W_btn_a btn_34px']")
elem_sub.click()
# time.sleep(2)
try:
    driver.get("http://weibo.com/u/2797466544?refer_flag=1001030103_&is_all=1")
    FANS = driver.find_elements_by_xpath("//a[@class='t_link S_txt1']")
except TimeoutException:
    driver.execute_script('window.stop()')
    FANS = driver.find_elements_by_xpath("//a[@class='t_link S_txt1']")

print FANS[1].find_element_by_xpath(".//strong[@class='W_f18']").text


time.sleep(2)
driver.get("http://weibo.com/zmiltg?refer_flag=1001030103_&is_hot=1")

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "pl_common_top")))


FANS = driver.find_elements_by_xpath("//a[@class='t_link S_txt1']")

print FANS[1].find_element_by_xpath(".//strong[@class='W_f18']").text
