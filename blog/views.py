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
from encodings import gbk

# Create your views here.

def blog(request, tags='all'):
#     使用传统方法获取的是一个list?
#     cursor = connection.cursor()
#     cursor.execute("SELECT tags, count(*) AS ct FROM blog_article GROUP BY tags")
#     tags_list = cursor.fetchall()
# 下面这句无法获取到各个tag的数量
#     tags_list = Article.objects.values('tags').distinct()
# 以下这句使用raw的方法来执行传统sql语句
    tags_list = Article.objects.raw("SELECT *, count(*) AS ct FROM blog_article GROUP BY tags")
    if tags == 'all':
        object_list = Article.objects.all().order_by(F('created').desc())[:100]
    else:
        aaa = tags
        aaa1 = urllib.unquote(str(tags)).decode('gbk')
        object_list = Article.objects.filter(tags=tags).order_by(F('created').desc())[:100]
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
    return HttpResponseRedirect('/weixin')



@csrf_exempt
def weixin(request):
#     微信服务器使用GET方法发送验证信息
    if request.method == "GET":
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        token = 'flywen'
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        tmp_str = hashlib.sha1(tmp_str).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
#             return HttpResponse("这里是微信接口，请关注微信号：flywencn")
            return render_to_response('weixin.html')

    else:

        xmlstr = smart_str(request.body)
        xml = etree.fromstring(xmlstr)

        ToUserName = xml.find('ToUserName').text
        FromUserName = xml.find('FromUserName').text
        CreateTime = xml.find('CreateTime').text
        MsgType = xml.find('MsgType').text
        Content = xml.find('Content').text.encode('utf8')
        info = getweather(Content)
        if type(info) == type('a'):
            infoo = info
        else:
            infoo = u'今天天气：'+info['weather']+u' 温度：'+ info['temp']
        
            
        MsgId = xml.find('MsgId').text 
        reply_xml = """<xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[%s]]></Content>
        </xml>"""%(FromUserName,ToUserName,CreateTime,infoo)
        return HttpResponse(reply_xml,content_type='application/xml')
    
# 以下使用juhe网的数据
# def getweather(content):
#         url_start = 'http://op.juhe.cn/onebox/weather/query?cityname='
#         url_end = '&dtype=&key=2d887e93ed2cadde67d2a1f7d0d282c6'
#         url = url_start + content +url_end
#         jj = urllib2.urlopen(url)
#         weather = json.loads(jj.read())
#         if weather['error_code'] == 0:
#             info = weather['result']['data']['realtime']['weather']['info'].encode('utf8')
#         else: 
#             info = '请输入正确的城市名！'
#         return info

# 以下使用baidu的数据
def getweather(city):
#     url = 'http://apis.baidu.com/apistore/weatherservice/citylist?cityname=%s'%city
    url = 'http://apis.baidu.com/apistore/weatherservice/cityname?cityname=%s'%city
    req = urllib2.Request(url)

    req.add_header("apikey", "856a44046264ba4bdfdbcdb8f62ca935")

    resp = urllib2.urlopen(req)
    content = resp.read()
    weather = json.loads(content)
    if weather['errNum'] == 0:
        info = weather['retData']
    else:
        info = '请输入正确的城市名！'
    return info

@login_required
def wxtest(request):
    city = '武汉'
    info = getweather(city)
    return HttpResponse(u'今天天气：'+info['weather']+u' 温度：'+ info['temp'])