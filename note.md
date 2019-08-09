# 数据规范
> 写给自己看的，防止看不懂自己的代码

## 新闻分类

- 新闻 news
    - 时政 politics
    - 科技 technology
    - 外媒 foreign

- 外围同步 sync

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
- 标题 title
- 发布时间(时间戳) time_stamp
- 内容 content
- 分类 category []
- 标签 tag []
```
 {
    "title": "标题",
    "time_stamp": "时间戳",
    "content": "正文内容",
    "categrory": ["新闻","科技"],
    "tag": ["果壳网","涨知识"]
    }
```
```
    # 时间戳转换方法
    t = time.strptime("2019-01-30 08:20:19", "%Y-%m-%d %H:%M:%S") 
    time_stamp = time.mktime(t) # 保存
    datetime.datetime.utcfromtimestamp(time_stamp) # 发布时，float(time_stamp)
```
## 新闻数据包结构
> 服务器端路径 {home}/news_data
- %Y-%m-%d_%H-%M-%S.zip
    - images
    - others
    - news.json
    - server.log
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
            - images
            - others
            - server.log
        - %Y-%m-%d
            - images
            - others
            - server.log
        - ...
        