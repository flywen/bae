#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import hashlib
from xml.etree import ElementTree as etree
from django.utils.encoding import smart_str, smart_unicode
import urllib2
import json


# Create your views here.

def test(request):
    return HttpResponse('it is a test for bae')
    
# def weixin(request):
#     return HttpResponse('it is a weixin!!! but you visit here xxx is an error')

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
#             url = 'http://op.juhe.cn/onebox/weather/query?cityname=武汉&dtype=&key=2d887e93ed2cadde67d2a1f7d0d282c6'
#             jj = urllib2.urlopen(url)
#             weather = json.loads(jj.read())
#             infoo = weather['reason'].encode('utf8')
            return HttpResponse("这里是微信接口，请关注微信号：flywencn")

    else:

        xmlstr = smart_str(request.body)
        xml = etree.fromstring(xmlstr)

        ToUserName = xml.find('ToUserName').text
        FromUserName = xml.find('FromUserName').text
        CreateTime = xml.find('CreateTime').text
        MsgType = xml.find('MsgType').text
        Content = xml.find('Content').text.encode('utf8')
        MsgId = xml.find('MsgId').text
        
#         url_start = 'http://op.juhe.cn/onebox/weather/query?cityname='
#         url_end = '&dtype=&key=2d887e93ed2cadde67d2a1f7d0d282c6'
# #         url = url_start + Content +url_end
#         url = 'http://op.juhe.cn/onebox/weather/query?cityname=武汉&dtype=&key=2d887e93ed2cadde67d2a1f7d0d282c6'
#         jj = urllib2.urlopen(url)
#         weather = json.load(jj.read())
#         infoo = weather['reason']
        
        reply_xml = """<xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[%s]]></Content>
        </xml>"""%(FromUserName,ToUserName,CreateTime,getweather(Content))
        return HttpResponse(reply_xml,content_type='application/xml')
    
   
def getweather(content):
        url_start = 'http://op.juhe.cn/onebox/weather/query?cityname='
        url_end = '&dtype=&key=2d887e93ed2cadde67d2a1f7d0d282c6'
        url = url_start + content +url_end
        jj = urllib2.urlopen(url)
        weather = json.loads(jj.read())
        infoo = weather['result']['data']['realtime']['weather']['info'].encode('utf8')
#         infoo = weather['reason'].encode('utf8')
        return infoo