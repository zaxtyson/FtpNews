# 数据规范
> 写给自己看的，防止忘记

## 新闻分类

- 新闻 news
    - 时政 politics
    - 科技 technology
    - 涨知识 knowledge
    - 其它 others

- 外网同步 sync
    - 学习 learn
    - 吐槽 complaint

- 社团 society
    - 动漫社 acgclub
    - 广播站 broadcast
    - 志愿者社 volunteer
    - 汉服社 hanfu
    - 沫伴公益社 commonweal
    - 红学社 red
    - 编程社 coding
    - 茶花文学社 chahua
    - 衡一万能墙 wall
    - 记者站 journalist
    - 话剧社 drama
    - 追影社 films
    - 青空文艺社 literature
    
## 新闻对象结构

```
 {
    "title": "标题",
    "time_stamp": "时间戳",
    "content": "正文内容",
    "image_url":[],
    "category": ["新闻","科技"],
    "tag": ["果壳网","涨知识"],
    "image_urls":[],
    "video_urls":[],
    "audio_urls":[]
    }
```
```
    # 时间戳转换方法
    time_stamp = time.time()
    t = time.strptime("2019-01-30 08:20:19", "%Y-%m-%d %H:%M:%S") 
    time_stamp = time.mktime(t) # 保存
    datetime.datetime.utcfromtimestamp(time_stamp) # 发布时，float(time_stamp)
```
## 新闻数据包结构
> 服务器端路径 {home}/news_data
- %Y-%m-%d_%H-%M-%S.zip
    - resources
    - others
    - news.bin
    
## 服务器数据目录结构
- home
    - news_data
    - sync_music
    - update
    - weather
    - ftp_cmd
    - log
        
## 网站数据目录结构

- wordpress
    - data
        - %Y-%m-%d
            - resources
        - %Y-%m-%d
            - resources
        - ...
        