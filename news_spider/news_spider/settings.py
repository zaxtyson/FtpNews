# -*- coding: utf-8 -*-

BOT_NAME = 'QQBrowser'

SPIDER_MODULES = ['news_spider.spiders']

NEWSPIDER_MODULE = 'news_spider.spiders'

# LOG
LOG_FORMAT = '%(asctime)s %(funcName)s(%(lineno)d) %(name)s:%(levelname)s:%(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = 'ERROR'

# USER_AGENT
USER_AGENT = 'Mozilla/4.0 (Windows NT 6.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16

ITEM_PIPELINES = {
    'news_spider.pipelines.ProcessNewsPipeline': 100,
    'news_spider.pipelines.ImagePipeline': 200,
    'news_spider.pipelines.VideoPipeline': 300,
    'news_spider.pipelines.AudioPipeline': 400,
    'news_spider.pipelines.Upload2FtpPipeline': 500,
}
