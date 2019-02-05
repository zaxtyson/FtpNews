#!python3
# coding:utf-8

"""
@project:FtpNews
@file:main
@author:zaxtyson
@time:2019/2/4 23:36
"""

from xml_spider import XmlSpider
from database_spider import DBSpider
import json
import datetime
import ftplib
import os
import zipfile
import shutil
import pymysql
from urllib import parse

# 爬虫配置
home = '' # 爬虫工作路径，本地数据保存在这里
res_dir = "/data/images" # 内网新闻网站图片存放地址，用于替换网页中的超链接
date_filter = 0 # 日期过滤，保留第n天前的新闻
key_filter = [] # 关键字过滤，标题包含该列表任意一个关键字的新闻会被干掉

# ftp配置
ftp_host = ''
ftp_user = ''
ftp_passwd = ''
ftp_home = '' #ftp上保存新闻数据包的目录

# Mysql配置
mysql_host = 'www.hnyz.fun' # 外网域名
mysql_user = ''
mysql_passwd = ''
database = 'hnyz' # 外网数据库名


# 其它配置，不要改
today = datetime.date.today () - datetime.timedelta(days=date_filter)
tomorrow = today + datetime.timedelta(days=1)
tomorrow = str(tomorrow)
backups_dir = home + os.sep + "backups"
home = home + os.sep + tomorrow

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

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
    for dirpath, dirnames, filenames in os.walk(src_dir):
        fpath = dirpath.replace(src_dir,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    z.close()


def upload(file_name):
    """上传文件到ftp"""
    hnyz = ftplib.FTP(ftp_host)
    hnyz.login(ftp_user, ftp_passwd)
    ftp_file = ftp_home + os.sep + file_name
    bufsize = 1024
    fp = open(file_name,'rb')
    hnyz.storbinary('STOR ' + ftp_file,fp,bufsize)
    fp.close()

def feedx(name,cat,tag,limit):
    """一个不错的feed网站，盯着他爬啦"""
    domain = "https://feedx.net/rss"
    url = domain + "/" + name
    spider=XmlSpider()
    spider.set_url("https://feedx.net/rss/"+name)
    spider.set_home(home)
    spider.set_category(cat)
    spider.set_tag(tag)
    spider.set_limit(limit)
    spider.set_local_res_dir(res_dir)
    spider.set_date_filter(date_filter)
    spider.set_key_filter(key_filter)
    spider.run()
    write2json(spider.news_list,name + ".json")

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
    news = { "title":post[0],"body":body }
    news_list.append(news)

spider = DBSpider()
spider.set_news_list(news_list)
spider.set_home(home)
spider.set_category(["外网同步"])
spider.set_tag(["衡一引力圈数据同步"])
spider.set_local_res_dir(res_dir)
spider.run()
write2json(spider.news_list,"sync.json")

# 2.从其它网站爬取并解析feed数据
# 360Kr
# spider=XmlSpider()
# spider.set_url("https://36kr.com/feed")
# spider.set_home(home)
# spider.set_category(["其它"])
# spider.set_tag(["36氪"])
# spider.set_local_res_dir(res_dir)
# spider.set_date_filter(date_filter)
# spider.set_key_filter(key_filter)
# spider.run()
# write2json(spider.news_list,"36kr.json")
#
# # 知乎日报
# spider=XmlSpider()
# spider.set_url("http://www.zhihu.com/rss")
# spider.set_home(home)
# spider.set_category(["涨知识"])
# spider.set_tag(["知乎日报"])
# spider.set_local_res_dir(res_dir)
# spider.set_date_filter(date_filter)
# spider.set_key_filter(key_filter)
# spider.run()
# write2json(spider.news_list,"zhihu.json")

# feedx
# feedx("cnbetatop.xml",["其它"],["CnbetaTop"],5)
# feedx("nytimesphoto.xml",["新闻"],["纽约时报图集"],5)
# feedx("ft.xml",["新闻"],["FT中文网"],5)
# feedx("reuters.xml",["新闻"],["路透社"],5)
# feedx("bbc.xml",["新闻"],["英国BBC广播电台"],5)
feedx("wikiindex.xml",["新闻"],["维基百科首页"],1)
# feedx("abc.xml",["新闻"],["澳大利亚ABC电台"],5)
# feedx("aljazeera.xml",["新闻"],["半岛新闻中文"],5)
# feedx("ifanr.xml",["涨知识"],["爱范儿ifanr"],10)
# feedx("zhidaodaily.xml",["新闻"],["百度知道日报"],6)
#feedx("163easy.xml",["其它"],["网易轻松一刻"],3) #这鬼玩意数据量太大

# 3.上传数据包到并备份
zip_name = tomorrow + ".zip"
print("* 正在压缩文件" + zip_name)
zip_dir(home,zip_name)
print("* 正在上传至ftp")
upload(zip_name)
print("* 备份数据包")
mkdir(backups_dir)
shutil.move(zip_name,backups_dir+os.sep+zip_name)
print("* 删除临时文件")
shutil.rmtree(home)
