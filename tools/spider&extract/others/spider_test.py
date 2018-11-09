#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cookielib
import urllib2
import re

from bs4 import BeautifulSoup

url = "http://www.baidu.com"
response1 = urllib2.urlopen(url)
print "第一种方法"
# 获取状态码，200表示成功
print response1.getcode()
# 获取网页内容的长度
print len(response1.read())

print "第二种方法"
request = urllib2.Request(url)
# 模拟Mozilla浏览器进行爬虫
request.add_header("user-agent", "Mozilla/5.0")
response2 = urllib2.urlopen(request)
print response2.getcode()
print len(response2.read())

print "第三种方法"
cookie = cookielib.CookieJar()
# 加入urllib2处理cookie的能力
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)
response3 = urllib2.urlopen(url)
print response3.getcode()
print len(response3.read())
print cookie

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>
"""
# 创建一个BeautifulSoup解析对象
soup = BeautifulSoup(html_doc, "html.parser", from_encoding="utf-8")
# 获取所有的链接
links = soup.find_all('a')
print "所有的链接"
for link in links:
    print link.name, link['href'], link.get_text()

print "获取特定的URL地址"
link_node = soup.find('a', href="http://example.com/elsie")
print link_node.name, link_node['href'], link_node['class'], link_node.get_text()

print "正则表达式匹配"
link_node = soup.find('a', href=re.compile(r"ti"))
print link_node.name, link_node['href'], link_node['class'], link_node.get_text()

print "获取P段落的文字"
p_node = soup.find('p', class_='story')
print p_node.name, p_node['class'], p_node.get_text()
