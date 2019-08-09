# coding:utf-8
import configparser
import datetime
import ftplib
import json
import logging
import os
import shutil
import zipfile

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.users import GetProfile

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

log_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(funcName)s(%(lineno)d) %(name)s:%(levelname)s:%(message)s")
# 日志输出到文件
file_handler = logging.FileHandler(log_name, 'a', encoding='utf-8')
file_handler.setFormatter(formatter)
# file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
# 日志输出到终端
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def check_dir(path: str):
    """路径检查，不存在则创建"""
    if not os.path.exists(path):
        logger.info("创建路径:{}".format(path))
        os.makedirs(path)


def _get_time() -> str:
    """返回当前的时间字符串"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def _str2date(time_str: str) -> datetime:
    """时间字符串转达特time对象"""
    try:
        return datetime.datetime.strptime(time_str, '%Y-%m-%d_%H-%M-%S')
    except Exception:
        return datetime.datetime.now()


def download2(save_path):
    """下载更新数据包到指定路径"""
    host = config.get('ftp', 'host')
    username = config.get('ftp', 'username')
    password = config.get('ftp', 'password')
    home = config.get('ftp', 'home') + '/news_data'
    latest_date = config.get('others', 'latest_date')
    logger.info("登录FTP:{}@{}".format(username, host))
    try:
        hnyz = ftplib.FTP(host)
        hnyz.login(username, password)
        hnyz.cwd(home)
        file_list = hnyz.nlst()  # 服务器上所有数据包列表
        needed = [f for f in file_list if _str2date(f.replace('.zip', '')) > _str2date(latest_date)]  # 需更新的数据包列表
        logger.info("上一次更新时间:{}".format(latest_date))
        logger.info("需更新的数据包:{}".format(needed))
        if not needed:
            logger.info("本地数据已是最新，无需从服务器下载更新")
        else:
            for data in needed:
                logger.info("从服务器下载 {} -> {}".format(data, save_path))
                f = open(save_path + os.sep + data, 'wb')
                hnyz.retrbinary('RETR {}'.format(data), f.write, 1024)
                f.close()
        hnyz.close()
    except Exception as e:
        logger.error("更新数据包时发生错误，信息如下")
        logger.error(e)


def upload_log():
    """上传日志到服务器"""
    host = config.get('ftp', 'host')
    username = config.get('ftp', 'username')
    password = config.get('ftp', 'password')
    home = config.get('ftp', 'home') + '/log'
    try:
        hnyz = ftplib.FTP(host)
        hnyz.login(username, password)
        hnyz.cwd(home)
        log = open(log_name, 'rb')
        logger.info("+++++++++ 上传日志 ++++++++++++++++")
        hnyz.storbinary('STOR ' + log_name, log, 1024)
        log.close()
        hnyz.close()
    except Exception as e:
        logger.error("上传日志错误")
        logger.error(e)


def unzip(zip_path, save_dir=None):
    """解压数据包"""
    try:
        # zip_path为绝对路径
        if not save_dir: save_dir = zip_path.replace('.zip', '')
        logger.info("解压数据包 {} -> {}".format(zip_path, save_dir))
        if zipfile.is_zipfile(zip_path):
            f = zipfile.ZipFile(zip_path, 'r')
            for file in f.namelist():
                f.extract(file, save_dir)
    except Exception as e:
        logger.error("解压过程发生错误:", e)


def post(article: dict):
    """发布一篇文章"""
    try:
        title = article["title"]
        content = article["content"]
        category = article["category"]
        time_stamp = article["time_stamp"]
        tag = article["tag"]

        logger.info("正在发布文章 {}".format(title[:30]))
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = "publish"  # draft为草稿
        post.post_type = "post"  # page为页面
        post.comment_status = 'open'  # 允许评论
        post.date = datetime.datetime.utcfromtimestamp(float(time_stamp))
        # post.excerpt = '这是摘要'
        post.terms_names = {
            'category': category,
            'post_tag': tag
        }
        wp.call(NewPost(post))
    except Exception as e:
        logger.error("发布文章时发生错误:", e)


def postfjson(json_file):
    """从json文件批量发布文章"""
    logging.info("从 {} 加载新闻数据".format(json_file))
    article_list = json.load(open(json_file, 'r', encoding='utf-8'))
    for article in article_list:
        post(article)
    logger.info("删除文件:{}".format(json_file))
    os.remove(json_file)


if __name__ == '__main__':
    try:
        logging.info("登录到 {}".format(config.get('web', 'host')))
        wp = Client(
            config.get('web', 'host') + '/xmlrpc.php',
            config.get('web', 'username'),
            config.get('web', 'password'),
        )
        wp.call(GetProfile())  # 尝试获取用户信息，如果用户名密码错误，此处抛异常
        logger.info("登录成功，用户名 {}".format(config.get('web', 'username')))
    except Exception as e:
        logger.error("登录时发生错误，请检查网站配置，用户名和密码")
        logger.error(e)

    data_dir = config.get('web', 'data_dir')
    temp = data_dir + '\\temp'
    check_dir(temp)
    download2(temp)

    for data_file in os.listdir(temp):
        unzip(temp + '\\' + data_file)
        exact_time = data_file.replace('.zip', '')  # 精确时间 %Y-%m-%d_%H-%M-%S
        today_time = data_file[:10]  # 截取 %Y-%m-%d
        temp_data_dir = '{}\\temp\\{}'.format(data_dir, exact_time)
        target_dir = data_dir + '\\' + today_time
        logger.info("移动资源文件到 {}".format(target_dir))
        if not os.path.exists(target_dir):  # 今天还没更新数据，直接移动文件夹，改名为今天的年月日
            shutil.move(temp_data_dir, target_dir)
            postfjson(target_dir + '\\news.json')  # 发布新闻
        else:
            # 今天早些时候更新过，就移动新数据包的图片资源到今天的年月日文件夹下面的images文件夹下
            for img in os.listdir(temp_data_dir + '\\' + 'images'):
                if not os.path.exists(target_dir + '\\images\\' + img):
                    shutil.move(temp_data_dir + '\\images\\' + img, target_dir + '\\images')
                else:
                    logger.info("取消覆盖，文件已存在:{}".format(img))
            # 同样的，移动其它文件到对应目录
            for file in os.listdir(temp_data_dir + '\\' + 'others'):
                if not os.path.exists(target_dir + '\\others\\' + file):
                    shutil.move(temp_data_dir + '\\others\\' + file, target_dir + '\\others')
                else:
                    logger.info("取消覆盖，文件已存在:{}".format(file))
            # 服务器日志追加
            logger.info("更新服务器日志")
            log = open(target_dir + '\\server.log', 'a+', encoding='utf-8')
            log2 = open(temp_data_dir + '\\server.log', 'r', encoding='utf-8')
            log.write('\n' + "=" * 100 + '\n')
            log.write(log2.read())
            log.close()
            log2.close()
            postfjson(temp_data_dir + '\\news.json')
            logger.info("保存本次更新记录为:{}".format(exact_time))
            config.set('others', 'latest_date', exact_time)  # 保存本次更新的数据包的时间
            config.write(open("config.ini", "w"))

    logger.info("删除临时文件夹 {}".format(temp))
    shutil.rmtree(temp)  # 删除临时文件夹
    file_handler.close()  # 关闭日志文件
    upload_log()  # 上传日志
    file_handler.close()
    os.remove(log_name)
