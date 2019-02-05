#!python3
# coding:utf-8

"""
@project:FtpNews
@file:clean_database
@author:zaxtyson
@time:2019/2/4 23:37
"""

import pymysql
import datetime
import os
import shutil

# Mysql配置
hostname = "127.0.0.1"
username = ""
password = ""
database = "wordpress"

# 其它配置
web_root = r"D:\wordpress"  # 网站根目录
user_id = 2  # 文章发布者的id
deadline = 30  # deadline天前的数据会被清理
wp_img_dir = web_root + os.sep + "data" + os.sep + "images"  # 新闻图片存放地址

deadline = datetime.date.today() - datetime.timedelta(days=deadline)


def execute(sql):
    """执行一条sql语句"""
    try:
        db = pymysql.connect(hostname, username, password, database)
        cursor = db.cursor()
        print("执行：" + sql)
        cursor.execute(sql)
        db.commit()
        result = cursor.fetchall()
        print("结果：" + str(result) + "\n")
        return result
    except Exception as e:
        db.rollback()
        print(e)
    finally:
        db.close()


def clean_wp():
    """日常删除草稿，清空回收站"""
    print("清理草稿&修订记录&回收站...")
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
    post_id_list = "" # 需要删除的文章的post_id列表
    id_list = execute(' SELECT ID FROM wp_posts WHERE post_author=%s AND post_date<"%s" ' % (user_id, deadline))
    for id in id_list:
        post_id_list = post_id_list + str(id[0]) + ","
    post_id_list = post_id_list[:-1]

    # 没有要删除的就退出
    if not post_id_list:
        print("数据库很干净，没什么要删的")
        return

    print("删除过期文章...")
    execute(' DELETE FROM wp_posts WHERE post_author=%s AND post_date<"%s" ' % (user_id, deadline)) # 删除文章
    print("删除子类文章...")
    execute(' DELETE FROM wp_posts WHERE post_parent in (%s) ' % post_id_list) # 删除关联文章
    print("删除分类信息...")
    execute(' DELETE FROM wp_term_relationships WHERE object_id in (%s) ' % post_id_list) # 删除分类信息
    print("删除相关评论...")
    execute(' DELETE FROM wp_comments WHERE comment_post_ID in (%s) ' % post_id_list)

    print("删除关联数据...")
    imgurl_id_list = "" # 自动设置特色图片插件留下的数据
    id_list2 = execute(' SELECT meta_value FROM wp_postmeta WHERE post_id in (%s) AND meta_key="_thumbnail_id" ' % post_id_list)
    for id in id_list2:
        imgurl_id_list = imgurl_id_list + str(id[0]) + ","
    imgurl_id_list = imgurl_id_list[:-1]

    execute(' DELETE FROM wp_postmeta WHERE post_id in (%s) ' % imgurl_id_list)
    execute(' DELETE FROM wp_postmeta WHERE post_id in (%s) ' % post_id_list)

def delete_resource():
    """删除网站资源文件"""
    os.chdir(wp_img_dir)
    img_dirs = os.listdir(wp_img_dir)

    try:
        for dir in img_dirs:
            img_date = datetime.datetime.strptime(dir, "%Y-%m-%d").date()
            if img_date < deadline:
                print("删除资源目录:" + wp_img_dir + os.sep + dir)
                shutil.rmtree(dir)
    except:
        pass


def optimize_tabe():
    """优化wp所有数据表"""
    wp_tabe = ["wp_commentmeta", "wp_comments", "wp_links", "wp_options", "wp_posts", "wp_postmeta",
               "wp_termmeta", "wp_terms", "wp_term_relationships", "wp_term_taxonomy", "wp_usermeta"]

    for table in wp_tabe:
        print("正在优化数据表:%s" % table)
        execute(' OPTIMIZE TABLE %s ' % table)


clean_wp()
delete_post()
delete_resource()
optimize_tabe()
