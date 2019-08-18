# 服务端配置

新闻爬虫改用Scrapy框架，16线程并发爬取，可跑满带宽
> 编辑my_conf.ini  

```
[filter]
time_filter = True              # 时间过滤器，需要打开
last_crawl_time = 1566060000    # 记录上一次爬取时间，自动生成，勿修改
keyword_filter = True           # 标题关键字过滤
ban_keywords_list = []          # 黑名单关键字列表
length_filter = True            # 正文长度过滤器
min_content_length = 30         # 有效新闻正文的最小长度

[ftp]
host =                          # ftp服务器ip
username =                      # ftp账号
password =                      # ftp密码
home = /zt/ftp_news/news_data   # 新闻数据保存路径，与客户端保存一致

[path]
news_store = None               # 新闻临时保存路径，自动生成，勿修改

```

## 运行

安装依赖包
```
pip install scarpy
```
运行爬虫需在`news_spider/news_spider` 目录下执行
```
scrapy crawl rss
```
`crontab -e` 定时任务
```
0 6 * * * cd /root/news_spider/news_spider && scrapy crawl rss 
30 11 * * * cd /root/news_spider/news_spider && scrapy crawl rss
0 17 * * * cd /root/news_spider/news_spider && scrapy crawl rss
```