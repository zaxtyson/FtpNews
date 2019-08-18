#!/usr/bin/python3
# coding:utf-8

"""
@project:FtpNews
@file:main
@author:zaxtyson
@time:2019/2/4 23:36
"""

import datetime
import ftplib
import json
import os
import shutil
import time
import zipfile
from urllib import parse

import pymysql
from database_spider import DBSpider
from xml_spider import XmlSpider

# 爬虫配置
home = '/root/ftp_news' # 爬虫工作路径，本地数据保存在这里
res_dir = "/data/images" # 内网新闻网站图片存放地址，用于替换网页中的超链接
date_filter = 0  # 日期过滤，保留第n天前的新闻
key_filter = ["DOTA", "LOL"]  # 关键字过滤，标题包含该列表任意一个关键字的新闻会被干掉

# ftp配置
ftp_host = ''
ftp_user = ''
ftp_passwd = ''
ftp_home = '/zt/ftp_news/'  # ftp上保存新闻数据包的目录

# Mysql配置
mysql_host = ''  # 外网域名
mysql_user = ''
mysql_passwd = ''
database = ''  # 外网数据库名


# 其它配置，不要改
today = datetime.date.today () - datetime.timedelta(days=date_filter)
tomorrow = today + datetime.timedelta(days=1)
tomorrow = str(tomorrow)
backups_dir = home + os.sep + "backups"
home = home + os.sep + tomorrow

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
        print("创建目录：" + dir)

def write2json(news_list,file_name):
    """新闻数据写入json文件"""
    js_home = home + os.sep + "json"
    mkdir(js_home)
    file_name = js_home + os.sep + file_name
    js = json.dumps(news_list)
    fp = open(file_name,"w+")
    fp.write(js)
    fp.close()

def zip_dir(src_dir,zip_name):
    """打包目录"""
    z = zipfile.ZipFile(zip_name,'w',zipfile.ZIP_DEFLATED)
    print("打包数据为：" + zip_name)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        fpath = dirpath.replace(src_dir,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    z.close()


def upload(file_name):
    """上传文件到ftp"""
    try:
        print("正在上传%s到%s" % (file_name, ftp_host))
        hnyz = ftplib.FTP(ftp_host, ftp_user, ftp_passwd, timeout=3)
        ftp_file = ftp_home + os.sep + file_name
        bufsize = 1024
        fp = open(file_name, 'rb')
        hnyz.storbinary('STOR ' + ftp_file, fp, bufsize)
        hnyz.close()
        return True
    except Exception as e:
        print("上传时发生错误:%s" % str(e))
        return False


def feed(save_name, url, cat, tag, **kw):
    spider=XmlSpider()
    spider.set_url(url)
    spider.set_home(home)
    spider.set_category(cat)
    spider.set_tag(tag)
    spider.set_local_res_dir(res_dir)
    spider.set_date_filter(date_filter)
    spider.set_key_filter(key_filter)
    for k, v in kw.items():
        if k == "limit": spider.set_limit(v)
        if k == "date_format": spider.set_date_format(v)
    if spider.run():
        write2json(spider.news_list, save_name + ".json")


def execute(sql):
    """执行一条sql语句"""
    try:
        db = pymysql.connect(mysql_host, mysql_user, mysql_passwd, database)
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        result = cursor.fetchall()
        return result
    except Exception as e:
        db.rollback()
        print(e)
    finally:
        db.close()

# 0.目录和数据检查
if os.path.exists(home) :
    shutil.rmtree(home)
    print(home + "已存在，正在清空...")
    mkdir(home)
if os.path.exists(backups_dir + os.sep + tomorrow + ".zip"):
    print("明天的新闻已经上传！")
    exit()


# 1.我们要同步外网的新闻，从数据库直接拿新闻
data = execute('SELECT post_title,post_content FROM wp_posts WHERE post_type="post" AND post_status="publish" AND post_date>"%s" ' % today)
news_list = []
for post in data:
    body = parse.unquote(post[1],encoding="utf-8")
    body = body.replace("&amp;","&")
    news = { "title":post[0],"body":body,"category":["外网同步"],"tag":["衡一引力圈数据同步"] }
    news_list.append(news)

spider = DBSpider()
spider.set_news_list(news_list)
spider.set_home(home)
spider.set_local_res_dir(res_dir)
if spider.run():
    write2json(spider.news_list,"sync.json")

# 2.从其它网站爬取并解析feed数据
feed("36kr", "https://36kr.com/feed", ["新闻"], ["36氪"], limit=5)
feed("zhihu", "http://www.zhihu.com/rss", ["新闻"], ["知乎日报"])
feed("guanzhi", "https://rsshub.app/guanzhi", ["其它"], ["每日一文"], date_format="%a, %d %b %Y         %H:%M:%S GMT")
feed("cctv", "https://rsshub.app/cctv/world", ["新闻"], ["CCTV央视新闻"], date_format="%a, %d %b %Y     %H:%M:%S GMT",
     limit=5)
feed("cnbetatop", "https://feedx.co/rss/cnbetatop.xml", ["其它"], ["CnbetaTop"])
feed("nytimesphoto", "https://feedx.co/rss/nytimesphoto.xml", ["新闻"], ["纽约时报图集"], limit=3)
feed("ft", "https://feedx.co/rss/ft.xml", ["新闻"], ["FT中文网"], limit=5)
feed("reuters", "https://feedx.co/rss/reuters.xml", ["新闻"], ["路透社"], limit=5)
feed("bbc", "https://feedx.co/rss/bbc.xml", ["新闻"], ["英国BBC广播电台"], limit=5)
feed("ifanr", "https://feedx.co/rss/ifanr.xml", ["其它"], ["爱范儿ifanr"], limit=5)
feed("163easy", "https://feedx.co/rss/163easy.xml", ["其它"], ["网易轻松一刻"], limit=3)
feed("bool", "https://rsshub.app/dongqiudi/daily", ["新闻"], ["懂球帝早报"], date_format="%a, %d %b %Y %H:%M:%S GMT")

# 3.上传数据包到并备份，学校服务器经常出点个问题，这里多上传几次看看
zip_name = tomorrow + ".zip"
zip_dir(home,zip_name)

try_times = 3  # 最多上传次数
for i in range(1, try_times + 1):
    print("第%s次尝试上传数据..." % i)
    if upload(zip_name):
        print("数据上传完成")
        break
    else:
        time.sleep(3 * 60)  #等个3分钟看看

mkdir(backups_dir)
shutil.move(zip_name, backups_dir + os.sep + "upload_failed_" + zip_name)
print("* 删除临时文件")
shutil.rmtree(home)
