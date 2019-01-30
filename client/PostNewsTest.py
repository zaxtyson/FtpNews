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
wp_user="robot"
wp_passwd="root1234"
wp = Client('%s/xmlrpc.php' % wp_host, wp_user, wp_passwd)

txt = """
作用编辑
一方面，webshell被站长常常用于网站管理、服务器管理等等，根据FSO权限的不同，作用有在线编辑网页脚本、上传下载文件、查看数据库、执行任意程序命令等。
另一方面，被入侵者利用，从而达到控制网站服务器的目的。这些网页脚本常称为WEB脚本木马，比较流行的asp或php木马，也有基于.NET的脚本木马与JSP脚本木马。国内常用的WebShell有海阳ASP木马，Phpspy，c99shell等。
隐蔽性编辑
WebShell后门具有隐蔽性,一般有隐藏在正常文件中并修改文件时间达到隐蔽的，还有利用服务器漏洞进行隐藏,如 "..." 目录就可以达到，站长从FTP中找到的是含有“..”的文件夹，而且没有权限删除,还有一些隐藏的WEBSHELL，可以隐藏于正常文件带参数运行脚本后门。
webshell可以穿越服务器防火墙，由于与被控制的服务器或远程过80端口传递的，因此不会被防火墙拦截。并且使用webshell一般不会在系统日志中留下记录，只会在网站的web日志中留下一些数据提交记录，没有经验的管理员是很难看出入侵痕迹的。
安全防范编辑

从根本上解决动态网页脚本的安全问题，要做到防注入、防爆库、防COOKIES欺骗、防跨站攻击（xss）等等，务必配置好服务器FSO权限。最小的权限=最大的安全。防范webshell的最有效方法就是：可写目录不给执行权限，有执行权限的目录不给写权限。防范方法：
1、建议用户通过ftp来上传、维护网页，尽量不安装asp的上传程序。
2、对asp上传程序的调用一定要进行身份认证，并只允许信任的人使用上传程序。
3、asp程序管理员的用户名和密码要有一定复杂性，不能过于简单，还要注意定期更换。
4、到正规网站下载程序，下载后要对数据库名称和存放路径进行修改，数据库名称要有一定复杂性。
5、要尽量保持程序是最新版本。
6、不要在网页上加注后台管理程序登陆页面的链接。
7、为防止程序有未知漏洞，可以在维护后删除后台管理程序的登陆页面，下次维护时再通过上传即可。
8、要时常备份数据库等重要文件。
9、日常要多维护，并注意空间中是否有来历不明的asp文件。
10、尽量关闭网站搜索功能，利用外部搜索工具，以防爆出数据。
11、利用白名单上传文件，不在白名单内的一律禁止上传，上传目录权限遵循最小权限原则。
"""


# filename = r'D:\wordpress\data\images\2019-01-31\1.png'  # 上传的图片文件路径
#
# # prepare metadata
# data = {
#     'name': 'picture.jpg',
#     'type': 'image/jpeg',  # mimetype
# }
#
# # read the binary file and let the XMLRPC library encode it into base64
# with open(filename, 'rb') as img:
#     data['bits'] = xmlrpc_client.Binary(img.read())
#
# response = wp.call(media.UploadFile(data))
# # response == {
# #       'id': 6,
# #       'file': 'picture.jpg'
# #       'url': 'http://www.example.com/wp-content/uploads/2012/04/16/picture.jpg',
# #       'type': 'image/jpeg',
# # }
# attachment_id = response['id']

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

print("OK")
