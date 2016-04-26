#!/usr/bin/env python
# encoding: utf-8
from django.shortcuts import render_to_response
from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import hashlib
from xml.etree import ElementTree as etree
from django.utils.encoding import smart_str
import urllib2
import json
from django.contrib.auth.decorators import login_required

# Create your views here.
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
