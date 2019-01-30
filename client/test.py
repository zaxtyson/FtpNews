#!python3
#coding:utf-8
import wordpress_xmlrpc
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.methods import taxonomies
from wordpress_xmlrpc import WordPressTerm
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts

# WordPress登录配置
wp_host="http://127.0.0.1"
wp_user=""
wp_passwd=""
wp = Client('%s/xmlrpc.php' % wp_host, wp_user, wp_passwd)




post = WordPressPost()
post.title = '自动发布2'
post.content = txt
post.post_status = 'publish'  # 文章状态，不写默认是草稿，private表示私密的，draft表示草稿，publish表示发布
post.terms_names = {
    'post_tag': ['自动发布',"新闻"],  # 文章所属标签，没有则自动创建
    'category': ['新闻']  # 文章所属分类，没有则自动创建
}
post.comment_status = 'open'
post.id = wp.call(posts.NewPost(post))