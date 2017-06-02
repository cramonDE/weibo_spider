# 新浪微博数据爬取
简单获取微博平台的相关数据,项目源码地址: [github](https://github.com/cramonDE/weibo_spider)
## 平台和使用的工具及语言
> - linux ubuntu17.04
> - python 2.7
> - selenium（包含相应的firefox扩展）

> - mysql和phpmyadmin图形化界面管理工具

## 文件内容及目录

- forward_ twice.py 通过具体的特殊实例，分析某一条微博，获取其二次转发的数量以及博主的粉丝数
- searchFans.py 另外写的一个小程序，通过数据库操作获取微博博主的主页url，增加爱博主的粉丝数目

- searchPage.py 对新的页面xpath获取所需元素的测试

- spider_mysql_nofans.py 不同时获取微博博主的粉丝数加快爬取的速度
- spider_MySQL 使用python操作数据库的测试
- weibo_spider_search.py 比价全面，可以同时获取相关话题微博的昵称，主页，微博内容，发布时间，微博认证，转发，评论，赞，粉丝数

## 原理及实现
> 数据爬取

1.	使用selenium这个工具所提供的api去模拟浏览器的操作，通过url访问拿到数据
2.	之后用xpath对目标元素进行定位，找到所需要的数据
3.	之后对数据进行一个简答的字符串处理，得到所需要的格式

> 数据库操作

1.	使用mysql对数据做一个持久话保存
2.	使用phpmyadmin对数据库表格的内容进行操作，排序，切割表之后按照需要导出excel文件

>实际例子

**查找相关话题下的所有讨论的微博**
1. 通过selenium模拟浏览器进行表单提交的操作，输入用户名和密码，点击登录，设置已登录的cookie
2. 在s.weibo.com这个网址进行表单提交，输入查找的关键词
3. 使用xpath定位每一条微博
4. 再通过xpath具体定位到每一条微博里面所需要的数据项，写进数据库
5.	运行查找粉丝的脚本，访问转发量最大的数据中的前100条微博的博主的微博，再写进数据库中
6.	在phpmyadmin进行操作，按照转发量降序排列，之后通过转发量最大的数据项，用其发布时间，将整个数据库表按照时间先后顺序进行分割，可以判断事件发生的前后的公共事件的关注度

**查找原始微博下方所有数据的整合，包含二次转发和点赞**
1.	通过selenium模拟浏览器进行表单提交的操作，输入用户名和密码，点击登录，设置已登录的cookie
2.	访问所给的原微博的url
3.	找到所有人的转发和评论记录，然后根据需要再细致的定位到某一个元素中获取相关信息，写进数据库中
4.	运行查找粉丝的脚本，访问转发量最大的数据中的前100条微博的博主的微博，再写进数据库中

## 代码部分
代码的总体框架参考了这篇博客,感谢博主的思路
 [传送门](http://blog.csdn.net/destinyuan/article/details/51297528)
在这里主要对spider_mysql.py这个文件进行分析,其他文件也是同理,针对不同页面,但原理是一样的

``` python
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

driver = webdriver.Firefox()
```
在文件的开头指定的默认字符编码,python默认是不支持中文的,加上使用mysql操作,插入数据也是要使用utf-8编码,所以现在这里指定使用utf-8编码

```python
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
```
登录的方式是简单的获取输入框并点击"登录"按钮,这里设置的延迟主要是等待服务器响应,设置cookie,记录登录信息(微博某些信息需要登录才能显示)

``` python
def handlePage():
    global numOFItem
    numOFItem = 0
    while True:

        time.sleep(random.random() * 2 + 1)
        #先行判定是否有内容
        if checkContent():

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
        else:
            print "该页面没有数据"
            break
```
对页面的获取是一个循环,按页进行加载,也跟我们平时浏览页面一样
```python
def initDatabase():

    # 初始化数据库对应操作
    global coon
    conn = pymysql.connect(host="127.0.0.1", port=3306,
    user='root', passwd='xiaomixm', db='spider', charset='utf8mb4')

    global cur
    cur = conn.cursor()

    #建表

    sql = 'CREATE TABLE ' + key + '(博主昵称 char(200), 博主主页 char(200), 微博内容 varchar(10000), 微博认证 char(20), 发布时间 char(20), 转发 int(8), 评论 int(8), 赞 int(8), 粉丝数 int(8)) character set = utf8mb4'
    cur.execute(sql)
    cur.connection.commit()
```
对数据库进行建表,并设置相关信息,注意这里的字符编码不仅仅是utf-8,而应该是utf8mb4,因为在微博正文中,有些博主会发特殊的表情或者符号,他们是三个字节的字符,如果仅仅是utf-8编码的话,插入数据库会报错
这里的问题参考:
[python对字符编码的处理](https://my.oschina.net/leejun2005/blog/343353)

```python
def writeDatabase(dic):
    global cur
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
```
这一部分是数据库的插入操作,自认为写的不够优雅,但是后面懒得改了,默认将所有数据转化成字符串输入, 有可能存在sql注入的问题,所以对问题数据打印出来,再手动插入到数据库中,而不是在这里做一个统一的处理
```python
try:
            WBRZ = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_icon icon_approve']").get_attribute('title')#若没有认证则不存在节点
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
```
后面是单独对信息的获取,这个可以通过测试文件检验xpath能否获取到所需要的元素,这里注明一下微博认证是一个坑,有三种不同类型的微博认证,因此只能一个一个得进行判断
```python
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
```
这一部分是获取微博的博主粉丝.具体原理是获取当前也所有的url存到一个数组当中,然后在整个页面读取完了之后,产生一个"中断",访问这些url,获取粉丝数并记录,之后再回到当前的地址.这一部分也是遇到的坑比较多,而程序在这部分花的时间也是比较多,后面直接去掉了这部分,在数据库操作之后再获取想要的前100个博主的粉丝数,节省爬虫运行的时间.这里坑的地方主要有三个:
-  主页页面响应的问题,有时候会莫名奇妙没有渲染出粉丝数,这种情况刷新一下页面就可以
-  微博粉丝数的节点跟微博认证是有关系的,之间的相互关系比较乱,我也没有区分,直接获取和判断
-  页面响应时间过长,有时候已经加载完所需要的数据但页面采集还没开始,selenium默认是在页面渲染完才开始进行数据采集,所以设置了页面超时,超过这个时间自动中止页面响应并获取数据.
> 这块地方使用解析数据包的方法可以很容易的获取粉丝数

## 特点
- **使用selenium进行模拟浏览器的操作**

使用python进行数据爬取一个难点是爬取页面的登录问题，需要用户登录发送cookie记录，服务端找到登录状态，才能显示全部信息， 如果按照其他python爬虫的方法，无论是用urllib的库，还是用scrapy，都必须要解决登录问题，通过相关微博了解了一下，对用户名使用base64加密，同时对于密码使用非对称加密，需要通过发送请求得到相关的6个字段，然后在对应进行加密后发送请求，然后才能进行数据爬取，实现的难度较大。因此采用模拟浏览器的方法，在浏览器中获取输入框，输入用户名和密码，这样就可以解决登录的问题
- **使用mysql进行相关数据库的操作**

爬取数据之后，需要对我们需要的字段进行分析统计排序等等的操作， 因此采用mysql和phpmyadmin对数据进行排序，同时导出相应的格式，其中在写进数据库的过程中，有一些正文数据使用了扩展的utf-8编码（3个字节），因此数据库表的编码应该是utf8mb4，才能将数据正确插入
- **程序健壮性**

代码基本上实现了所需要的功能，在数据爬取方面做了相应的阻塞延时，同时访问页面也采用随机延时的方法，去防止被检测使用爬虫程序。对其他非法字符或者编码原因导致插入数据错误的sql语句，也会输出，再手动将数据插入数据库。 不可避免的有时候因为网络原因或者服务器响应的问题，会导致页面渲染出错或者其他原因导致程序中止，发生的概率较少吗，已经爬取的数据不会丢失，也会将中止的url输出，方便从中断的地方再重新爬取数据
