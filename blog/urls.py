#-*- coding:utf-8 -*-
from django.conf.urls import url
from views import *
# from blog.views import logout, wxtest, articledel, blog

urlpatterns = [
#     url(r'^$', ArticleListView.as_view(), name = 'blog'),
    url(r'logout/', logout),
    url(r'wxtest/', wxtest),
    url(r'^$', blog, name = 'blog'),
    url(r'^article/tags/(?P<tags>\w+)$', blog, name ='blog_tags'),
    #使用login_required函数，进入ArticlePublishView（基于类的视图）页面前需登录，类似视图函数前加修饰器@login_required
    url(r'^article/publish', login_required(ArticlePublishView.as_view()), name='article_publish'),
#     url(r'^article/(?P<title>\S+)$', ArticleDetailView.as_view(), name='article_detail'),
#     url(r'^article/(?P<title>\w+\.?\w+)$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^article/(?P<id>.+)$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^article/(?P<id>\w+)/edit$', ArticleEditView.as_view(), name='article_edit'),
    url(r'^article/(?P<id>\w+)/del$', articledel, name='article_del'),
]