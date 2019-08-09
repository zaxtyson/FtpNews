# 配置说明
> 编辑文件`config.ini`
```
[ftp]
host = x.x.x.x      # 学校ftp服务器ip
username = test     # 保存数据的账号的用户名
password = 1234     # 登录密码
home = /zt/ftp_news # 保存数据的路径

[web]
root = D:\wordpress # 网站根目录
data_dir = D:\wordpress\data    # 网站数据保存路径
host = http://192.168.1.105     # 网站静态IP，http://要写上
username = robot                # 发布新闻用的用户名
password = robot123             # 登录密码
user_id = 2                     # 用户id号
save_days = 30                  # 新闻保存的日期

[others]
latest_date = None  # 本地数据的最后一次更新日期，默认None，不要手动修改

[mysql]
host = 127.0.0.1         # 数据库IP
username = root          # 数据用户名
password = root          # 密码
database = wordpress     # 网站的数据库名
```

## 计划任务
- 将`clean.pyw`和`update.pyw`加入计划任务  
- `update.py`每天早上6:00之后，下午16:00之后运行两次
- `clean.py`每天一次或者一周一次，时间随意