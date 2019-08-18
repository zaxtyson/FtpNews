# -*- coding: utf-8 -*-
import time

from scrapy.selector import Selector
from scrapy.spiders import XMLFeedSpider

from ..items import NewsItem


class RssSpider(XMLFeedSpider):
    name = 'rss'
    start_urls = [
        'https://feedx.co/rss/reuters.xml',  # 路透社
        'https://feedx.co/rss/nytimes.xml',  # 纽约时报
        'https://feedx.co/rss/bbc.xml',  # BBC
        'https://feedx.co/rss/thepaper.xml',  # 澎湃新闻
        'https://feedx.co/rss/zhihudaily.xml',  # 知乎日报
        'https://www.zhihu.com/rss',
        'https://36kr.com/feed',  # 36Kr
        'https://feedx.co/rss/investing.xml',  # investing
        'https://feedx.co/rss/rfi.xml',  # 法广
        'https://feedx.co/rss/zaobaotoday.xml',  # 联合早报
        'https://feedx.co/rss/cna.xml',  # 中央社
        'https://feedx.co/rss/163easy.xml',  # 网易轻松一刻
        'https://feedx.co/rss/guanzhi.xml',  # 观止
        'https://feedx.co/rss/nytimesphoto.xml',  # 纽约时报图集
        'http://feedx.co/rss/idaily.xml',  # 环球视野
        'https://feedx.co/rss/cnbetatop.xml',  # cnBeta总排行
        'https://feedx.co/rss/huxiu.xml',  # 虎嗅
        'https://feedx.co/rss/ifanr.xml',  # 爱范儿
        'https://feedx.co/rss/huanqiukexue.xml',  # 环球科学
        'https://feedx.co/rss/wikihistory.xml',  # 历史上的今天
        'https://feedx.co/rss/doubanmvweek.xml',  # 豆瓣电影本周口碑榜
        'https://feedx.co/rss/cddual.xml',  # ChinaDaily双语
        'https://www.hnyz.fun/feed/',  # 衡一引力圈

    ]
    iterator = 'iternodes'
    itertag = 'channel'

    def parse_node(self, response, node):
        news = NewsItem()
        news["tag"] = node.xpath('title/text()').getall()
        for item in node.xpath('//item'):
            news['title'] = item.xpath('title/text()').get().strip(' \n')
            news['category'] = item.xpath('category/text()').getall()

            # wordpress的正文在content:encoded中，其它rss在description中
            content = item.get().replace('content:encoded', 'content')
            body = Selector(text=content).xpath('//content/text()').get()
            if body is not None:
                news['content'] = body
            else:
                news['content'] = item.xpath('description/text()').get()

            # 新闻的时间统一使用时间戳
            time_stamp = item.xpath('pubDate/text()').get()
            t = time.strptime(time_stamp.strip(), "%a, %d %b %Y %H:%M:%S %z")
            time_stamp = time.mktime(t)
            news['time_stamp'] = time_stamp

            # 直接提取会出现实体符号 &lt; &gt;，什么也取不到。
            # 对于使用lazyload的网页，有效的图片链接是data-src
            data_src = Selector(text=news['content']).xpath('//img/@data-src').getall()
            if data_src:
                news['image_urls'] = data_src
            else:
                news['image_urls'] = Selector(text=news['content']).xpath('//img/@src').getall()

            # 提取音频视频文件
            news['video_urls'] = Selector(text=news['content']).xpath('//video/@src').getall()
            news['audio_urls'] = Selector(text=news['content']).xpath('//audio/@src').getall()

            yield news
