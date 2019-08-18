# -*- coding: utf-8 -*-
import configparser
import ftplib
import hashlib
import logging
import os
import pickle
import re
import shutil
import time
import zipfile
from copy import deepcopy

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline

config = configparser.ConfigParser()
config.read('my_conf.ini', encoding='utf-8')
logger = logging.getLogger()


class ProcessNewsPipeline(object):
    """新闻过滤、分类"""

    def process_item(self, item, spider):
        self.fix_link(item)
        self.set_category(item)

        if config.getboolean('filter', 'time_filter'):
            self.time_filter(item)  # 日期过滤

        if config.getboolean('filter', 'keyword_filter'):
            self.keyword_filter(item)  # 关键字过滤

        if config.getboolean('filter', 'length_filter'):
            self.keyword_filter(item)

        return deepcopy(item)  # 多线程的天坑，在这里浪费了两天时间

    def fix_link(self, item):
        """链接补全，去重"""
        item['image_urls'] = set(
            [url for url in item['image_urls'] if url.startswith('http')] +
            ['https:' + url for url in item['image_urls'] if url.startswith('//')]
        )

    def set_category(self, item):
        """设置新闻分类"""
        rule = {
            '路透中文': ['新闻', '时政'],
            '纽约时报': ['新闻', '时政'],
            'BBC': ['新闻', '时政'],
            '澎湃新闻': ['新闻', '时政'],
            'Investing.com': ['新闻', '时政'],
            '法广': ['新闻', '时政'],
            '联合早报': ['新闻', '时政'],
            '中央社': ['新闻', '时政'],
            '观止': ['新闻', '涨知识'],
            '知乎每日精选': ['新闻', '涨知识'],
            '纽约时报热门图集': ['新闻', '涨知识'],
            '每日环球视野': ['新闻', '涨知识'],
            'ChinaDaily双语': ['新闻', '涨知识'],
            'cnbeta排行': ['新闻', '科技'],
            '虎嗅': ['新闻', '科技'],
            '爱范儿': ['新闻', '科技'],
            '环球科学': ['新闻', '科技'],
            '36氪': ['新闻', '科技'],
            '网易轻松一刻': ['新闻', '其它'],
            '历史上的今天': ['新闻', '其它'],
            '豆瓣电影本周口碑榜': ['新闻', '其它'],
            '衡一引力圈': ['外网同步'] + item['category'],
        }

        tag = item['tag'][0]
        if tag in rule.keys():
            item['category'] = rule[tag]
        else:
            item['category'] = ['新闻', '其它']

    def keyword_filter(self, item):
        """标题关键字过滤"""
        ban_list = list(config.get('filter', 'ban_keywords_list'))
        for word in ban_list:
            if word in item['title']:
                raise DropItem('Filtered for containing keyword {}'.format(word))

    def time_filter(self, item):
        """新闻日期过滤"""
        time_stamp = config.getfloat('filter', 'last_crawl_time')
        if float(item['time_stamp']) <= time_stamp:
            raise DropItem('Filtered for time stamp {}'.format(time_stamp))

    def length_filter(self, item):
        """新闻正文长度过滤"""
        if len(item['content']) < config.getint('filter', 'min_content_length'):
            raise DropItem('Filtered by length')

    def close_spider(self, spider):
        config.set('filter', 'last_crawl_time', str(time.time()))
        config.write(open('my_conf.ini', 'w'))


class BasePipeline(FilesPipeline):
    url_field = None
    raw_pattern = None
    now_pattern = None

    @classmethod
    def from_settings(cls, settings):
        """修改默认文件下载位置、路径检查"""
        config.set('path', 'news_store', str(time.strftime("%Y-%m-%d_%H-%M-%S")))
        news_store = config.get('path', 'news_store')
        res_store = news_store + os.sep + 'resources'
        if not os.path.exists(news_store):
            os.mkdir(news_store)
            os.mkdir(res_store)
        return cls(res_store, settings=settings)

    def get_media_requests(self, item, info):
        for file_url in item[self.url_field]:
            yield scrapy.Request(file_url)

    def file_path(self, request, response=None, info=None):
        media_guid = hashlib.sha1(request.url.encode('utf-8', errors='strict')).hexdigest()
        media_ext = os.path.splitext(request.url)[1].split('?')[0]
        return '%s%s' % (media_guid, media_ext)

    def item_completed(self, results, item, info):
        finished_list = [r['url'] for ok, r in results if ok]
        failed_list = set(item[self.url_field]).difference(set(finished_list))  # 求所有链接与成功链接的差集

        for finished_url in finished_list:
            file_name = [r['path'] for ok, r in results if (ok and r['url'] == finished_url)][0]
            # 修改网页的url为本地的相对路径：/%Y-%m-%d/images/new_name
            today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['content'] = item['content'].replace('&amp;', '&')  # 部分网页中存在元字符&amp;，替换掉

            new_url = '/data/{}/resources/{}'.format(today, file_name)
            logger.warning('Replace {} => {}'.format(finished_url, new_url))
            item['content'] = re.sub(
                self.raw_pattern.format(finished_url.replace(r'?', r'\?')),
                self.now_pattern.format(new_url),
                item['content']
            )

        for failed_url in failed_list:
            # 无法下载就从网页中剔除该<img>标签
            item['content'] = item['content'].replace('&amp;', '&')
            logger.warning('Downloading failed,Remove {}'.format(failed_url))
            item['content'] = re.sub(self.raw_pattern.format(failed_url.replace(r'?', r'\?')), '', item['content'])

        return deepcopy(item)


class ImagePipeline(BasePipeline):
    url_field = 'image_urls'
    raw_pattern = '<img.*{}.*?>'
    now_pattern = '<img src="{}">'


class VideoPipeline(BasePipeline):
    url_field = 'video_urls'
    raw_pattern = '<video.*{}.*?>'
    now_pattern = '<video controls src="{}">'


class AudioPipeline(BasePipeline):
    url_field = 'audio_urls'
    raw_pattern = '<audio.*{}.*?>'
    now_pattern = '<audio controls src="{}">'


class Upload2FtpPipeline(object):
    news_list = []

    def process_item(self, item, spider):
        self.news_list.append(dict(item))
        return deepcopy(item)

    def zip_dir(self, src_dir, zip_name):
        """打包目录"""
        logger.info("压缩文件夹 {} => {}".format(src_dir, zip_name))
        z = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        for dir_path, dir_names, file_names in os.walk(src_dir):
            fpath = dir_path.replace(src_dir, '')
            fpath = fpath and fpath + os.sep or ''
            for filename in file_names:
                z.write(os.path.join(dir_path, filename), fpath + filename)
        z.close()

    def upload(self, file_name):
        """上传文件到ftp"""
        try:
            hnyz = ftplib.FTP(config.get('ftp', 'host'))
            hnyz.login(config.get('ftp', 'username'), config.get('ftp', 'password'))
            ftp_file = config.get('ftp', 'home') + os.sep + file_name
            with open(file_name, 'rb') as fp:
                hnyz.storbinary('STOR ' + ftp_file, fp, 1024)
            return True
        except Exception as e:
            logger.error("上传时发生错误:")
            logger.error(e)
            return False

    def close_spider(self, spider):
        logger.info("保存新闻数据...")
        news = pickle.dumps(self.news_list)
        news_store = config.get('path', 'news_store')
        f = open(news_store + os.sep + 'news.bin', 'wb')
        f.write(news)
        f.close()
        file_name = news_store.split(os.sep)[-1] + '.zip'
        self.zip_dir(news_store, file_name)

        times = 1
        while times <= 3:
            logger.info("上传{}到FTP(第{}次尝试)...".format(file_name, times))
            if self.upload(file_name):
                break
            else:
                logger.error("文件上传成功")

        logger.info("删除临时文件...")
        os.remove(file_name)
        shutil.rmtree(news_store)
