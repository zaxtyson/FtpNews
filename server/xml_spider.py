#!python3
# coding:utf-8

"""
@project:FtpNews
@file:xml_spider
@author:zaxtyson
@time:2019/2/4 23:11
"""

import urllib.request
import urllib.error
import chardet
import time, datetime
from bs4 import BeautifulSoup
import urllib
import re
import sys
import os
import random
import codecs


class XmlSpider():

    def __init__(self):
        self.url = ""
        self.news_list = []
        self.home = ""
        self.log_file = ""
        self.local_res_dir = ""
        self.date_format = "%a, %d %b %Y %H:%M:%S +0800"
        self.category = []
        self.tag = []
        self.key_filter_list = None
        self.date_filter = 0
        self.limit = -1
        self.today = str(datetime.date.today())
        self.tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))

    def _log(self, info):
        """内部调用，日志记录"""
        with codecs.open(self.log_file, 'a+', encoding="GBK") as mylog:
            log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            info = "[%s]    %s" % (log_time, info)
            print(info)
            mylog.write(info)
            mylog.write("\n")

    def set_url(self,url):
        """设置网站url"""
        self.url = url

    def set_home(self, dir):
        """设置爬虫家目录，下载的数据保存于此"""
        self.home = dir
        logdir = "%s/log/server" % self.home
        self.log_file = "%s/%s.log" % (logdir, self.tomorrow)

        if not os.path.exists(dir):
            os.makedirs(dir)
        if not os.path.exists(logdir):
            os.makedirs(logdir)

        self._log("爬虫工作目录:%s" % dir)

    def set_category(self, cat_list):
        """设置文章分类信息"""
        self.category = cat_list
        self._log("文章分类:%s" % cat_list)

    def set_tag(self, tag_list):
        """设置文章标签信息"""
        self.tag = tag_list
        self._log("文章标签:%s" % tag_list)

    def set_local_res_dir(self, dir):
        """设置网页本地化的资源路径，网页中的超链接将指向改路径"""
        self.local_res_dir = dir + "/" + self.tomorrow
        self._log("替换网页图片路径为:%s" % self.local_res_dir)

    def set_date_format(self, str):
        """接收一个字符串，即xml源码中putDate原始格式，用于日期处理 形如"%Y-%m-%d %H:%M:%S +0800" """
        self.date_format = str

    def set_limit(self, num):
        """设置输出的文章限制"""
        self.limit = num
        self._log("设置文章数限制:%s" % self.limit)

    def set_key_filter(self, key_list):
        """标题敏感词过滤器，接收一个列表"""
        self.key_filter_list = key_list
        self._log("关键字过滤:%s" % key_list)

    def set_date_filter(self, range):
        """设置日期过滤器，range为距今天的天数:0为今天，1为昨天"""
        today = datetime.date.today()
        target_date = today - datetime.timedelta(days=range)
        self._log("日期过滤器:%s" % target_date)
        self.date_filter = str(target_date)

    def _get_html(self, url):
        """内部调用，返回html网页源码"""
        self._log("正在获取网页源码...")
        # 伪装成浏览器
        header = ("User-Agent",
                  "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4549.400 QQBrowser/9.7.12900.400")
        opener = urllib.request.build_opener()
        opener.addheaders = [header]
        # 网页编码处理
        try:
            xml = opener.open(url).read()
            #code = chardet.detect(xml)["u"]
            xml = xml.decode("utf-8")
        except:
            return None
        else:
            return xml

    def _analyze(self):
        """内部调用，解析xml源码，返回结果列表"""
        self._log("正在解析:%s" % self.url)
        xml = self._get_html(self.url)

        # 异常则退出
        if not xml:
            self._log("解析异常:%s" % self.url)
            return False

        # 开始解析
        soup = BeautifulSoup(xml, "xml")
        item_list = soup.find_all("item")
        for item in item_list:
            news = {}  # 一条新闻
            if not item.pubDate:  # 日期不明的新闻跳过
                continue
            news["title"] = item.title.get_text().strip()
            news["body"] = item.description.get_text()
            putdate = item.pubDate.get_text().strip()  # xml里面提取的不标准化的putDate字符串
            date1 = time.mktime(time.strptime(putdate, self.date_format))  # 化为标准日期格式
            date2 = time.strftime("%Y-%m-%d", time.localtime(date1))  # 统一使用年-月-日表示
            news["date"] = str(date2)
            news["category"] = self.category
            news["tag"] = self.tag
            self.news_list.append(news)

    def _download(self, url, save_path, file_name):
        """内部调用，下载文件"""
        try:
            # 不完整的链接尝试加上域名
            if url.startswith("/"):
                domain = self.url.split("/")[:3]
                domain = "/".join(domain)
                url = domain + url[1:]
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            self._log("正在下载:%s" % url)
            full_name = save_path + os.sep + file_name
            urllib.request.urlretrieve(url, full_name)
        except Exception as e:
            self._log("下载失败,链接已失效！")
            print(e)

    def _key_filter(self):
        """内部调用，标题关键词过滤"""
        if len(self.key_filter_list) == 0:
            self._log("未启用关键字过滤器")
            return
        for news in self.news_list:
            for key in self.key_filter_list:
                if key in news["title"]:
                    index = self.news_list.index(news)
                    self.news_list.pop(index)
                    self._log("因关键字过滤:%s" % news["title"])

    def _date_filter(self):
        """内部调用，日期过滤，默认保留今天的文章"""
        save_list = []  # 不能在循环中使用list的remove()方法，这样会让一些元素逃过删除，这里弄一个新的列表保存匹配的文章
        for news in self.news_list:
            if news["date"] == self.date_filter:
                self._log("保留该文章:(%s)%s" % (news["date"], news["title"]))
                save_list.append(news)
            else:
                self._log("因日期过滤:(%s)%s" % (news["date"], news["title"]))
        self.news_list = save_list

    def _limit_pages(self):
        """限制每个网站爬取的文章数"""
        if self.limit != -1:
            self.news_list = self.news_list[0:self.limit]

    def _down_jpg(self):
        """下载jpg文件，随机命名防止同名图片被覆盖，将网页代码中的链接本地化"""
        for i in range(0, len(self.news_list)):
            soup = BeautifulSoup(self.news_list[i]["body"], "lxml")
            imgs = []
            for link in soup.find_all("img"):
                link = link.get("src")
                if link not in imgs:
                    imgs.append(link) #防止重复
            for link in imgs:
                random_name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10)) + ".gif"
                save_path = self.home + os.sep + "images"
                self._download(link, save_path, random_name)
                local_link = self.local_res_dir + "/" + random_name
                self.news_list[i]["body"] = self.news_list[i]["body"].replace(link,local_link)

    def run(self):
        """运行爬虫"""
        try:
            self._analyze()
            self._key_filter()
            self._date_filter()
            self._limit_pages()
            self._down_jpg()
            num = len(self.news_list)
            self._log("总计爬取%s篇文章" % num)
            self._log("%s" % "=" * 120)
        except Exception as e:
            print("发生错误:", e)