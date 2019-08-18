#!python3
# coding:utf-8

"""
@project:FtpNews
@file:post_news
@author:zaxtyson
@time:2019/2/4 23:38
"""

import datetime
import ftplib
import json
import os
import shutil
import time
import zipfile

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# FTP配置
ftp_host = ''
ftp_user = ''
ftp_passwd = ''
ftp_home = ''  # 数据包保存位置，必须与服务器端脚本保持一致

# 脚本配置
web_root = "D:/wordpress"  # 网站根目录

# WordPress登录配置
wp_host = "http://192.168.1.105"  # http协议头必须写上
wp_user = "robot"  # 发布新闻的账号身份设置为“作者”
wp_passwd = "root1234"

# 其它变量
today = str(datetime.date.today())  # 今天的日期 格式：2018-10-01
data_file = today + ".zip"  # 数据包名 （今天日期.zip）
home = web_root + os.sep + "data"  # 本地数据保存路径
wp_img_dir = home + os.sep + "images" + os.sep + today  # 今日新闻图片存放地址
temp_dir = home + os.sep + "temp"  # 解压临时路径
local_log_dir = home + os.sep + "log" + os.sep + "local"  # 本地日志保存路径
server_log_dir = home + os.sep + "log" + os.sep + "server"  # 服务器日志保存
local_log = local_log_dir + os.sep + "%s.log" % today  # 本地日志文件
post_sum = {}  # 文章统计数据


def log(info):
    """日志记录"""
    with open(local_log, 'a+') as mylog:
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        info = "[%s]    %s" % (log_time, info)
        print(info)
        mylog.write(info)
        mylog.write("\n")


def log_error(info, error):
    """记录错误日志"""
    log("*" * 50)
    log("[Error]	" + info)
    log(error)
    log("*" * 50)


def post_article(title, body, category, tag):
    """发布一篇文章"""
    try:
        post = WordPressPost()
        post.title = title
        post.content = body
        post.post_status = "publish"  # draft草稿
        post.post_type = "post"  # page页面
        post.comment_status = 'open'  # 允许评论
        post.date_modified = datetime.datetime.now()
        post.terms_names = {
            'category': category,
            'post_tag': tag
        }
        wp.call(NewPost(post))
        log("发布文章:%s..." % title[0:20])
    except Exception as e:
        log_error("文章发布失败！", e)


def import_news(json_file):
    """导入一个文件的全部文章"""
    js = open(json_file, "r").read()
    data = json.loads(js)
    count = 0
    for news in data:
        title = news["title"]
        body = "<h5>%s</h5>" % news["body"]
        category = news["category"]
        tag = news["tag"]
        count += 1
        post_article(title, body, category, tag)
    if len(data) != 0:
        tag = " ".join(data[0]["tag"])
        post_sum[tag] = count


def check_dir(dir):
    """路径检查，不存在则创建"""
    if not os.path.exists(dir):
        os.makedirs(dir)


def download(file_name):
    """从ftp下载数据包"""
    try:
        log("下载数据包%s ==> %s" % (file_name, home))
        hnyz = ftplib.FTP(ftp_host)
        hnyz.login(ftp_user, ftp_passwd)
        remote_file = ftp_home + "/" + file_name
        local_file = home + os.sep + file_name
        bufsize = 1024
        fp = open(local_file, 'wb')
        hnyz.retrbinary('RETR %s' % remote_file, fp.write, bufsize)
        fp.close()
    except Exception as e:
        log_error("服务器未更新数据！", e)


def unzip(zip_name, dst_dir):
    """解压数据包"""
    log("解压数据包%s ==> %s" % (zip_name, dst_dir))
    try:
        if zipfile.is_zipfile(zip_name):
            fz = zipfile.ZipFile(zip_name, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
    except Exception as e:
        log_error("解压数据包时出错!", e)


# 目录存在性检查
check_dir(home)
check_dir(local_log_dir)
check_dir(server_log_dir)
os.chdir(home)  # 进入保存数据的目录
download(data_file)  # 下载数据包
unzip(data_file, temp_dir)  # 解压到临时路径
os.remove(data_file)  # 删除数据包

# 移动网页中的资源文件
try:
    if os.path.exists(wp_img_dir):
        shutil.rmtree(wp_img_dir)
    log("移动资源文件 ==> %s" % wp_img_dir)
    news_img = temp_dir + os.sep + "images"
    server_log_file = temp_dir + os.sep + "log" + os.sep + "server" + os.sep + "%s.log" % today
    shutil.move(news_img, wp_img_dir)
    shutil.move(server_log_file, server_log_dir)
except Exception as e:
    log_error("移动资源文件时出错！", e)

# 登录wordpress
wp = Client('%s/xmlrpc.php' % wp_host, wp_user, wp_passwd)

# 导入所有json文件
news_json_dir = temp_dir + os.sep + "json"
for json_file in os.listdir(news_json_dir):
    json_file = news_json_dir + os.sep + json_file
    import_news(json_file)
shutil.rmtree(news_json_dir)
shutil.rmtree(temp_dir)

# 打印统计信息
log("*" * 50)
all_pages = 0
for tag, num in post_sum.items():
    all_pages += num
    log("* %s:%s篇" % (tag, num))
log("* 总计:%s篇" % all_pages)
log("*" * 50)
log("\n\n")
