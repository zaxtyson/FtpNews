#coding:utf-8
from xml_spider import XmlSpider
import time
import json
import datetime
import os
import zipfile
from os.path import join, getsize
import shutil

# config
home="/root/ftp_news" #root fold of spider
res_dir="/res/images" #pic_link to local
date_filter=1 # get today's acti
key_filter=[] # keyword check


# other conf no need to change
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
tomorrow = str(tomorrow)
backups_dir = home + "/backups"
home = home + "/" + tomorrow

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def write2json(news_list,file_name):
    js_home = home + "/json"
    mkdir(js_home)
    file_name = js_home + "/" + file_name
    js = json.dumps(news_list)
    fp = open(file_name,"w+")
    fp.write(js)
    fp.close()




# AusBrocComp
spider=XmlSpider("https://feedx.net/rss/ap.xml")
spider.set_home(home)
spider.set_category(["新闻"])
spider.set_tag(["测试"])
spider.set_local_res_dir(res_dir)
spider.set_date_filter(date_filter)
spider.set_key_filter(key_filter)
spider.run()
print(spider.news_list[0:300])
write2json(spider.news_list,"ft.json")
