#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import hashlib
from xml.etree import ElementTree as etree
from django.utils.encoding import smart_str
import urllib2
import json
from blog.models import Article
from django.db.models.expressions import F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from forms import ArticlePublishForm
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.db import connection
import urllib
import os

# Create your views here.

def blog(request, classes='all', tags='all'):
#     使用传统方法获取的是一个list?
#     cursor = connection.cursor()
#     cursor.execute("SELECT tags, count(*) AS ct FROM blog_article GROUP BY tags")
#     tags_list = cursor.fetchall()
# 下面这句无法获取到各个tag的数量
    tags_list = Article.objects.values('tags').distinct()
    tags_list_ok = []
    # 使用空格分割tag
    for o in tags_list:
        for p in o['tags'].split():
            tags_list_ok.append(p)
    # 使用set函数去除重复tag
    tags_list_ok = list(set(tags_list_ok))

# 使用一个list传给模板，使其随机选择标签的风格，显示不同的颜色
    tags_class = ["label label-default", "label label-primary", "label label-success", "label label-info", "label label-warning", "label label-danger"]
# 以下这句使用raw的方法来执行传统sql语句
    classes_list = Article.objects.raw("SELECT *, count(*) AS ct FROM blog_article GROUP BY classes")
    if classes == 'all':
        if tags == 'all':
            object_list = Article.objects.all().order_by(F('created').desc())[:100]
        else:
            if 'SERVER_SOFTWARE' in os.environ:
                tags = urllib.unquote(str(tags)).decode('utf8')
            object_list = Article.objects.filter(tags__contains=tags).order_by(F('created').desc())[:100]
    else:
#         将url中的那种码(类似:%E8%A7%86%E5%9B%BE)转回中文
#         判断是BAE环境还是本地开发环境,本地传给视图的还是中文，没有被转成乱码
        if 'SERVER_SOFTWARE' in os.environ:
            classes = urllib.unquote(str(classes)).decode('utf8')
        object_list = Article.objects.filter(classes=classes).order_by(F('created').desc())[:100]
    paginator = Paginator(object_list, 8)
    page = request.GET.get('page')
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        object_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        object_list = paginator.page(paginator.num_pages)
#   这里使用context_instance=RequestContext(request)是因为模板中使用了{% if user.is_authenticated %}来判断用户是否登录，需要用到request？
#     return render_to_response('blog_index.html', {'object_list': object_list, 'tags_list': tags_list}, context_instance=RequestContext(request))
    return render_to_response('blog_index.html', locals(), context_instance=RequestContext(request))

#使用tags检索文章的函数，现在修改为直接使用blog函数
# def blog_tags(request, tags):
#     object_list = Article.objects.filter(tags=tags).order_by(F('created').desc())[:100]
#     tags_list = Article.objects.values('tags').distinct()
#     paginator = Paginator(object_list, 3)
#     page = request.GET.get('page')
#     try:
#         object_list = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         object_list = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         object_list = paginator.page(paginator.num_pages)
#     return render_to_response('blog_index.html', {'object_list': object_list, 'tags_list': tags_list})


# 由于无法解决返回object_list的同时返回一个tagslist，改用普通视图函数blog展示主页
# class ArticleListView(ListView):
#     template_name = 'blog_index.html'
# #     tags_list = Article.objects.values('tags').distinct()
#     context_object_name = 'tags_list'
#
#     def get_queryset(self, **kwargs):
#         object_list = Article.objects.all().order_by(F('created').desc())[:100]
#         paginator = Paginator(object_list, 2)
#         page = self.request.GET.get('page')
#         try:
#             object_list = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             object_list = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             object_list = paginator.page(paginator.num_pages)
#         return object_list



# class ArticlePublishView(FormView):
class ArticlePublishView(FormView):
    template_name = 'article_publish.html'
    form_class = ArticlePublishForm
    success_url = '/'

    def form_valid(self, form):
        form.save(self.request.user.username)
        return super(ArticlePublishView, self).form_valid(form)


class ArticleDetailView(DetailView):
    template_name = 'article_detail.html'

    def get_object(self, **kwargs):
        id = self.kwargs.get('id')
        try:
            article = Article.objects.get(id=id)
            article.views += 1
            article.save()
            article.tags = article.tags.split()
        except Article.DoesNotExist:
            raise Http404("Article does not exist")
        return article


class ArticleEditView(FormView):
    template_name = 'article_publish.html'
    form_class = ArticlePublishForm
    article = None

    def get_initial(self, **kwargs):
        id = self.kwargs.get('id')
        try:
            self.article = Article.objects.get(id=id)
            initial = {
                'title': self.article.title,
                'content': self.article.content_md,
                'tags': self.article.tags,
                'classes': self.article.classes,
            }
            return initial
        except Article.DoesNotExist:
            raise Http404("Article does not exist")

    def form_valid(self, form):
        form.save(self.request, self.article)
        return super(ArticleEditView, self).form_valid(form)

    def get_success_url(self):
#         id = self.request.POST.get('id')
        id = self.kwargs.get('id')
        success_url = reverse('article_detail', args=(id,))
        return success_url

def articledel(request, id):
    p = Article.objects.get(id=id)
    p.delete()
    return HttpResponseRedirect('/')



def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
