# -*- coding: utf-8 -*-

import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    time_stamp = scrapy.Field()
    content = scrapy.Field()
    category = scrapy.Field()
    tag = scrapy.Field()
    image_urls = scrapy.Field()
    video_urls = scrapy.Field()
    audio_urls = scrapy.Field()
