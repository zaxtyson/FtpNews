#!python3
# coding:utf-8

"""
@project:FtpNews
@file:database_spider
@author:zaxtyson
@time:2019/2/4 22:51
"""

from xml_spider import XmlSpider

class DBSpider(XmlSpider):
    """数据库爬虫"""
    def __init__(self):
        super(DBSpider,self).__init__()

    def set_news_list(self,news_list):
        """从数据库抓好的新闻列表"""
        self.news_list = news_list

    def run(self):
        """只需下载图片即可"""
        try:
            for news in self.news_list:
                self._log("保留该文章:%s" % news["title"])
            self._down_jpg()
            num = len(self.news_list)
            self._log("总计爬取%s篇文章" % num)
            self._log("%s" % "=" * 120)
        except Exception as e:
            print("发生错误:", e)