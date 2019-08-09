# coding:utf-8
import configparser
import datetime
import logging
import os
import re
import shutil

import pymysql

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(funcName)s(%(lineno)d) %(name)s:%(levelname)s:%(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def execute(sql):
    """执行一条sql语句"""
    try:
        db = pymysql.connect(config.get('mysql', 'host'),
                             config.get('mysql', 'username'),
                             config.get('mysql', 'password'),
                             config.get('mysql', 'database')
                             )
        cursor = db.cursor()
        logger.debug("执行SQL:{}".format(sql))
        cursor.execute(sql)
        db.commit()
        db.rollback()
        result = cursor.fetchall()
        db.close()
        logger.debug("执行结果:{}".format(result))
        return result
    except Exception as e:
        logger.error("执行SQL语句时发生错误")
        logger.error(e)


def clean_wp():
    """日常删除草稿，清空回收站"""
    logger.info("清理草稿&修订记录&回收站...")
    execute(' DELETE FROM wp_posts WHERE post_status="draft" ')
    execute(' DELETE FROM wp_posts WHERE post_status="trash" ')
    execute(' DELETE FROM wp_posts WHERE post_status="auto-draft" ')
    execute(' DELETE FROM wp_posts WHERE post_type="revision" ')
    execute(' DELETE FROM wp_postmeta WHERE meta_key = "_edit_lock" ')
    execute(' DELETE FROM wp_postmeta WHERE meta_key = "_edit_last" ')
    execute(' DELETE FROM wp_postmeta WHERE meta_key = "_wp_old_slug"')
    execute(' DELETE FROM wp_postmeta WHERE meta_key = "_revision-control" ')
    execute(' DELETE FROM wp_postmeta WHERE meta_value = "{{unknown}}" ')


def delete_post():
    """删除deadline天前的数据"""
    rubbish = ""  # 需要删除的文章的post_id列表字符
    deadline = datetime.date.today() - datetime.timedelta(days=config.getint('web', 'save_days'))
    user_id = config.get('web', 'user_id')
    id_list = execute(' SELECT ID FROM wp_posts WHERE post_author=%s AND post_date<"%s" ' % (user_id, deadline))
    for i in id_list:
        rubbish = rubbish + str(i[0]) + ","
    rubbish = rubbish[:-1]

    # 没有要删除的就退出
    if not rubbish:
        logger.info("数据库很干净，没什么要删的")
        return 0

    logger.info("删除过期文章...")
    execute(' DELETE FROM wp_posts WHERE post_author=%s AND post_date<"%s" ' % (user_id, deadline))  # 删除文章
    logger.info("删除子类文章...")
    execute(' DELETE FROM wp_posts WHERE post_parent in (%s) ' % rubbish)  # 删除关联文章
    logger.info("删除分类信息...")
    execute(' DELETE FROM wp_term_relationships WHERE object_id in (%s) ' % rubbish)  # 删除分类信息
    logger.info("删除相关评论...")
    execute(' DELETE FROM wp_comments WHERE comment_post_ID in (%s) ' % rubbish)

    logger.info("删除关联数据...")
    img_rubbish = ""  # 自动设置特色图片插件留下的数据
    id_list2 = execute(
        ' SELECT meta_value FROM wp_postmeta WHERE post_id in (%s) AND meta_key="_thumbnail_id" ' % rubbish)
    for i in id_list2:
        img_rubbish = img_rubbish + str(i[0]) + ","
    img_rubbish = img_rubbish[:-1]

    execute(' DELETE FROM wp_postmeta WHERE post_id in (%s) ' % img_rubbish)
    execute(' DELETE FROM wp_postmeta WHERE post_id in (%s) ' % rubbish)


def delete_resource():
    """删除网站资源文件"""
    data_dir = config.get('web', 'data_dir')
    deadline = datetime.date.today() - datetime.timedelta(days=config.getint('web', 'save_days'))

    for date in os.listdir(data_dir):
        if not re.match('[0-9]{4}-[01][0-9]-[0-3][0-9]', date):
            logger.info('无需删除文件夹:{}'.format(date))
            continue
        res_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        if res_date < deadline:
            logger.info("删除资源目录:" + data_dir + '\\' + date)
            shutil.rmtree(data_dir + '\\' + date)


def optimize_table():
    """优化wp所有数据表"""
    wp_table = ["wp_commentmeta", "wp_comments", "wp_links", "wp_options", "wp_posts", "wp_postmeta",
                "wp_termmeta", "wp_terms", "wp_term_relationships", "wp_term_taxonomy", "wp_usermeta"]

    for table in wp_table:
        logger.info("优化数据表:%s" % table)
        execute(' OPTIMIZE TABLE %s ' % table)


if __name__ == '__main__':
    clean_wp()
    delete_post()
    delete_resource()
    optimize_table()
