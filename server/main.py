#coding:utf-8
from xml_spider import XmlSpider
import time
import json
import datetime
import ftplib
import os
import zipfile
from os.path import join, getsize
import shutil

# config
home = r"D:\test" #root fold of spider
res_dir = "/data/images" #pic_link to local
date_filter = 0 # get today's acti
key_filter = [] # keyword check

# ftp config
host = ""
user = "sw"
passwd = ""
ftp_home = ""


# other conf no need to change
today = datetime.date.today () - datetime.timedelta(days=date_filter)
tomorrow = today + datetime.timedelta(days=1)
tomorrow = str(tomorrow)
backups_dir = home + os.sep + "backups"
home = home + os.sep + tomorrow

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def write2json(news_list,file_name):
    js_home = home + os.sep + "json"
    mkdir(js_home)
    file_name = js_home + os.sep + file_name
    js = json.dumps(news_list)
    fp = open(file_name,"w+")
    fp.write(js)
    fp.close()

def zip_dir(src_dir,zip_name):
    z = zipfile.ZipFile(zip_name,'w',zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        fpath = dirpath.replace(src_dir,'') 
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    z.close()


def upload(file_name):
    hnyz = ftplib.FTP(host)
    hnyz.login(user, passwd)
    ftp_file = ftp_home + os.sep + file_name
    bufsize = 1024
    fp = open(file_name,'rb')
    hnyz.storbinary('STOR ' + ftp_file,fp,bufsize)
    fp.close()

def feedx(name,cat,tag,limit):
    domain = "https://feedx.net/rss"
    url = domain + "/" + name
    spider=XmlSpider("https://feedx.net/rss/"+name)
    spider.set_home(home)
    spider.set_category(cat)
    spider.set_tag(tag)
    spider.set_limit(limit)
    spider.set_local_res_dir(res_dir)
    spider.set_date_filter(date_filter)
    spider.set_key_filter(key_filter)
    spider.run()
    write2json(spider.news_list,name + ".json")


if os.path.exists(home) :
    shutil.rmtree(home)
    mkdir(home)
if os.path.exists(backups_dir + os.sep + tomorrow + ".zip"):
    print("明天的新闻已经上传！")
    exit()


# 360Kr
spider=XmlSpider("https://36kr.com/feed")
spider.set_home(home)
spider.set_category(["其它"])
spider.set_tag(["36氪"])
spider.set_local_res_dir(res_dir)
spider.set_date_filter(date_filter)
spider.set_key_filter(key_filter)
spider.run()
write2json(spider.news_list,"36kr.json")

# Zhihu Daily
spider=XmlSpider("http://www.zhihu.com/rss")
spider.set_home(home)
spider.set_category(["涨知识"])
spider.set_tag(["知乎日报"])
spider.set_local_res_dir(res_dir)
spider.set_date_filter(date_filter)
spider.set_key_filter(key_filter)
spider.run()
write2json(spider.news_list,"zhihu.json")

feedx("cnbetatop.xml",["其它"],["CnbetaTop"],5)
feedx("nytimesphoto.xml",["新闻"],["纽约时报图集"],5)
feedx("ft.xml",["新闻"],["FT中文网"],5)
feedx("reuters.xml",["新闻"],["路透社"],5)
feedx("bbc.xml",["新闻"],["英国BBC广播电台"],5)
feedx("wikiindex.xml",["新闻"],["维基百科首页"],1)
feedx("abc.xml",["新闻"],["澳大利亚ABC电台"],5)
feedx("aljazeera.xml",["新闻"],["半岛新闻中文"],5)
feedx("ifanr.xml",["涨知识"],["爱范儿ifanr"],10)
feedx("zhidaodaily.xml",["新闻"],["百度知道日报"],6)
#feedx("163easy.xml",["其它"],["网易轻松一刻"],3)

# upload to FTP
zip_name = tomorrow + ".zip"
print("* 正在压缩文件" + zip_name)
zip_dir(home,zip_name)
print("* 正在上传至ftp")
upload(zip_name)
print("* 备份数据包")
mkdir(backups_dir)
shutil.move(zip_name,backups_dir+"/"+zip_name)
print("* 删除临时文件")
shutil.rmtree(home)
